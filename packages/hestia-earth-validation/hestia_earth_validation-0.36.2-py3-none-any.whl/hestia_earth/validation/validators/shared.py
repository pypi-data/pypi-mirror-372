import os
from concurrent.futures import ThreadPoolExecutor
from decimal import Decimal
from functools import reduce
from typing import List
import re
from hestia_earth.schema import TermTermType, SiteSiteType
from hestia_earth.utils.api import download_hestia
from hestia_earth.utils.model import filter_list_term_type
from hestia_earth.utils.tools import flatten, list_sum, safe_parse_float, safe_parse_date, get_dict_key

from hestia_earth.validation.gee import (
    MAX_AREA_SIZE, is_enabled as gee_is_enabled, id_to_level, get_region_id, get_region_distance
)
from hestia_earth.validation.models import (
    is_enabled as models_is_enabled, value_from_model, method_tier_from_model, run_model, run_model_from_node
)
from hestia_earth.validation.utils import (
    update_error_path, _filter_list_errors, _next_error, _value_average, is_number, match_value_type,
    find_linked_node, _is_before_today,
    _list_except_item, _dict_without_key, hash_dict,
    group_blank_nodes, term_valueType,
    get_lookup_value
)

_VALIDATE_PRIVATE_SOURCE = os.getenv('VALIDATE_PRIVATE_SOURCE', 'true') == 'true'
CROP_SITE_TYPE = [
    SiteSiteType.CROPLAND.value,
    SiteSiteType.GLASS_OR_HIGH_ACCESSIBLE_COVER.value
]
OTHER_MODEL_ID = 'otherModel'


def validate_properties_same_length(node: dict, list_key: str, prop_key: str, prop_keys: list):
    def validate(values: tuple):
        index, blank_node = values
        value_len = len(blank_node.get(prop_key, ''))
        invalid_prop_key = next((
            key for key in prop_keys if blank_node.get(key) and len(blank_node.get(key)) != value_len), None)
        return value_len == 0 or invalid_prop_key is None or {
            'level': 'error',
            'dataPath': f".{list_key}[{index}].{invalid_prop_key}",
            'message': f"must have the same length as {prop_key}"
        }

    return _filter_list_errors(flatten(map(validate, enumerate(node.get(list_key, [])))))


def validate_date_lt_today(node: dict, key: str):
    date = get_dict_key(node, key)
    return date is None or _is_before_today(date) or {
        'level': 'error',
        'dataPath': f".{key}",
        'message': 'must be before today'
    }


def validate_list_date_lt_today(node: dict, list_key: str, node_keys: list):
    def validate(values: tuple):
        index, value = values
        errors = list(map(lambda key: {'key': key, 'error': validate_date_lt_today(value, key)}, node_keys))
        return _filter_list_errors(
            [update_error_path(error['error'], list_key, index) for error in errors if error['error'] is not True]
        )

    return _filter_list_errors(flatten(map(validate, enumerate(node.get(list_key, [])))))


def is_date_after(min_date: str, date: str, strict: bool = True):
    return min_date is None or date is None or (
        len(min_date) <= 7 and len(date) <= 7 and date >= min_date
    ) or (
        date > min_date if strict else date >= min_date
    )


def is_date_equal(date1: str, date2: str, validate_year_only: bool = False):
    date1 = safe_parse_date(date1)
    date2 = safe_parse_date(date2)
    return (
        date1.year == date2.year if validate_year_only else date1 == date2
    ) if all([date1, date2]) else False


def validate_list_dates_after(node: dict, node_key: str, list_key: str, list_key_fields: list):
    min_date = node.get(node_key)

    def validate_field_list(blank_node: dict, index: int, field: str, field_index: int):
        date = blank_node.get(field)[field_index]
        return is_date_after(min_date, date, False) or {
            'level': 'warning',
            'dataPath': f".{list_key}[{index}].{field}[{field_index}]",
            'message': f"must be greater than {node.get('type', node.get('@type'))} {node_key}"
        }

    def validate_field(blank_node: dict, index: int, field: str):
        date = blank_node.get(field)
        return [
            validate_field_list(blank_node, index, field, field_index) for field_index in range(0, len(date))
        ] if isinstance(date, list) else (
            is_date_after(min_date, date, False) or {
                'level': 'warning',
                'dataPath': f".{list_key}[{index}].{field}",
                'message': f"must be greater than {node.get('type', node.get('@type'))} {node_key}"
            }
        )

    def validate(values: tuple):
        index, blank_node = values
        return _filter_list_errors(flatten([validate_field(blank_node, index, field) for field in list_key_fields]))

    return _filter_list_errors(map(validate, enumerate(node.get(list_key, []))))


