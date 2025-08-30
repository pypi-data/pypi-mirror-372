from hestia_earth.schema import SiteSiteType, TermTermType
from hestia_earth.utils.model import filter_list_term_type, find_term_match, find_primary_product
from hestia_earth.utils.tools import flatten, list_sum, safe_parse_float, non_empty_list
from hestia_earth.utils.lookup import download_lookup, get_table_value, column_name
from hestia_earth.utils.blank_node import get_node_value

from hestia_earth.validation.utils import (
    _filter_list_errors, get_lookup_value, is_permanent_crop, blank_node_properties_group
)
from hestia_earth.validation.terms import TERMS_QUERY, get_terms
from .shared import valid_list_sum, is_value_below


def validate_defaultValue(data: dict, list_key: str = 'practices'):
    def validate(values: tuple):
        index, practice = values
        term = practice.get('term', {})
        has_value = len(practice.get('value', [])) > 0
        is_value_required = any([term.get('units', '').startswith('%')])
        default_value = get_lookup_value(term, 'defaultValue')
        return has_value or default_value is None or is_value_required or {
            'level': 'warning',
            'dataPath': f".{list_key}[{index}]",
            'message': 'should specify a value when HESTIA has a default one',
            'params': {
                'term': term,
                'expected': default_value
            }
        }

    return _filter_list_errors(flatten(map(validate, enumerate(data.get(list_key, [])))))


def validate_longFallowDuration(practices: list):
    max_nb_years = 5
    longFallowDuration = find_term_match(practices, 'longFallowDuration', None)
    longFallowDuration_index = practices.index(longFallowDuration) if longFallowDuration else 0
    value = list_sum(longFallowDuration.get('value', [0])) if longFallowDuration else 0
    rotationDuration = list_sum(find_term_match(practices, 'rotationDuration').get('value', 0))
    return value == 0 or ((rotationDuration - value) / value) < max_nb_years * 365 or {
        'level': 'error',
        'dataPath': f".practices[{longFallowDuration_index}].value",
        'message': f"longFallowDuration must be lower than {max_nb_years} years"
    }


def validate_waterRegime_rice_products(cycle: dict, list_key: str = 'practices'):
    all_rice_product_ids = get_terms(TERMS_QUERY.RICE)
    primary_product = find_primary_product(cycle) or {}
    primary_product_id = primary_product.get('term', {}).get('@id')
    is_rice_product = primary_product_id in all_rice_product_ids

    practice_term_type = TermTermType.WATERREGIME.value

    def validate(values: tuple):
        index, practice = values
        term = practice.get('term', {})
        term_type = term.get('termType')
        has_value = list_sum(practice.get('value') or [0], 0) > 0
        allowed_product_ids = (get_lookup_value(term, 'allowedRiceTermIds') or '').split(';')
        is_allowed = primary_product_id in allowed_product_ids
        return term_type != practice_term_type or not has_value or is_allowed or {
            'level': 'error',
            'dataPath': f".{list_key}[{index}].term",
            'message': 'rice products not allowed for this water regime practice',
            'params': {
                'term': term,
                'products': [primary_product.get('term', {})]
            }
        }

    return not is_rice_product or _filter_list_errors(flatten(map(validate, enumerate(cycle.get(list_key, [])))))


def validate_croppingDuration_riceGrainInHuskFlooded(cycle: dict, list_key: str = 'practices'):
    has_product = find_term_match(cycle.get('products', []), 'riceGrainInHuskFlooded')

    practice_id = 'croppingDuration'
    practice_index = next((
        i for i, p in enumerate(cycle.get(list_key, [])) if p.get('term', {}).get('@id') == practice_id
    ), -1) if has_product else -1

    lookup = download_lookup('region-ch4ef-IPCC2019.csv')
    country_id = cycle.get('site', {}).get('country', {}).get('@id')
    min_value = safe_parse_float(
        get_table_value(lookup, 'termid', country_id, column_name('Rice_croppingDuration_days_min')),
        None
    )
    max_value = safe_parse_float(
        get_table_value(lookup, 'termid', country_id, column_name('Rice_croppingDuration_days_max')),
        None
    )

    value = list_sum(cycle.get(list_key, [])[practice_index].get('value', [])) if practice_index >= 0 else None

    return practice_index == -1 or all([is_value_below(value, max_value), is_value_below(min_value, value)]) or {
        'level': 'error',
        'dataPath': f".{list_key}[{practice_index}].value",
        'message': f"{practice_id} must be between min and max",
        'params': {
            'min': min_value,
            'max': max_value
        }
    }


