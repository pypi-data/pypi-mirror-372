import importlib
from hestia_earth.schema import SiteSiteType
from hestia_earth.utils.lookup import download_lookup, lookup_term_ids
from hestia_earth.utils.model import find_term_match
from hestia_earth.utils.tools import list_sum, non_empty_list, safe_parse_float, flatten

from hestia_earth.validation.utils import (
    group_blank_nodes, _filter_list_errors, _value_average, _node_year, get_lookup_value
)
from hestia_earth.validation.models import is_enabled as models_is_enabled, value_from_model
from .shared import need_validate_coordinates, value_difference, _parse_node_value


SOIL_TEXTURE_IDS = ['sandContent', 'siltContent', 'clayContent']
MEASUREMENTS_MODELS = {
    'precipitationAnnual': {'model': 'geospatialDatabase', 'runByYear': True},
    'precipitationLongTermAnnualMean': {'model': 'geospatialDatabase', 'runByYear': False},
    'temperatureAnnual': {'model': 'geospatialDatabase', 'runByYear': True},
    'temperatureLongTermAnnualMean': {'model': 'geospatialDatabase', 'runByYear': False}
}
WATER_SITE_TYPES = [
    SiteSiteType.POND.value,
    SiteSiteType.RIVER_OR_STREAM.value,
    SiteSiteType.LAKE.value,
    SiteSiteType.SEA_OR_OCEAN.value,
]


def _group_measurement_key(measurement: dict):
    keys = non_empty_list([
        str(measurement.get('depthUpper', '')),
        str(measurement.get('depthLower', '')),
        measurement.get('startDate'),
        measurement.get('endDate')
    ])
    return '-'.join(keys) if len(keys) > 0 else 'default'


def validate_soilTexture(measurements: list):
    lookup = download_lookup('soilTexture.csv')
    soil_texture_ids = lookup_term_ids(lookup)

    def validate_single(measurements: list, texture: dict, measurement_id: str):
        term = texture['node'].get('term', {})
        min = safe_parse_float(get_lookup_value(term, f"{measurement_id}Min"), default=0)
        max = safe_parse_float(get_lookup_value(term, f"{measurement_id}Max"), default=100)
        # set default value to min so if no value then passes validation
        measurement = next(
            (v for v in measurements if v['node'].get('term', {}).get('@id') == measurement_id), {})
        texture_value = _value_average(measurement.get('node'), min)
        return min <= texture_value <= max or {
            'level': 'error',
            'dataPath': f".measurements[{measurement['index']}].value",
            'message': 'is outside the allowed range',
            'params': {
                'term': measurement['node'].get('term', {}),
                'range': {'min': min, 'max': max}
            }
        }

    def validate(values: list):
        texture_ids = list(filter(lambda v: v['node'].get('term', {}).get('@id') in soil_texture_ids, values))
        return len(texture_ids) == 0 or flatten(map(
            lambda texture: list(map(lambda id: validate_single(values, texture, id), SOIL_TEXTURE_IDS)),
            texture_ids
        ))

    groupped_values = group_blank_nodes(enumerate(measurements), by_sum=False).values()
    return _filter_list_errors(flatten(map(validate, groupped_values)))


def validate_depths(measurements: list):
    def validate(values: tuple):
        index, measurement = values
        depthUpper = measurement.get('depthUpper')
        depthLower = measurement.get('depthLower')
        return any([depthUpper is None, depthLower is None]) or depthUpper <= depthLower or {
            'level': 'error',
            'dataPath': f".measurements[{index}].depthLower",
            'message': 'must be greater than or equal to depthUpper'
        }

    return _filter_list_errors(map(validate, enumerate(measurements)))


def validate_required_depths(site: dict, list_key: str):
    def validate(values: tuple):
        index, measurement = values
        term = measurement.get('term', {})
        depth_error = get_lookup_value(term, 'depthSensitive')
        depth_warning = get_lookup_value(term, 'recommendAddingDepth')
        has_depths = measurement.get('depthUpper') is not None and measurement.get('depthLower') is not None
        return has_depths or (
            {
                'level': 'error',
                'dataPath': f".{list_key}[{index}]",
                'message': 'must set both depthUpper and depthLower'
            } if depth_error else {
                'level': 'warning',
                'dataPath': f".{list_key}[{index}]",
                'message': 'should set both depthUpper and depthLower'
            } if depth_warning else True
        )

    return _filter_list_errors(map(validate, enumerate(site.get(list_key, []))))


def validate_term_unique(measurements: list):
    def count_same_term(term_id: str):
        return len(list(filter(lambda x: x.get('term', {}).get('@id') == term_id, measurements)))

    def validate(values: tuple):
        index, measurement = values
        term = measurement.get('term', {})
        term_id = term.get('@id')
        unique = get_lookup_value(term, 'oneMeasurementPerSite')
        unique = False if unique is None or unique == '-' else bool(unique)
        return not unique or count_same_term(term_id) == 1 or {
            'level': 'error',
            'dataPath': f".measurements[{index}].term.name",
            'message': 'must be unique'
        }

    return _filter_list_errors(map(validate, enumerate(measurements)))