def validate_dates(node: dict): return is_date_after(node.get('startDate'), node.get('endDate'))


def validate_list_dates(node: dict, list_key: str):
    def validate(values: tuple):
        index, value = values
        return validate_dates(value) or {
            'level': 'error',
            'dataPath': f".{list_key}[{index}].endDate",
            'message': 'must be greater than startDate'
        }

    return _filter_list_errors(map(validate, enumerate(node.get(list_key, []))))


def validate_list_dates_format(node: dict, list_key: str):
    return validate_properties_same_length(node, list_key, 'endDate', ['startDate'])


def validate_list_dates_length(node: dict, list_key: str):
    def validate(values: tuple):
        index, blank_node = values
        value = blank_node.get('value')
        dates = blank_node.get('dates')
        return value is None or dates is None or len(dates) == len(value) or {
            'level': 'error',
            'dataPath': f".{list_key}[{index}].dates",
            'message': 'must contain as many items as values',
            'params': {
                'expected': len(value),
                'current': len(dates)
            }
        }

    return _filter_list_errors(map(validate, enumerate(node.get(list_key, []))))


def is_value_below(value1, value2):
    compare_lists = isinstance(value1, list) and isinstance(value2, list)
    return any([value1 is None, value2 is None]) or (
        _is_list_value_below(value1, value2) if compare_lists else any([
            # allow 1% of rounding error
            value1 <= value2 * 1.01,
            Decimal(str(value1)) <= Decimal(str(value2))
        ])
    )


def _is_list_value_below(list1: list, list2: list):
    def compare_enum(index: int): return is_value_below(list1[index], list2[index])

    return len(list1) != len(list2) or \
        next((x for x in list(map(compare_enum, range(len(list1)))) if x is not True), True) is True


def validate_list_value_between_min_max(node: dict, list_key: str):
    def validate(values: tuple):
        index, blank_node = values
        min = blank_node.get('min')
        max = blank_node.get('max')
        value = blank_node.get('value')

        return all([is_value_below(value, max), is_value_below(min, value)]) or {
            'level': 'error',
            'dataPath': f".{list_key}[{index}].value",
            'message': 'must be between min and max',
            'params': {
                'min': min,
                'max': max
            }
        }

    return _next_error(list(map(validate, enumerate(node.get(list_key, [])))))


def validate_list_min_below_max(node: dict, list_key: str):
    def validate(values: tuple):
        index, blank_node = values
        min = blank_node.get('min')
        max = blank_node.get('max')
        return is_value_below(min, max) or {
            'level': 'error',
            'dataPath': f".{list_key}[{index}].max",
            'message': 'must be greater than min'
        }

    return _next_error(list(map(validate, enumerate(node.get(list_key, [])))))


def _value_range_error(value: int, minimum: int, maximum: int):
    return 'minimum' if minimum is not None and not is_value_below(minimum, value) else (
        'maximum' if maximum is not None and not is_value_below(value, maximum) else False
    )


def validate_list_min_max_lookup(node: dict, list_key: list, list_key_field='value'):
    def validate(values: tuple):
        index, blank_node = values
        term = blank_node.get('term', {})
        mininum = safe_parse_float(get_lookup_value(term, 'minimum'), None)
        maximum = safe_parse_float(get_lookup_value(term, 'maximum'), None)
        value = _value_average(blank_node, None, list_key_field)
        error = _value_range_error(value, mininum, maximum) if value is not None else False
        return error is False or ({
            'level': 'error',
            'dataPath': f".{list_key}[{index}].{list_key_field}",
            'message': f"should be above {mininum}"
        } if error == 'minimum' else {
            'level': 'error',
            'dataPath': f".{list_key}[{index}].{list_key_field}",
            'message': f"should be below {maximum}"
        })

    return _filter_list_errors(map(validate, enumerate(node.get(list_key, []))))


def validate_nodes_duplicates(node: dict, node_by_hash: dict):
    node_without_id = _dict_without_key(node, 'id')
    key = hash_dict(node_without_id)
    duplicates = _list_except_item(node_by_hash.get(key, []), node)
    return [next(
        ({
            'level': 'warning',
            'dataPath': '',
            'message': f"might be a duplicate of the {dup.get('type')} with id {dup.get('id')}"
        } for dup in duplicates),
        True
    )] if len(duplicates) > 0 else []