def validate_excretaManagement(node: dict, practices: list):
    has_input = len(filter_list_term_type(node.get('inputs', []), TermTermType.EXCRETA)) > 0
    has_practice = len(filter_list_term_type(practices, TermTermType.EXCRETAMANAGEMENT)) > 0
    return not has_practice or has_input or {
        'level': 'error',
        'dataPath': '.practices',
        'message': 'an excreta input is required when using an excretaManagement practice'
    }


NO_TILLAGE_ID = 'noTillage'
FULL_TILLAGE_ID = 'fullTillage'
TILLAGE_DEPTH_ID = 'tillageDepth'
NB_TILLAGES_ID = 'numberOfTillages'


def _practice_is_tillage(practice: dict):
    term = practice.get('term', {})
    term_type = practice.get('term', {}).get('termType')
    return True if term_type == TermTermType.OPERATION.value and get_lookup_value(term, 'isTillage') else False


def validate_no_tillage(practices: list):
    tillage_practices = filter_list_term_type(practices, TermTermType.TILLAGE)
    no_tillage = find_term_match(tillage_practices, NO_TILLAGE_ID, None)
    no_value = list_sum(no_tillage.get('value', [100]), 100) if no_tillage else 0

    return _filter_list_errors([{
        'level': 'error',
        'dataPath': f".practices[{index}]",
        'message': f"is not allowed in combination with {NO_TILLAGE_ID}"
    } for index, p in enumerate(practices) if _practice_is_tillage(p)] if no_value == 100 else [])


_TILLAGE_SITE_TYPES = [
    SiteSiteType.CROPLAND.value
]


def validate_tillage_site_type(practices: list, site: dict):
    has_tillage = len(filter_list_term_type(practices, TermTermType.TILLAGE)) > 0
    site_type = site.get('siteType')
    return site_type not in _TILLAGE_SITE_TYPES or has_tillage or {
        'level': 'warning',
        'dataPath': '.practices',
        'message': 'should contain a tillage practice'
    }


def validate_tillage_values(practices: list):
    tillage_100_index = next((index for index in range(0, len(practices)) if all([
        practices[index].get('term', {}).get('termType') == TermTermType.TILLAGE.value,
        list_sum(practices[index].get('value', [0])) == 100
    ])), -1)
    tillage_100_practice = practices[tillage_100_index] if tillage_100_index >= 0 else None
    tillage_100_term = (tillage_100_practice or {}).get('term', {})

    tillage_depth_practice = find_term_match(practices, TILLAGE_DEPTH_ID)
    nb_tillages_practice = find_term_match(practices, NB_TILLAGES_ID)
    error_message = (
        'cannot use no tillage if depth or number of tillages is not 0' if all([
            tillage_100_term.get('@id') == NO_TILLAGE_ID,
            any([
                tillage_depth_practice and list_sum(tillage_depth_practice.get('value', [0])) > 0,
                nb_tillages_practice and list_sum(nb_tillages_practice.get('value', [0])) > 0
            ])

        ])
        else 'cannot use full tillage if depth or number of tillages is 0' if all([
            tillage_100_term.get('@id') == FULL_TILLAGE_ID,
            any([
                tillage_depth_practice and list_sum(tillage_depth_practice.get('value', [1])) == 0,
                nb_tillages_practice and list_sum(nb_tillages_practice.get('value', [1])) == 0
            ])
        ])
        else None
    ) if tillage_100_practice else None
    return {
        'level': 'error',
        'dataPath': f".practices[{tillage_100_index}]",
        'message': error_message
    } if error_message else True


def validate_liveAnimal_system(data: dict):
    has_animal = len(filter_list_term_type(data.get('products', []), [
        TermTermType.ANIMALPRODUCT, TermTermType.LIVEANIMAL
    ])) > 0
    has_system = len(filter_list_term_type(data.get('practices', []), TermTermType.SYSTEM)) > 0
    return not has_animal or has_system or {
        'level': 'warning',
        'dataPath': '.practices',
        'message': 'should add an animal production system'
    }


PASTURE_GRASS_TERM_ID = 'pastureGrass'


def validate_pastureGrass_key_termType(data: dict, list_key: str = 'practices'):
    validate_key_termType = TermTermType.LANDCOVER.value

    def validate(values: tuple):
        index, practice = values
        term_id = practice.get('term', {}).get('@id')
        key_termType = practice.get('key', {}).get('termType')
        return term_id != PASTURE_GRASS_TERM_ID or not key_termType or key_termType == validate_key_termType or {
            'level': 'error',
            'dataPath': f".{list_key}[{index}].key",
            'message': f"{PASTURE_GRASS_TERM_ID} key termType must be '{validate_key_termType}'",
            'params': {
                'value': key_termType,
                'expected': validate_key_termType,
                'term': practice.get('key', {})
            }
        }

    return _filter_list_errors(flatten(map(validate, enumerate(data.get(list_key, [])))))