def validate_require_startDate_endDate(site: dict, list_key: str):
    site_start_date = site.get('startDate')
    site_end_date = site.get('endDate')

    def validate(values: tuple):
        index, measurement = values
        term = measurement.get('term', {})
        start_date = measurement.get('startDate')
        end_date = measurement.get('endDate')
        required = get_lookup_value(term, 'needStartDateEndDate')
        return any([
            not required,
            start_date is not None and end_date is not None,
            site_start_date is not None and start_date == site_start_date,
            site_end_date is not None and end_date == site_end_date
        ]) or list(map(lambda k: {
            'level': 'error',
            'dataPath': f".{list_key}[{index}]",
            'message': f"should have required property '{k}'",
            'params': {
                'missingProperty': k
            }
        }, ['startDate', 'endDate']))

    return _filter_list_errors(flatten(map(validate, enumerate(site.get(list_key, [])))))


def _run_from_model(site: dict, blank_node: dict):
    term_id = blank_node.get('term', {}).get('@id')
    params = MEASUREMENTS_MODELS.get(term_id, {})
    year = _node_year(blank_node)
    should_run = all([
        need_validate_coordinates(site),
        not params.get('runByYear', False) or year is not None
    ])
    model_run = importlib.import_module(
        f"hestia_earth.models.{params.get('model')}.{term_id}"
    )._run if params.get('model') else None
    return (
        model_run(site, year) if params.get('runByYear', False) else model_run(site)
    ) if all([params.get('model'), should_run]) else None


def validate_with_models(site: dict, list_key: str):
    threshold = 0.25

    def validate(values: tuple):
        index, blank_node = values
        value = _parse_node_value(blank_node)
        expected_node = _run_from_model(site, blank_node) or {}
        expected_method_model = (
            (expected_node[0] or {}) if isinstance(expected_node, list) else expected_node
        ).get('methodModel', {})
        expected_value = value_from_model(expected_node) if expected_node else None
        delta = value_difference(value or 0, expected_value)
        data_path = '' if blank_node.get('value') is None else '.value'
        return delta < threshold or {
            'level': 'warning',
            'dataPath': f".{list_key}[{index}]{data_path}",
            'message': 'the measurement provided might be in error',
            'params': {
                'term': blank_node.get('term', {}),
                'model': expected_method_model,
                'current': value,
                'expected': expected_value,
                'delta': delta * 100,
                'threshold': threshold
            }
        }

    nodes = site.get(list_key, []) if models_is_enabled() else []
    return _filter_list_errors(flatten(map(validate, enumerate(nodes))))


def validate_value_length(site: dict, list_key: str):
    def validate(values: tuple):
        index, blank_node = values
        term = blank_node.get('term', {})
        array_type = get_lookup_value(term, 'arrayTreatment')
        value_length = len(blank_node.get('value', []))
        return array_type != 'arrayNotAllowed' or value_length <= 1 or {
            'level': 'error',
            'dataPath': f".measurements[{index}].value",
            'message': 'must not contain more than 1 value'
        }

    return _filter_list_errors(flatten(map(validate, enumerate(site.get(list_key, [])))))


def validate_water_measurements(site: dict, list_key: str):
    site_type_valid = site.get('siteType') in WATER_SITE_TYPES
    nodes = site.get(list_key, [])
    term_ids = ['salineWater', 'freshWater', 'brackishWater', 'waterSalinity']
    has_node = any([find_term_match(nodes, term_id) for term_id in term_ids])
    return not site_type_valid or has_node or {
        'level': 'error',
        'dataPath': f".{list_key}",
        'message': 'must specify water type for ponds',
        'params': {
            'ids': term_ids
        }
    }


_ALLOWED_SALINITY = {
    'brackishWater': lambda value: 18000 <= value >= 500,
    'freshWater': lambda value: value < 500,
    'salineWater': lambda value: value > 18000,
}


def validate_water_salinity(site: dict, list_key: str):
    site_type_valid = site.get('siteType') in WATER_SITE_TYPES
    nodes = site.get(list_key, [])
    waterSalinity = list_sum(find_term_match(nodes, 'waterSalinity', {}).get('value', []), None)
    valid_saline_ids = non_empty_list([
        term_id
        for term_id in _ALLOWED_SALINITY.keys()
        if _ALLOWED_SALINITY[term_id](waterSalinity)
    ]) if waterSalinity is not None else []
    invalid_saline_nodes = non_empty_list([
        find_term_match(nodes, term_id)
        for term_id in _ALLOWED_SALINITY.keys()
        if not _ALLOWED_SALINITY[term_id](waterSalinity)
    ]) if waterSalinity is not None else []
    return not site_type_valid or waterSalinity is None or not invalid_saline_nodes or {
        'level': 'error',
        'dataPath': f".{list_key}",
        'message': 'invalid water salinity',
        'params': {
            'current': invalid_saline_nodes[0].get('term', {}).get('@id'),
            'expected': valid_saline_ids[0]
        }
    }