def validate_list_duplicate_values(node: dict, list_key: str, prop: str, value: str):
    values = node.get(list_key, [])
    duplicates = list(filter(lambda v: get_dict_key(v, prop) == value, values))
    return len(duplicates) < 2 or {
        'level': 'error',
        'dataPath': f".{list_key}[{values.index(duplicates[1])}].{prop}",
        'message': f"must have only one entry with the same {prop} = {value}"
    }


def validate_list_term_percent(node: dict, list_key: str):
    def soft_validate(index: int, value): return (is_number(value) and 0 < value and value <= 1) and {
        'level': 'warning',
        'dataPath': f".{list_key}[{index}].value",
        'message': 'may be between 0 and 100'
    }

    def hard_validate(index: int, value): return (is_number(value) and 0 <= value and value <= 100) or {
        'level': 'error',
        'dataPath': f".{list_key}[{index}].value",
        'message': 'should be between 0 and 100 (percentage)'
    }

    def validate(values: tuple):
        index, blank_node = values
        units = blank_node.get('term', {}).get('units', '')
        value = _value_average(blank_node, blank_node.get('value')) if units == '%' else None
        is_empty = value is None or (isinstance(value, list) and len(value) == 0)
        return is_empty or soft_validate(index, value) or hard_validate(index, value)

    return _filter_list_errors(map(validate, enumerate(node.get(list_key, []))))


def valid_list_sum(blank_nodes: list):
    values = [_value_average(p, default=None) for p in blank_nodes]
    values_number = list(filter(is_number, values))
    is_valid = len(values) == len(values_number)
    return list_sum(values_number), is_valid


def validate_list_sum_100_percent(node: dict, list_key: str):
    def validate(values: list):
        term_ids = [v['node'].get('term', {}).get('@id') for v in values]
        total_value, valid_sum = valid_list_sum([v['node'] for v in values])
        blank_node = values[0]
        min_value = 99.5
        max_value = 100.5
        sum_equal_100 = blank_node.get('sumIs100Group')
        valid = all([
            total_value <= max_value,
            not sum_equal_100 or total_value >= min_value
        ])
        return valid or [
            {
                'level': 'error',
                'dataPath': f".{list_key}[{value.get('index')}]",
                'message': f"value should sum to {'' if sum_equal_100 else 'maximum '}100 across all values",
                'params': {
                    'termIds': term_ids,
                    'sum': total_value,
                    'max': max_value
                } | ({'min': min_value} if sum_equal_100 else {})
            } for value in values
        ]

    groupped_values = group_blank_nodes(enumerate(node.get(list_key, []))).values()
    return _filter_list_errors(flatten(map(validate, groupped_values)))


def validate_list_percent_requires_value(node: dict, list_key: str, term_types: List[TermTermType] = []):
    term_types_str = [t.value for t in term_types]

    def validate(values: tuple):
        index, blank_node = values
        term = blank_node.get('term', {})
        validate_value = all([
            term.get('termType') in term_types_str,
            term.get('units', '').startswith('%')
        ])
        value = blank_node.get('value', [])
        return not validate_value or len(value) > 0 or {
            'level': 'error',
            'dataPath': f".{list_key}[{index}]",
            'message': "should have required property 'value'",
            'params': {
                'term': term,
                'missingProperty': 'value'
            }
        }

    return _filter_list_errors(map(validate, enumerate(node.get(list_key, []))))


def validate_list_valueType(node: dict, list_key: str):
    def validate(values: tuple):
        index, blank_node = values
        term = blank_node.get('term', {})
        expected_value_type = term_valueType(term)
        value = blank_node.get('value')
        return value is None or match_value_type(expected_value_type, value) or {
            'level': 'error',
            'dataPath': f".{list_key}[{index}].value",
            'message': f"must be a {expected_value_type}"
        }

    return _filter_list_errors(map(validate, enumerate(node.get(list_key, []))))


def validate_is_region(node: dict, region_key='region'):
    region_id = node.get(region_key, {}).get('@id', '')
    level = id_to_level(region_id)
    return region_id == '' or level > 0 or {
        'level': 'error',
        'dataPath': f".{region_key}",
        'message': 'must not be a country'
    }


