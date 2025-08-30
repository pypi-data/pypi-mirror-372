from hestia_earth.schema import TermTermType
from hestia_earth.utils.api import download_hestia
from hestia_earth.utils.model import find_term_match, filter_list_term_type
from hestia_earth.utils.tools import flatten, list_sum

from hestia_earth.validation.utils import _filter_list_errors, update_error_path, term_id_prefix
from hestia_earth.validation.validators.shared import is_value_different
from .practice import validate_excretaManagement


def _previous_transformation(cycle: dict, list_key: str, transformation: dict, index: int):
    tr_id = transformation.get('previousTransformationId')
    transformations = cycle.get(list_key, [])
    # previous transformation must be before the current transformation index
    return next(
        (transformations[i] for i in reversed(range(0, min(index, len(transformations))))
         if transformations[i].get('transformationId') == tr_id and i < index),
        None
    )


def _validate_previous_term(cycle: dict, list_key: str, transformation: dict, index: int):
    previous_transformation = _previous_transformation(cycle, list_key, transformation, index)
    tr_id = transformation.get('previousTransformationId')
    return not tr_id or previous_transformation is not None or {
        'level': 'error',
        'dataPath': f".{list_key}[{index}].previousTransformationId",
        'message': 'must point to a previous transformation in the list'
    }


def _cycle_has_product(cycle: dict, input: dict):
    term_id = input.get('term', {}).get('@id')
    return find_term_match(cycle.get('products', []), term_id, None) is not None


def _validate_previous_input(cycle: dict, list_key: str, transformation: dict, index: int):
    has_previous_transformation = transformation.get('previousTransformationId') is not None
    inputs = transformation.get('inputs', [])

    def validate_in_cycle():
        return any([
            len(cycle.get('products', [])) == 0,
            len(inputs) == 0
        ]) or any([_cycle_has_product(cycle, i) for i in inputs]) or {
            'level': 'error',
            'dataPath': f".{list_key}[{index}]",
            'message': 'at least one Input must be a Product of the Cycle'
        }

    def validate_in_previous_transformation():
        previous_transformation = _previous_transformation(cycle, list_key, transformation, index)
        return not previous_transformation or any([
            len(previous_transformation.get('products', [])) == 0,
            len(inputs) == 0
        ]) or any([_cycle_has_product(previous_transformation, i) for i in inputs]) or {
            'level': 'error',
            'dataPath': f".{list_key}[{index}]",
            'message': 'at least one Input must be a Product of the previous Transformation'
        }

    return validate_in_previous_transformation() if has_previous_transformation else validate_in_cycle()


def _validate_previous_product_value(cycle: dict, list_key: str, transformation: dict, index: int):
    share = transformation.get('transformedShare')
    inputs = transformation.get('inputs', [])
    previous_transformation = _previous_transformation(cycle, list_key, transformation, index)
    products = (previous_transformation or cycle).get('products', [])

    def validate_input(input_index: int):
        input = list_sum(inputs[input_index].get('value', []), None)
        term_id = inputs[input_index].get('term', {}).get('@id')
        product = list_sum(find_term_match(products, term_id).get('value', []), None)
        return any([not input, not product]) or not is_value_different(input, product * share / 100, 0.01) or {
            'level': 'error',
            'dataPath': f".transformations[{index}].inputs[{input_index}].value",
            'message': 'must be equal to previous product multiplied by the share'
        }

    return any([
        len(products) == 0,
        share is None
    ]) or _filter_list_errors(flatten(map(validate_input, range(len(inputs)))))


def validate_previous_transformation(cycle: dict, list_key: str = 'transformations'):
    def validate(values: tuple):
        index, transformation = values
        return _filter_list_errors(map(lambda func: func(cycle, list_key, transformation, index), [
            _validate_previous_term,
            _validate_previous_input,
            _validate_previous_product_value
        ]))

    return _filter_list_errors(map(validate, enumerate(cycle.get(list_key, []))))


def validate_transformation_excretaManagement(cycle: dict, list_key: str = 'transformations'):
    def validate(values: tuple):
        index, transformation = values
        practices = transformation.get('practices', []) + [{'term': transformation.get('term')}]
        error = validate_excretaManagement(transformation, practices)
        return error is True or update_error_path(error, list_key, index)

    return _filter_list_errors(map(validate, enumerate(cycle.get(list_key, []))))


def validate_linked_emission(cycle: dict, list_key: str = 'transformations'):
    emissions = cycle.get('emissions', [])

    def validate_emission(transformation_index: int, transformation: dict):
        def validate(values: tuple):
            index, emission = values
            term_id = emission.get('term', {}).get('@id')
            same_emissions = list(filter(lambda e: e.get('term', {}).get('@id') == term_id, emissions))
            linked_emission = next((e for e in same_emissions if all([
                e.get('transformation', {}).get('@id') == transformation.get('term', {}).get('@id')
            ])), None)
            return len(same_emissions) == 0 or linked_emission is not None or {
                'level': 'warning',
                'dataPath': f".{list_key}[{transformation_index}].emissions[{index}]",
                'message': 'should be linked to an emission in the Cycle',
                'params': {
                    'term': emission.get('term', {})
                }
            }

        return validate

    def validate(values: tuple):
        index, transformation = values
        return _filter_list_errors(
            map(validate_emission(index, transformation), enumerate(transformation.get('emissions', [])))
        )

    return len(emissions) == 0 or _filter_list_errors(flatten(map(validate, enumerate(cycle.get(list_key, [])))))


def _is_generic_excreta(term_id: str): return len((download_hestia(term_id) or {}).get('subClassOf', [])) == 0


def validate_excreta_inputs_products(transformations: list):
    def validate_product(transformation_index: int, input_prefix_ids: list):
        def validate(values: tuple):
            index, product = values
            term = product.get('term', {})
            term_id = term.get('@id', '')
            is_excreta = term.get('termType', '') == TermTermType.EXCRETA.value
            return not is_excreta or _is_generic_excreta(term_id) or term_id_prefix(term_id) in input_prefix_ids or {
                'level': 'error',
                'dataPath': f".transformations[{transformation_index}].products[{index}]",
                'message': 'must be included as an Input',
                'params': {
                    'term': term,
                    'expected': input_prefix_ids
                }
            }
        return validate

    def validate(values: tuple):
        index, transformation = values
        excreta_inputs = filter_list_term_type(transformation.get('inputs', []), TermTermType.EXCRETA)
        input_prefix_ids = list(set([term_id_prefix(v.get('term', {}).get('@id')) for v in excreta_inputs]))
        return len(input_prefix_ids) == 0 or _filter_list_errors(
            map(validate_product(index, input_prefix_ids), enumerate(transformation.get('products', [])))
        )

    return _filter_list_errors(flatten(map(validate, enumerate(transformations))))
