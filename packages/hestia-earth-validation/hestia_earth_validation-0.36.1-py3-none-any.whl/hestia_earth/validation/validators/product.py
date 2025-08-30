import traceback
from hestia_earth.schema import TermTermType, CycleFunctionalUnit
from hestia_earth.utils.lookup import extract_grouped_data
from hestia_earth.utils.tools import list_sum, flatten, non_empty_list
from hestia_earth.utils.model import filter_list_term_type

from hestia_earth.validation.log import logger
from hestia_earth.validation.utils import _list_sum, _filter_list_errors, get_lookup_value
from .shared import CROP_SITE_TYPE


def validate_economicValueShare(products: list):
    sum = _list_sum(products, 'economicValueShare')
    return sum <= 100.5 or {
        'level': 'error',
        'dataPath': '.products',
        'message': 'economicValueShare should sum to 100 or less across all products',
        'params': {
            'sum': sum
        }
    }


def validate_value_empty(products: list):
    def validate(values: tuple):
        index, product = values
        return len(product.get('value', [])) > 0 or {
            'level': 'warning',
            'dataPath': f".products[{index}]",
            'message': 'may not be 0'
        }

    return _filter_list_errors(map(validate, enumerate(products)))


def validate_value_0(products: list):
    def validate(values: tuple):
        index, product = values
        value = list_sum(product.get('value', [-1]), -1)
        eva = product.get('economicValueShare', 0)
        revenue = product.get('revenue', 0)
        return value != 0 or _filter_list_errors([
            eva == 0 or {
                'level': 'error',
                'dataPath': f".products[{index}].value",
                'message': 'economicValueShare must be 0 for product value 0',
                'params': {
                    'value': eva,
                    'term': product.get('term')
                }
            },
            revenue == 0 or {
                'level': 'error',
                'dataPath': f".products[{index}].value",
                'message': 'revenue must be 0 for product value 0',
                'params': {
                    'value': revenue,
                    'term': product.get('term')
                }
            }
        ])

    return _filter_list_errors(flatten(map(validate, enumerate(products))))


MAX_PRIMARY_PRODUCTS = 1


def validate_primary(products: list):
    primary = list(filter(lambda p: p.get('primary', False), products))
    return len(primary) <= MAX_PRIMARY_PRODUCTS or {
        'level': 'error',
        'dataPath': '.products',
        'message': f"only {MAX_PRIMARY_PRODUCTS} primary product allowed"
    }


def validate_product_ha_functional_unit_ha(cycle: dict, list_key: str = 'products'):
    functional_unit = cycle.get('functionalUnit', CycleFunctionalUnit.RELATIVE.value)

    def validate(values: tuple):
        index, product = values
        term_units = product.get('term', {}).get('units')
        value = list_sum(product.get('value', [0]))
        return term_units != 'ha' or value <= 1 or {
            'level': 'error',
            'dataPath': f".{list_key}[{index}].value",
            'message': 'must be below or equal to 1 for unit in ha',
            'params': {
                'term': product.get('term', {})
            }
        }

    return functional_unit != CycleFunctionalUnit._1_HA.value or \
        _filter_list_errors(map(validate, enumerate(cycle.get(list_key, []))))


def _validate_product_yield(country: dict, list_key: str, threshold: float):
    from .distribution import YIELD_COLUMN, get_stats_by_group_key, validate as validate_distribution

    country_id = country.get('@id')

    def validate(values: tuple):
        index, product = values

        product_id = product.get('term', {}).get('@id')
        product_value = product.get('value', [])

        def _get_mu_sd():
            return get_stats_by_group_key(YIELD_COLUMN, country_id, product_id)

        valid, outliers, min, max = validate_distribution(product_value, threshold, get_mu_sd=_get_mu_sd)
        return valid or {
            'level': 'warning',
            'dataPath': f".{list_key}[{index}].value",
            'message': 'is outside confidence interval',
            'params': {
                'term': product.get('term', {}),
                'country': country,
                'outliers': outliers,
                'threshold': threshold,
                'min': min,
                'max': max
            }
        }
    return validate


def validate_product_yield(
    cycle: dict, site: dict, list_key: str = 'products', threshold: float = 0.95
):
    country = site.get('country', {})
    products = cycle.get(list_key, [])

    try:
        return site.get('siteType') not in CROP_SITE_TYPE or (
            _filter_list_errors(map(_validate_product_yield(country, list_key, threshold), enumerate(products)))
        )
    except Exception:
        stack = traceback.format_exc()
        logger.error(f"Error validating using distribution: '{stack}'")
        return True


def _excreta_term_ids(term: dict, column: str, group_key: str):
    value = get_lookup_value(term, column)
    # handle using `|` to allow multiple values
    return non_empty_list((extract_grouped_data(value, group_key) or '').split('|'))


def _grouped_excreta_term_ids(term: dict, group_keys: list):
    grouped_columns = {
        'kg': 'excretaKgMassTermIds',
        'kg N': 'excretaKgNTermIds',
        'kg VS': 'excretaKgVsTermIds',
    }
    grouped_values = {
        units: flatten([
            _excreta_term_ids(term, column, group_key)
            for group_key in group_keys
        ])
        for units, column in grouped_columns.items()
    }
    # include `default` key if no values found
    return {
        units: grouped_values.get(units, []) + (
            _excreta_term_ids(term, column, 'default') if not grouped_values.get(units) else []
        )
        for units, column in grouped_columns.items()
    }


def validate_excreta_product(cycle: dict, list_key: str = 'products'):
    animal_products = [
        (index, product)
        for index, product in enumerate(cycle.get(list_key, []))
        if product.get('term', {}).get('termType') in [
            TermTermType.ANIMALPRODUCT.value,
            TermTermType.LIVEANIMAL.value,
            TermTermType.LIVEAQUATICSPECIES.value
        ]
    ]
    excreta_products = [
        (index, product)
        for index, product in enumerate(cycle.get(list_key, []))
        if product.get('term', {}).get('termType') in [
            TermTermType.EXCRETA.value
        ]
    ]
    systems = filter_list_term_type(cycle.get('practices', []), TermTermType.SYSTEM)
    group_keys = [s.get('term', {}).get('@id') for s in systems]
    allowed_excreta_per_product = {
        product.get('term', {}).get('@id'): _grouped_excreta_term_ids(product.get('term', {}), group_keys)
        for _i, product in animal_products
    }

    def validate_animal(values: tuple):
        """
        Validate the the animal product has an excreta term
        """
        index, blank_node = values
        term = blank_node.get('term', {})
        term_id = term.get('@id')
        allowed_ids = flatten(allowed_excreta_per_product.get(term_id, {}).values())
        return {
            'level': 'warning',
            'dataPath': f".{list_key}[{index}]",
            'message': 'should add an excreta product',
            'params': {
                'expected': allowed_ids
            }
        }

    def validate_excreta(values: tuple):
        """
        Validate that the excreta is allowed.
        """
        index, blank_node = values
        term = blank_node.get('term', {})
        term_id = term.get('@id')
        allowed_ids = non_empty_list(flatten([
            v.get(term.get('units')) for v in allowed_excreta_per_product.values()
        ]))
        return term_id in allowed_ids or {
            'level': 'error',
            'dataPath': f".{list_key}[{index}].term.@id",
            'message': 'is not an allowed excreta product',
            'params': {
                'current': term_id,
                'expected': allowed_ids
            }
        }

    return (
        _filter_list_errors(map(validate_excreta, excreta_products)) if excreta_products
        else _filter_list_errors(map(validate_animal, animal_products))
    ) if animal_products else True