def validate_region_in_country(node: dict, region_key='region'):
    country = node.get('country', {})
    region_id = node.get(region_key, {}).get('@id', '')
    return region_id == '' or region_id[0:8] == country.get('@id') or {
        'level': 'error',
        'dataPath': f".{region_key}",
        'message': 'must be within the country',
        'params': {
            'country': country.get('name')
        }
    }


def validate_country(node: dict):
    country_id = node.get('country', {}).get('@id', '')
    # handle additional regions used as country, like region-world
    is_region = country_id.startswith('region-')
    return country_id == '' or is_region or bool(re.search(r'GADM-[A-Z]{3}$', country_id)) or {
        'level': 'error',
        'dataPath': '.country',
        'message': 'must be a country'
    }


def validate_country_region(node: dict):
    return _filter_list_errors([
        validate_country(node),
        validate_is_region(node),
        validate_region_in_country(node)
    ])


def validate_list_country_region(node: dict, list_key: str):
    def validate(values: tuple):
        index, blank_node = values
        errors = [
            validate_country(blank_node),
            validate_is_region(blank_node),
            validate_region_in_country(blank_node)
        ]
        errors = [update_error_path(error, list_key, index) for error in errors if error is not True]
        return _filter_list_errors(errors)

    return _filter_list_errors(map(validate, enumerate(node.get(list_key, []))))


def need_validate_coordinates(node: dict): return gee_is_enabled() and 'latitude' in node and 'longitude' in node


def validate_coordinates(node: dict):
    latitude = node.get('latitude')
    longitude = node.get('longitude')
    country = node.get('country', {})
    region = node.get('region')
    gadm_id = region.get('@id') if region else country.get('@id')
    id = get_region_id(node)
    return gadm_id == id or {
        'level': 'error',
        'dataPath': '.region' if region else '.country',
        'message': 'does not contain latitude and longitude',
        'params': {
            'current': gadm_id,
            'expected': id,
            'distance': get_region_distance(gadm_id, latitude=latitude, longitude=longitude)
        }
    }


def need_validate_area(node: dict):
    return all(['area' in node, 'boundary' in node, 'boundaryArea' in node])


def validate_area(node: dict):
    threshold = 0.05
    value = round(node.get('area', 0), 1)
    expected_value = round(node.get('boundaryArea', 0), 1)
    delta = value_difference(value, expected_value)
    return delta < threshold or {
        'level': 'warning',
        'dataPath': '.area',
        'message': 'should be equal to boundary',
        'params': {
            'current': value,
            'expected': expected_value,
            'delta': delta * 100,
            'threshold': threshold
        }
    }


def validate_boundary_area(node: dict):
    area = node.get('boundaryArea', 0) / 100
    return area < MAX_AREA_SIZE or {
        'level': 'warning',
        'dataPath': '.boundaryArea',
        'message': 'should be lower than max size',
        'params': {
            'current': area,
            'expected': MAX_AREA_SIZE
        }
    }


def need_validate_region_size(node: dict):
    return all([
        gee_is_enabled(),
        not need_validate_coordinates(node),
        'boundaryArea' not in node,
        'region' in node or 'country' in node
    ])


def validate_region_size(node: dict):
    region_id = node.get('region', node.get('country', {})).get('@id')
    region = download_hestia(region_id) if region_id else {}
    try:
        from hestia_earth.earth_engine.gadm import get_size_km2
        # get_region_size might throw error is geometry has too many edges
        area = region.get('area', get_size_km2(region_id) if region_id else None) or 0
    except Exception:
        area = 0
    return area < MAX_AREA_SIZE or {
        'level': 'warning',
        'dataPath': f".{'region' if node.get('region') else 'country'}",
        'message': 'should be lower than max size',
        'params': {
            'current': area,
            'expected': MAX_AREA_SIZE
        }
    }


N_A_VALUES = [
    '#n/a',
    '#na',
    'n/a',
    'na',
    'n.a',
    'nodata',
    'no data'
]


def validate_empty_fields(node: dict):
    keys = list(filter(lambda key: isinstance(node.get(key), str), node.keys()))

    def validate(key: str):
        return not node.get(key).lower() in N_A_VALUES or {
            'level': 'warning',
            'dataPath': f".{key}",
            'message': 'may not be empty'
        }

    return _filter_list_errors(map(validate, keys), False)