def validate_pastureGrass_key_value(data: dict, list_key: str = 'practices'):
    practices = [p for p in data.get(list_key, []) if p.get('term', {}).get('@id') == PASTURE_GRASS_TERM_ID]
    total_value, valid_sum = valid_list_sum(practices)
    return {
        'level': 'error',
        'dataPath': f".{list_key}",
        'message': 'all values must be numbers'
    } if not valid_sum else len(practices) == 0 or total_value == 100 or {
        'level': 'error',
        'dataPath': f".{list_key}",
        'message': f"the sum of all {PASTURE_GRASS_TERM_ID} values must be 100",
        'params': {
            'expected': 100,
            'current': total_value
        }
    }


def validate_has_pastureGrass(data: dict, site: dict, list_key: str = 'practices'):
    site_type = site.get('siteType')
    has_practice = find_term_match(data.get(list_key, []), PASTURE_GRASS_TERM_ID, None) is not None
    return site_type not in [
        SiteSiteType.PERMANENT_PASTURE.value
    ] or has_practice or {
        'level': 'warning',
        'dataPath': f".{list_key}",
        'message': f"should add the term {PASTURE_GRASS_TERM_ID}"
    }


def validate_permanent_crop_productive_phase(cycle: dict, list_key: str = 'practices'):
    practice_id = 'productivePhasePermanentCrops'
    permanent_crop = is_permanent_crop(cycle)
    primary_product = find_primary_product(cycle) or {}
    product_value = list_sum(primary_product.get('value', [-1]), default=-1)
    has_practice = find_term_match(cycle.get(list_key, []), practice_id, None) is not None
    return not permanent_crop or product_value != 0 or has_practice or {
        'level': 'error',
        'dataPath': f".{list_key}",
        'message': f"must add the term {practice_id}"
    }


def validate_processing_operation(cycle: dict, site: dict, list_key: str = 'practices'):
    operations = filter_list_term_type(cycle.get(list_key, []), TermTermType.OPERATION)
    primary_processing_operations = [
        v for v in operations if all([
            not (not get_lookup_value(v.get('term', {}), 'isProcessingOperation')),
            (v.get('primaryPercent') or 0) > 0
        ])
    ]
    is_valid = any([
        site.get('siteType') != SiteSiteType.AGRI_FOOD_PROCESSOR.value,
        len(primary_processing_operations) > 0
    ])
    return is_valid or {
        'level': 'error',
        'dataPath': f".{list_key}",
        'message': 'must have a primary processing operation'
    }


def validate_landCover_match_products(cycle: dict, site: dict, list_key: str = 'practices'):
    # validate that at least one `landCover` practice matches an equivalent Product
    landCover_practice_ids = [
        p.get('term', {}).get('@id')
        for p in filter_list_term_type(cycle.get('practices', []), TermTermType.LANDCOVER)
        # ignore any practices with a `blankNodesGroup=Cover crops`
        if blank_node_properties_group(p) != 'Cover crops'
    ]
    landCover_product_ids = non_empty_list([
        get_lookup_value(p.get('term', {}), 'landCoverTermId')
        for p in cycle.get('products', [])
    ])
    is_cropland = site.get('siteType') == SiteSiteType.CROPLAND.value

    return not is_cropland or not landCover_practice_ids or not landCover_product_ids or any([
        (term_id in landCover_product_ids) for term_id in landCover_practice_ids
    ]) or {
        'level': 'error',
        'dataPath': f".{list_key}",
        'message': 'at least one landCover practice must match an equivalent product',
        'params': {
            'current': landCover_practice_ids,
            'expected': landCover_product_ids
        }
    }


def validate_practices_management(cycle: dict, site: dict, list_key: str = 'practices'):
    # validate that practices and management nodes, with same term and dates, have the same value
    management_nodes = site.get('management', [])

    def validate(values: tuple):
        index, practice = values
        term_id = practice.get('term', {}).get('@id')
        value = get_node_value(practice)
        management_node = [
            v for v in management_nodes
            if all([
                v.get('term', {}).get('@id') == term_id,
                v.get('startDate') == practice.get('startDate'),
                v.get('endDate') == practice.get('endDate'),
            ])
        ]
        return len(management_node) == 0 or management_node[0].get('value') == value or {
            'level': 'error',
            'dataPath': f".{list_key}[{index}].value",
            'message': 'should match the site management node value',
            'params': {
                'current': value,
                'expected': management_node[0].get('value')
            }
        }

    return _filter_list_errors(
        flatten(map(validate, enumerate(cycle.get(list_key, []))))
    ) if management_nodes else True
