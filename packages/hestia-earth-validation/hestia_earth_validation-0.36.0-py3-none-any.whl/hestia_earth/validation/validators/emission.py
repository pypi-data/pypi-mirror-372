from hestia_earth.schema import EmissionMethodTier
from hestia_earth.utils.tools import flatten
from hestia_earth.utils.model import find_term_match

from hestia_earth.validation.utils import _filter_list_errors


def validate_linked_terms(cycle: dict, list_key: str, linked_key: str, linked_list_key: str, soft_check=False):
    linked_nodes = cycle.get(linked_list_key, [])

    def validate(values: tuple):
        index, emission = values
        linked_items = emission.get(linked_key, [])
        return len(linked_items) == 0 or any([
            find_term_match(linked_nodes, item.get('@id')) for item in (
                [linked_items] if isinstance(linked_items, dict) else linked_items
            )
        ]) or {
            'level': 'warning' if soft_check else 'error',
            'dataPath': f".{list_key}[{index}]",
            'message': f"{'should' if soft_check else 'must'} add the linked {linked_list_key} to the cycle",
            'params': {
                'term': emission.get('term', {}),
                'expected': linked_items
            }
        }

    return _filter_list_errors(flatten(map(validate, enumerate(cycle.get(list_key, [])))))


_NOT_RELEVANT_ID = 'emissionNotRelevant'


def validate_method_not_relevant(cycle: dict, list_key: str):
    def validate(values: tuple):
        index, emission = values
        term_id = emission.get('methodModel', {}).get('@id')
        return term_id != _NOT_RELEVANT_ID or {
            'level': 'warning',
            'dataPath': f".{list_key}[{index}].methodModel.@id",
            'message': 'should not use not relevant model',
            'params': {
                'term': emission.get('term', {}),
                'model': emission.get('methodModel', {})
            }
        }

    return _filter_list_errors(flatten(map(validate, enumerate(cycle.get(list_key, [])))))


def validate_methodTier_not_relevant(cycle: dict, list_key: str):
    def validate(values: tuple):
        index, emission = values
        methodTier = emission.get('methodTier')
        return methodTier != EmissionMethodTier.NOT_RELEVANT.value or {
            'level': 'warning',
            'dataPath': f".{list_key}[{index}].methodTier",
            'message': 'should not use not relevant methodTier',
            'params': {
                'term': emission.get('term', {})
            }
        }

    return _filter_list_errors(flatten(map(validate, enumerate(cycle.get(list_key, [])))))