def validate_linked_source_privacy(node: dict, key: str, node_map: dict = {}):
    related_source = find_linked_node(node_map, node.get(key, {}))
    node_privacy = node.get('dataPrivate')
    related_source_privacy = related_source.get('dataPrivate') if related_source else None
    return related_source_privacy is None or node_privacy == related_source_privacy or {
        'level': 'error',
        'dataPath': '.dataPrivate',
        'message': 'should have the same privacy as the related source',
        'params': {
            'dataPrivate': node_privacy,
            key: {
                'dataPrivate': related_source_privacy
            }
        }
    }


def validate_private_has_source(node: dict, key: str):
    node_private = node.get('dataPrivate')
    return any([
        not _VALIDATE_PRIVATE_SOURCE,
        not node_private,
        node.get(key) is not None
    ]) or {
        'level': 'warning',
        'dataPath': '.dataPrivate',
        'message': 'should add a source',
        'params': {
            'current': key
        }
    }


def value_difference(value: float, expected_value: float):
    """
    Get the difference in percentage between a value and the expected value.

    Parameters
    ----------
    value : float
        The value to check.
    expected_value : float
        The expected value.

    Returns
    -------
    bool
        The difference in percentage between the value and the expected value.
    """
    return 0 if any([
        isinstance(expected_value, list),
        expected_value == 0,
        expected_value is None,
        isinstance(value, list),
        value is None
    ]) else round(abs(value - expected_value) / expected_value, 4)


def is_value_different(value: float, expected_value: float, delta: float = 0.05) -> bool:
    """
    Check the difference in percentage between a value and the expected value.

    Parameters
    ----------
    value : float
        The value to check.
    expected_value : float
        The value it should be close to.
    delta : float
        The accepted difference between the value and the expected one. Defaults to `5%`.

    Returns
    -------
    bool
        `True` if the value is within the percentage of the expected value, `False` otherwise.
    """
    return value_difference(value, expected_value) > delta


def _parse_node_value(node: dict):
    def parse_list_value(value: list):
        return list_sum(value) if len(value) > 0 else None

    value = node.get('value')
    return None if value is None else (
        parse_list_value(value) if isinstance(value, list) else value
    )


def _get_term_recalculated_max_delta(term: dict):
    col_name = 'valueToleranceToHestiaRecalculatedValue'
    return safe_parse_float(get_lookup_value(term, col_name), default=5) / 100


def _validate_list_model(node: dict, list_key: str):
    def validate(values: tuple):
        index, blank_node = values
        term = blank_node.get('term', {})
        max_delta = _get_term_recalculated_max_delta(term)
        try:
            method_tier = blank_node.get('methodTier')
            value = _parse_node_value(blank_node)
            # skip validation if `value` is not set
            result = run_model_from_node(blank_node, node) if value is not None else None
            expected_value = value_from_model(result) if result else 0
            expected_method_tier = method_tier_from_model(result)
            delta = value_difference(value, expected_value)
            return method_tier != expected_method_tier or delta < max_delta or {
                'level': 'error',
                'dataPath': f".{list_key}[{index}].value",
                'message': 'the value provided is not consistent with the model result',
                'params': {
                    'model': blank_node.get('methodModel', {}),
                    'term': term,
                    'current': value,
                    'expected': expected_value,
                    'delta': delta * 100,
                    'threshold': max_delta
                }
            }
        except Exception:
            return True
    return validate


def validate_list_model(node: dict, list_key: str) -> list:
    """
    Validates a list using the engine models.
    This method will go through every element of the list and run the model that matches the
    `methodModel` and `term.@id` on the element.
    Note: if the `methodTier` returned is different than the reported one, the result will be ignored.

    Parameters
    ----------
    node : dict
        The node containing the list to run.
    list_key : str
        The property of the node containing the list to run.

    Returns
    -------
    list
        List of errors from the models or `True` if no errors.
    """
    nodes = node.get(list_key, []) if models_is_enabled() else []
    with ThreadPoolExecutor() as executor:
        errors = list(executor.map(_validate_list_model(node, list_key), enumerate(nodes)))
    return _filter_list_errors(errors)


def _reset_completeness(node: dict):
    completeness = node.get('completeness', {})
    completeness = reduce(lambda prev, curr: {**prev, curr: False}, completeness.keys(), completeness)
    return {**node, 'completeness': completeness}


def _get_model_from_result(result: dict):
    return result.get('methodModel', result.get('model')) if result else None


