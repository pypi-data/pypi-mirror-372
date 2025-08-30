from functools import reduce
from hestia_earth.schema import TermTermType
from hestia_earth.utils.lookup import download_lookup, get_table_value, column_name, lookup_term_ids
from hestia_earth.utils.tools import flatten, non_empty_list

from hestia_earth.validation.utils import _filter_list_errors
from hestia_earth.validation.terms import TERMS_QUERY, get_terms

IGNORE_MODELS = [
    'aggregatedModels'  # used only for aggregations, should not be shown as possible values
]


def _indicator_group_key(indicator: dict, include_term: bool = True):
    return '-'.join(non_empty_list(flatten([
        indicator.get('term', {}).get('@id') if include_term else '',
        indicator.get('country', {}).get('@id'),
        indicator.get('landCover', {}).get('@id'),
        [i.get('@id') for i in indicator.get('inputs', [])],
    ])))


def _group_indicators(indicators: list, include_term: bool = True):
    def group_by(groups: dict, indicator: dict):
        group_key = _indicator_group_key(indicator, include_term)
        groups[group_key] = groups.get(group_key, []) + [indicator]
        return groups

    return reduce(group_by, indicators, {})


def _allowed_characterisedIndicator_model(lookup, models: list, term_id: str):
    return [
        m for m in models if m != 'termid' and
        get_table_value(lookup, 'termid', term_id, column_name(m)) and
        m not in IGNORE_MODELS
    ]


def _is_method_allowed(lookup, term_id: str, model: str):
    value = get_table_value(lookup, 'termid', term_id, column_name(model))
    # bug numpy bool not returning `True`
    return True if value else False


def validate_characterisedIndicator_model(node: dict, list_key: str):
    lookup = download_lookup('characterisedIndicator-model-mapping.csv', keep_in_memory=False)
    models = get_terms(TERMS_QUERY.MODEL)

    def validate(values: tuple):
        index, value = values
        term = value.get('term', {})
        term_id = term.get('@id')
        model = value.get('methodModel', {})
        model_id = model.get('@id')
        should_validate = term_id in lookup_term_ids(lookup) and model_id is not None
        return not should_validate or _is_method_allowed(lookup, term_id, model_id) or {
            'level': 'error',
            'dataPath': f".{list_key}[{index}].methodModel.@id",
            'message': 'is not allowed for this characterisedIndicator',
            'params': {
                'term': term,
                'model': model,
                'allowedValues': _allowed_characterisedIndicator_model(lookup, models, term_id)
            }
        }

    return _filter_list_errors(list(map(validate, enumerate(node.get(list_key, [])))))


def _below_occupation(index: int, value: float, blank_nodes: list, suffix: str):
    other_values = list(filter(lambda b: b.get('term', {}).get('@id').endswith(suffix), blank_nodes))
    other_values = [other_value.get('value', 0) for other_value in other_values]
    return len(other_values) == 0 or all([
        value <= (other_value * 1.05) for other_value in other_values
    ]) or {
        'level': 'error',
        'dataPath': f".emissionsResourceUse[{index}].value",
        'message': 'must be less than or equal to land occupation',
        'params': {
            'current': value,
            'max': min(other_values)
        }
    }


def validate_landTransformation(node: dict, list_key='emissionsResourceUse'):
    blank_nodes = node.get(list_key, [])
    grouped_land_occupation = _group_indicators([
        v for v in blank_nodes if v.get('term', {}).get('@id', '').startswith('landOccupation')
    ], include_term=False)

    def validate(values: tuple):
        index, blank_node = values
        term_id = blank_node.get('term', {}).get('@id')
        value = blank_node.get('value', 0)
        group_key = _indicator_group_key(blank_node, include_term=False)
        land_occupation_blank_nodes = grouped_land_occupation.get(group_key) or []
        return not term_id.startswith('landTransformation') or [
            not term_id.endswith('DuringCycle') or
            _below_occupation(index, value, land_occupation_blank_nodes, 'DuringCycle'),
            not term_id.endswith('InputsProduction') or
            _below_occupation(index, value, land_occupation_blank_nodes, 'InputsProduction')
        ]

    return _filter_list_errors(flatten(map(validate, enumerate(blank_nodes))))


def validate_inonising_compounds_waste(node: dict, list_key='emissionsResourceUse'):
    blank_nodes = node.get(list_key, [])
    allowed_term_types = [None, TermTermType.WASTE.value]

    def validate(values: tuple):
        index, blank_node = values
        term_id = blank_node.get('term', {}).get('@id')
        key_term_type = blank_node.get('key', {}).get('termType')
        return not term_id.startswith('ionisingCompounds') or key_term_type in allowed_term_types or {
            'level': 'error',
            'dataPath': f".{list_key}[{index}].key.termType",
            'message': 'should be equal to one of the allowed values',
            'params': {
                'allowedValues': non_empty_list(allowed_term_types)
            }
        }

    return _filter_list_errors(flatten(map(validate, enumerate(blank_nodes))))