def _validate_list_model_config(node: dict, list_key: str, conf: dict):
    def validate_model(term: dict, value: float, index: int, model_conf: dict):
        node_run = _reset_completeness(node) if model_conf.get('resetDataCompleteness', False) else node
        expected_result = run_model(model_conf['model'], term.get('@id'), node_run)
        expected_value = value_from_model(expected_result)
        delta = value_difference(value, expected_value)
        return delta < model_conf['delta'] or {
            'level': model_conf.get('level', 'error'),
            'dataPath': f".{list_key}[{index}].value",
            'message': 'the value provided is not consistent with the model result',
            'params': {
                'model': _get_model_from_result(expected_result[0]),
                'term': term,
                'current': value,
                'expected': expected_value,
                'delta': delta * 100,
                'threshold': model_conf['delta']
            }
        }

    def validate(values: tuple):
        index, blank_node = values
        value = _parse_node_value(blank_node)
        term = blank_node.get('term', {})
        term_id = blank_node.get('term', {}).get('@id')
        # get the configuration for this element
        # if it does not exist or no `value` is set, skip model
        term_conf = conf.get(term_id)
        return validate_model(term, value, index, term_conf) if term_conf and value is not None else True

    return validate


def validate_list_model_config(node: dict, list_key: str, conf: dict):
    """
    Validates a list using the engine models.
    This method uses a configuration to determine which `term` in the elements should run.
    It does not use the `methodModel` that could be found on each element.

    Parameters
    ----------
    node : dict
        The node containing the list to run.
    list_key : str
        The property of the node containing the list to run.
    conf : dict
        The configuration to decide which models to run.

    Returns
    -------
    list
        List of errors from the models or `True` if no errors.
    """
    nodes = node.get(list_key, []) if models_is_enabled() else []
    with ThreadPoolExecutor() as executor:
        errors = list(executor.map(_validate_list_model_config(node, list_key,  conf), enumerate(nodes)))
    return _filter_list_errors(errors)


def _unique_term_grouping(term_id: str):
    # TODO: use a lookup instead
    return re.split(
        r'(Kg|Liveweight|ColdCarcassWeight|ColdDressedCarcassWeight|ReadyToCookWeight)', term_id
    )[0] if term_id else None


def validate_duplicated_term_units(node: dict, list_key: str, term_types: List[TermTermType]):
    def term_ids_mapper(prev: dict, curr: dict):
        term = curr.get('term', {})
        term_id = term.get('@id')
        term_id_suffix = _unique_term_grouping(term_id)
        prev[term_id_suffix] = prev.get(term_id_suffix, []) + [term.get('units')]
        return prev

    blank_nodes = node.get(list_key, [])
    term_ids_to_units = reduce(term_ids_mapper, filter_list_term_type(blank_nodes, term_types), {})

    def validate(values: tuple):
        index, blank_node = values
        term = blank_node.get('term', {})
        term_id = term.get('@id')
        term_id_suffix = _unique_term_grouping(term_id)
        units = term_ids_to_units.get(term_id_suffix, [])
        return len(units) <= 1 or {
            'level': 'warning',
            'dataPath': f".{list_key}[{index}].term",
            'message': 'should not use identical terms with different units',
            'params': {
                'term': term,
                'units': units
            }
        }

    return _filter_list_errors(map(validate, enumerate(blank_nodes)))


def validate_other_model(node: dict, list_key: str):
    def validate(values: tuple):
        index, blank_node = values
        term = blank_node.get('methodModel', {})
        term_id = term.get('@id')
        return term_id != OTHER_MODEL_ID or bool(blank_node.get('methodModelDescription')) or {
            'level': 'error',
            'dataPath': f".{list_key}[{index}].methodModel",
            'message': 'is required when using other model'
        }

    return _filter_list_errors(map(validate, enumerate(node.get(list_key, []))))


def validate_nested_existing_node(node: dict, key: str):
    # detect when a non-indexed node references indexed nodes
    is_indexed = '@id' in node
    nested_value = node.get(key)
    return is_indexed or (
        _filter_list_errors([
            '@id' not in value or {
                'level': 'warning',
                'dataPath': f".{key}[{index}].@id",
                'message': 'should not link to an existing node',
                'params': {
                    'node': value
                }
            }
            for index, value in enumerate(nested_value)
        ]) if isinstance(nested_value, list) else (
            '@id' not in (nested_value or {}) or {
                'level': 'warning',
                'dataPath': f".{key}.@id",
                'message': 'should not link to an existing node',
                'params': {
                    'node': nested_value
                }
            }
        )
    )
