import os
from hestia_earth.schema import NodeType, SiteSiteType, TermTermType, CycleFunctionalUnit, CycleStartDateDefinition
from hestia_earth.utils.tools import flatten, list_sum, non_empty_list, safe_parse_float
from hestia_earth.utils.date import diff_in_days, is_in_days
from hestia_earth.utils.model import find_term_match, filter_list_term_type, find_primary_product
from hestia_earth.utils.lookup import get_table_value, download_lookup, column_name

from hestia_earth.validation.utils import (
    _filter_list_errors, find_linked_node, _value_average, list_sum_terms, is_same_product, is_permanent_crop,
    get_lookup_value
)
from hestia_earth.validation.terms import TERMS_QUERY, get_terms
from hestia_earth.validation.models import run_models
from .shared import (
    validate_dates, validate_list_dates, validate_list_dates_after, validate_date_lt_today, validate_list_min_below_max,
    validate_list_min_max_lookup, validate_list_term_percent, validate_linked_source_privacy,
    validate_list_dates_length, validate_list_date_lt_today, validate_list_model, validate_list_model_config,
    validate_list_dates_format, validate_list_duplicate_values, validate_private_has_source,
    validate_list_value_between_min_max,
    validate_duplicated_term_units,
    validate_list_sum_100_percent,
    validate_list_percent_requires_value,
    validate_list_valueType,
    validate_other_model,
    validate_nested_existing_node,
    validate_list_country_region
)
from .aggregated_cycle import (
    validate_linked_impactAssessment
)
from .animal import (
    validate_has_animals,
    validate_duplicated_feed_inputs,
    validate_has_pregnancyRateTotal
)
from .emission import validate_linked_terms, validate_method_not_relevant, validate_methodTier_not_relevant
from .input import (
    validate_must_include_id, validate_input_country, validate_related_impacts, validate_input_distribution_value,
    validate_animalFeed_requires_isAnimalFeed,
    validate_saplings,
    validate_input_is_product
)
from .practice import (
    validate_longFallowDuration, validate_excretaManagement, validate_no_tillage,
    validate_tillage_site_type, validate_liveAnimal_system, validate_pastureGrass_key_termType,
    validate_has_pastureGrass, validate_pastureGrass_key_value, validate_defaultValue,
    validate_tillage_values,
    validate_waterRegime_rice_products,
    validate_croppingDuration_riceGrainInHuskFlooded,
    validate_permanent_crop_productive_phase,
    validate_processing_operation,
    validate_landCover_match_products,
    validate_practices_management
)
from .product import (
    validate_economicValueShare, validate_value_empty, validate_value_0,
    validate_primary as validate_product_primary, validate_product_ha_functional_unit_ha, validate_product_yield,
    validate_excreta_product
)
from .completeness import validate_completeness, validate_completeness_blank_nodes
from .transformation import (
    validate_previous_transformation, validate_transformation_excretaManagement, validate_linked_emission
)
from .property import (
    validate_all as validate_properties,
    validate_volatileSolidsContent
)


_VALIDATE_LINKED_IA = os.getenv('VALIDATE_LINKED_IA', 'true') == 'true'
_VALIDATE_COMPLETENESS_AREAS = os.getenv('VALIDATE_COMPLETENESS_AREAS', 'true') == 'true'
_RUN_CYCLE_MODELS = os.getenv('VALIDATE_RUN_CYCLE_MODELS', 'false') == 'true'

SITE_TYPES_CROP_RESIDUE = [
    SiteSiteType.CROPLAND.value,
    SiteSiteType.GLASS_OR_HIGH_ACCESSIBLE_COVER.value
]
SITE_TYPES_NOT_1_HA = [
    SiteSiteType.AGRI_FOOD_PROCESSOR.value,
    SiteSiteType.FOOD_RETAILER.value
]
PRODUCTS_MODEL_CONFIG = {
    'aboveGroundCropResidueTotal': {
        'level': 'warning',
        'model': 'ipcc2006',
        'delta': 0.5,
        'resetDataCompleteness': True
    }
}
INPUTS_MODEL_CONFIG = {
    'saplingsDepreciatedAmountPerCycle': {
        'level': 'warning',
        'model': 'pooreNemecek2018',
        'delta': 0.25,
        'resetDataCompleteness': True
    }
}
# list of models to run before validating the cycle
CYCLE_MODELS_PRE_RUN = [
    {
        "key": "animals",
        "model": "cycle",
        "value": "animal.input.properties",
        "runStrategy": "always",
        "mergeStrategy": "list"
    },
    {
        "key": "inputs",
        "model": "cycle",
        "value": "input.properties",
        "runStrategy": "always",
        "mergeStrategy": "list"
    },
    {
        "key": "products",
        "model": "cycle",
        "value": "product.properties",
        "runStrategy": "always",
        "mergeStrategy": "list"
    }
]
DUPLICATED_TERM_UNITS_TERM_TYPES = [
    TermTermType.ANIMALPRODUCT,
    TermTermType.ORGANICFERTILISER
]
# sum of all values with same termTpe must be exactly 100
PRACTICE_SUM_100_TERM_TYPES = [
    TermTermType.TILLAGE,
    TermTermType.WATERREGIME
]
# sum of all values with same termTpe must be maximum 100
PRACTICE_SUM_100_MAX_TERM_TYPES = [
    TermTermType.CROPRESIDUEMANAGEMENT,
    TermTermType.LANDCOVER
]


def validate_functionalUnit_not_1_ha(cycle: dict, site: dict, other_sites: list = []):
    all_sites = non_empty_list([site] + (other_sites or []))
    site_types = non_empty_list([s.get('siteType') for s in all_sites])
    value = cycle.get('functionalUnit')
    forbidden = CycleFunctionalUnit._1_HA.value
    invalid_site_type = next((site_type for site_type in site_types if site_type in SITE_TYPES_NOT_1_HA), None)
    return value != forbidden or not invalid_site_type or {
        'level': 'error',
        'dataPath': '.functionalUnit',
        'message': f"must not be equal to {forbidden}",
        'params': {
            'siteType': invalid_site_type
        }
    }


def validate_cycle_dates(cycle: dict):
    return validate_dates(cycle) or {
        'level': 'error',
        'dataPath': '.endDate',
        'message': 'must be greater than startDate'
    }


def _should_validate_cycleDuration(cycle: dict):
    return 'cycleDuration' in cycle and is_in_days(cycle.get('startDate')) and is_in_days(cycle.get('endDate'))


def validate_cycleDuration(cycle: dict):
    duration = diff_in_days(cycle.get('startDate'), cycle.get('endDate'))
    return duration == round(cycle.get('cycleDuration'), 1) or {
        'level': 'error',
        'dataPath': '.cycleDuration',
        'message': f"must equal to endDate - startDate in days (~{duration})"
    }


def validate_sum_aboveGroundCropResidue(products: list):
    prefix = 'aboveGroundCropResidue'
    total_residue_index = next((n for n in range(len(products)) if 'Total' in products[n].get(
        'term', {}).get('@id') and products[n].get('term', {}).get('@id').startswith(prefix)), None)
    total_residue = None if total_residue_index is None else _value_average(products[total_residue_index])

    other_residues = list(filter(lambda n: n.get('term').get('@id').startswith(prefix)
                                 and 'Total' not in n.get('term').get('@id'), products))
    other_residues_ids = list(map(lambda n: n.get('term').get('@id'), other_residues))
    other_sum = sum([_value_average(node) for node in other_residues])

    return total_residue_index is None or len(other_residues) == 0 or (total_residue * 1.01) >= other_sum or {
        'level': 'error',
        'dataPath': f".products[{total_residue_index}].value",
        'message': f"must be more than or equal to ({' + '.join(other_residues_ids)})"
    }


def _crop_residue_fate(cycle: dict):
    practices = filter_list_term_type(cycle.get('practices', []), TermTermType.CROPRESIDUEMANAGEMENT)
    products = filter_list_term_type(cycle.get('products', []), TermTermType.CROPRESIDUE)
    terms = get_terms(TERMS_QUERY.CROP_RESIDUE)
    above_terms = list(filter(lambda term: term.startswith('above'), terms))
    sum_above_ground = list_sum_terms(products, above_terms)
    below_terms = list(filter(lambda term: term.startswith('below'), terms))
    sum_below_ground = list_sum_terms(products, below_terms)
    return (practices, sum_above_ground, sum_below_ground)


def validate_crop_residue_complete(cycle: dict, site: dict):
    def validate():
        practices, sum_above_ground, sum_below_ground = _crop_residue_fate(cycle)
        return all([len(practices) > 0, sum_above_ground, sum_below_ground is not None]) or {
            'level': 'error',
            'dataPath': '',
            'message': 'must specify the fate of cropResidue',
            'params': {
                'siteType': SITE_TYPES_CROP_RESIDUE
            }
        }

    data_complete = cycle.get('completeness', {}).get(TermTermType.CROPRESIDUE.value, False)
    site_type = site.get('siteType')
    return not data_complete or site_type not in SITE_TYPES_CROP_RESIDUE or validate()


def validate_crop_residue_incomplete(cycle: dict, site: dict):
    def validate():
        practices, sum_above_ground, sum_below_ground = _crop_residue_fate(cycle)
        return any([len(practices) > 0, sum_above_ground, sum_below_ground is not None]) or {
            'level': 'warning',
            'dataPath': '',
            'message': 'should specify the fate of cropResidue',
            'params': {
                'siteType': SITE_TYPES_CROP_RESIDUE
            }
        }

    data_complete = cycle.get('completeness', {}).get(TermTermType.CROPRESIDUE.value, False)
    site_type = site.get('siteType')
    return data_complete or site_type not in SITE_TYPES_CROP_RESIDUE or validate()


def validate_crop_siteDuration(cycle: dict):
    is_crop = (find_primary_product(cycle) or {}).get('term', {}).get('termType') == TermTermType.CROP.value
    cycleDuration = cycle.get('cycleDuration')
    siteDuration = cycle.get('siteDuration')
    startDateDefinition = cycle.get('startDateDefinition')
    harvest_previous_crop = CycleStartDateDefinition.HARVEST_OF_PREVIOUS_CROP.value
    is_harvest_previous_crop = startDateDefinition == harvest_previous_crop
    permanent_crop = is_permanent_crop(cycle)

    return any([
        not is_crop,
        permanent_crop,
        is_harvest_previous_crop,
        cycleDuration is None,
        siteDuration is None
    ]) or cycleDuration != siteDuration or {
        'level': 'error',
        'dataPath': '.siteDuration',
        'message': 'should not be equal to cycleDuration for crop',
        'params': {
            'current': startDateDefinition,
            'expected': harvest_previous_crop
        }
    }


def validate_siteDuration(cycle: dict):
    cycleDuration = cycle.get('cycleDuration')
    siteDuration = cycle.get('siteDuration')
    has_multiple_sites = len(cycle.get('otherSites', [])) > 0
    return cycleDuration is None or siteDuration is None or has_multiple_sites or siteDuration <= cycleDuration or {
        'level': 'error',
        'dataPath': '.siteDuration',
        'message': 'must be less than or equal to cycleDuration'
    }


def validate_durations(cycle: dict):
    is_relative = cycle.get('functionalUnit') == CycleFunctionalUnit.RELATIVE.value
    siteDuration = cycle.get('siteDuration')
    siteArea = cycle.get('siteArea')

    otherSites = cycle.get('otherSites', [])
    otherSitesDuration = cycle.get('otherSitesDuration', [])
    otherSitesArea = cycle.get('otherSitesArea', [])

    missing_fields = [] if not is_relative else (
        [
            'siteDuration' if siteDuration is None else None,
            'siteArea' if siteArea is None else None,
        ] + non_empty_list([
            'otherSitesDuration' if any([
                len(otherSitesDuration) <= index or otherSitesDuration[index] is None
                for index, value in enumerate(otherSites)
            ]) else None,
            'otherSitesArea' if any([
                len(otherSitesArea) <= index or otherSitesArea[index] is None
                for index, value in enumerate(otherSites)
            ]) else None,
        ] if len(otherSites) > 0 else [])
    )
    return not missing_fields or {
        'level': 'warning',
        'dataPath': '',
        'message': 'should add the fields for a relative cycle',
        'params': {
            'expected': missing_fields
        }
    }


def _product_cover_crop(product: dict):
    is_cover_crop = get_lookup_value(product.get('term', {}), 'possibleCoverCrop')
    return not (not is_cover_crop)  # convert numpy boolean to boolean


def validate_possibleCoverCrop(cycle: dict):
    cover_crop = find_term_match(cycle.get('practices', []), 'coverCrop', None)
    cover_crop_value = cover_crop.get('value', []) if cover_crop else None
    has_cover_crop = cover_crop_value is not None and (
        len(cover_crop_value) == 0 or (cover_crop_value[0] != 0 and cover_crop_value[0] != 'false')
    )
    invalid_product = next((p for p in cycle.get('products', []) if not _product_cover_crop(p)), None)

    return not has_cover_crop or invalid_product is None or {
        'level': 'error',
        'dataPath': '',
        'message': 'cover crop cycle contains non cover crop product'
    }


def validate_set_treatment(cycle: dict, source: dict):
    key = 'treatment'
    has_experimentDesign = 'experimentDesign' in source
    has_treatment = key in cycle
    return not has_experimentDesign or has_treatment or {
        'level': 'warning',
        'dataPath': f".{key}",
        'message': f"should specify a {key} when experimentDesign is specified"
    }


def validate_products_animals(cycle: dict):
    products = cycle.get('products', [])
    has_liveAnimal = len(filter_list_term_type(products, TermTermType.LIVEANIMAL)) > 0
    has_animalProduct = len(filter_list_term_type(products, TermTermType.ANIMALPRODUCT)) > 0
    return not all([has_liveAnimal, has_animalProduct]) or {
        'level': 'warning',
        'dataPath': '.products',
        'message': 'should not specify both liveAnimal and animalProduct'
    }


def validate_stocking_density(cycle: dict, site: dict, list_key: str = 'practices'):
    """
    Incite users to add the practice "Stocking density" on relative functionalUnit and permanent pasture.
    """
    term_id = 'stockingDensityPermanentPastureAverage'
    is_relative = cycle.get('functionalUnit') == CycleFunctionalUnit.RELATIVE.value
    is_permanent_pasture = site.get('siteType') == SiteSiteType.PERMANENT_PASTURE.value
    products = cycle.get('products', [])
    has_animals = any([
        len(filter_list_term_type(products, [TermTermType.LIVEANIMAL, TermTermType.ANIMALPRODUCT])) > 0,
        len(cycle.get('animals', [])) > 0
    ])
    has_practice = find_term_match(cycle.get(list_key, []), term_id, None) is not None
    return not all([is_relative, is_permanent_pasture, has_animals]) or has_practice or {
        'level': 'warning',
        'dataPath': f".{list_key}",
        'message': f"should add the term {term_id}",
        'params': {
            'expected': term_id
        }
    }


def _filter_same_cycle(cycle: dict):
    def filter(impact_assessment: dict):
        ia_cycle = impact_assessment.get('cycle', {})
        return any([
            ia_cycle.get('id') and ia_cycle.get('id') == cycle.get('id'),
            ia_cycle.get('@id') and ia_cycle.get('@id') == cycle.get('@id')
        ])
    return filter


def _should_have_linked_impact_assessment(product: dict):
    term = product.get('term', {})
    should_generate_ia = get_lookup_value(term, 'generateImpactAssessment')
    return all([
        list_sum(product.get('value', [])) > 0,
        product.get('economicValueShare', 1) != 0,
        product.get('price', 1) != 0,
        product.get('revenue', 1) != 0,
        str(should_generate_ia).lower() != 'false'
    ])


def validate_linked_impact_assessment(cycle: dict, node_map: dict = {}):
    """
    Validate that every product that should have an ImpactAssessment, actually has one.
    In some cases, the same product could be added multiple times with different unique properties, in which case
    an ImpactAssessment should exist for each.
    """
    uploaded_impact_assessments = node_map.get(NodeType.IMPACTASSESSMENT.value, {}).values()
    related_impact_assessments = list(filter(_filter_same_cycle(cycle), uploaded_impact_assessments))

    def validate(values: tuple):
        index, product = values
        same_products = [v for v in related_impact_assessments if is_same_product(product, v.get('product', {}))]
        message = 'multiple ImpactAssessment are associated with this Product' if len(same_products) > 1 else \
            'no ImpactAssessment are associated with this Product'
        return len(same_products) == 1 or {
            'level': 'error',
            'dataPath': f".products[{index}].term",
            'message': message,
            'params': {
                'product': product.get('term', {}),
                'node': {
                    'type': 'Cycle',
                    'id': cycle.get('id', cycle.get('@id'))
                }
            }
        }

    products = enumerate(cycle.get('products', []))
    products = [(index, product) for index, product in products if _should_have_linked_impact_assessment(product)]
    return _filter_list_errors(flatten(map(validate, products)))


def _allowed_animal_ids(term: dict):
    value = get_lookup_value(term, 'allowedAnimalProductTermIds')
    return (value or '').split(';')


def validate_animal_product_mapping(cycle: dict):
    """
    Validate mapping between the `liveAnimal` in the `Animal` blank nodes, and the Cycle `Product` as `animalProduct`.
    """
    live_animals = filter_list_term_type(cycle.get('animals', []), TermTermType.LIVEANIMAL)
    allowed_term_ids = sorted(list(set(
        non_empty_list(flatten([_allowed_animal_ids(v.get('term', {})) for v in live_animals]))
    )))

    def validate(values: tuple):
        index, product = values
        term = product.get('term', {})
        term_id = term.get('@id')
        is_animal_product = term.get('termType') == TermTermType.ANIMALPRODUCT.value
        return not is_animal_product or term_id in allowed_term_ids or {
            'level': 'error',
            'dataPath': f".products[{index}].term",
            'message': 'is not an allowed animalProduct',
            'params': {
                'expected': allowed_term_ids
            }
        }

    products = enumerate(cycle.get('products', []))
    return _filter_list_errors(flatten(map(validate, products))) if allowed_term_ids else True


def _is_substrate_practice(practice: dict):
    term_id = practice.get('term', {}).get('@id')
    return 'substrate' in term_id.lower()


def validate_requires_substrate(cycle: dict, site: dict):
    site_type = site.get('siteType')
    substrate_practice = next((p for p in cycle.get('practices', []) if _is_substrate_practice(p)), None)
    return not site_type == SiteSiteType.GLASS_OR_HIGH_ACCESSIBLE_COVER.value or (
        not substrate_practice or
        len(filter_list_term_type(cycle.get('inputs', []), TermTermType.SUBSTRATE)) > 0 or
        {
            'level': 'error',
            'dataPath': '.inputs',
            'message': 'must add substrate inputs',
            'params': {
                'term': substrate_practice.get('term')
            }
        }
    )


def validate_maximum_cycleDuration(cycle: dict):
    cycleDuration = cycle.get('cycleDuration')
    startDate = cycle.get('startDate')
    endDate = cycle.get('endDate')
    use_dates = all([not cycleDuration, endDate, startDate])
    duration = diff_in_days(startDate, endDate) if use_dates else cycleDuration

    product = (find_primary_product(cycle) or {}).get('term', {})
    is_crop = product.get('termType') == TermTermType.CROP.value
    max_cycleDuration = get_lookup_value(product, 'maximumCycleDuration')
    return not duration or not is_crop or not max_cycleDuration or duration <= int(max_cycleDuration) * 1.05 or {
        'level': 'error',
        'dataPath': '.startDate' if use_dates else '.cycleDuration',
        'message': 'must be below maximum cycleDuration',
        'params': {
            'comparison': '<=',
            'limit': int(max_cycleDuration),
            'exclusive': False,
            'current': duration
        }
    }


def validate_riceGrainInHuskFlooded_minimum_cycleDuration(cycle: dict, site: dict):
    cycleDuration = cycle.get('cycleDuration')
    country_id = site.get('country', {}).get('@id')
    product = find_primary_product(cycle) or {}
    product_term_id = product.get('term', {}).get('@id')
    check_value = all([
        site.get('siteType') == SiteSiteType.CROPLAND.value,
        product_term_id == 'riceGrainInHuskFlooded'
    ])
    min_cycleDuration = safe_parse_float(
        get_table_value(
            download_lookup('region-ch4ef-IPCC2019.csv') if product else None,
            'termid',
            country_id,
            column_name('Rice_croppingDuration_days_min')
        ), default=0
    ) if check_value else 0
    return min_cycleDuration == 0 or not cycleDuration or cycleDuration >= int(min_cycleDuration) or {
        'level': 'warning',
        'dataPath': '.cycleDuration',
        'message': 'should be more than the cropping duration',
        'params': {
            'expected': int(min_cycleDuration),
            'current': cycleDuration
        }
    }


def validate_cycle(cycle: dict, node_map: dict = {}):
    """
    Validates a single `Cycle`.

    Parameters
    ----------
    cycle : dict
        The `Cycle` to validate.
    node_map : dict
        The list of all nodes to do cross-validation, grouped by `type` and `id`.

    Returns
    -------
    List
        The list of errors for the `Cycle`, which can be empty if no errors detected.
    """
    site = find_linked_node(node_map, cycle.get('site', {}))
    source = find_linked_node(node_map, cycle.get('defaultSource', {}))
    other_sites = non_empty_list([find_linked_node(node_map, s) for s in cycle.get('otherSites', [])])
    is_aggregated = cycle.get('aggregated', False)
    cycle = run_models(cycle, CYCLE_MODELS_PRE_RUN) if _RUN_CYCLE_MODELS else cycle
    return flatten([
        validate_cycle_dates(cycle),
        validate_date_lt_today(cycle, 'startDate'),
        validate_date_lt_today(cycle, 'endDate'),
        validate_linked_source_privacy(cycle, 'defaultSource', node_map),
        validate_private_has_source(cycle, 'defaultSource'),
        validate_cycleDuration(cycle) if _should_validate_cycleDuration(cycle) else True,
        validate_completeness(cycle, site, other_sites),
        is_aggregated or not _VALIDATE_COMPLETENESS_AREAS or validate_completeness_blank_nodes(cycle),
        validate_crop_siteDuration(cycle),
        validate_siteDuration(cycle),
        validate_durations(cycle),
        validate_possibleCoverCrop(cycle),
        validate_products_animals(cycle),
        validate_set_treatment(cycle, source) if source else True,
        validate_functionalUnit_not_1_ha(cycle, site, other_sites) if site else True,
        validate_stocking_density(cycle, site) if site else True,
        validate_animalFeed_requires_isAnimalFeed(cycle, site) if site else True,
        validate_requires_substrate(cycle, site) if site else True,
        validate_riceGrainInHuskFlooded_minimum_cycleDuration(cycle, site) if site else True,
        validate_animal_product_mapping(cycle),
        validate_duplicated_feed_inputs(cycle),
        is_aggregated or validate_maximum_cycleDuration(cycle),
        validate_nested_existing_node(cycle, 'site'),
        validate_nested_existing_node(cycle, 'otherSites'),
        not is_aggregated or validate_linked_impactAssessment(cycle, 'inputs')
    ]) + flatten(
        ([
            validate_list_model(cycle, 'emissions'),
            validate_list_dates(cycle, 'emissions'),
            validate_list_dates_after(cycle, 'startDate', 'emissions', ['startDate', 'endDate']),
            validate_list_dates_format(cycle, 'emissions'),
            validate_list_min_below_max(cycle, 'emissions'),
            validate_list_value_between_min_max(cycle, 'emissions'),
            validate_list_term_percent(cycle, 'emissions'),
            validate_list_dates_length(cycle, 'emissions'),
            validate_list_date_lt_today(cycle, 'emissions', ['startDate', 'endDate']),
            validate_properties(cycle, 'emissions'),
            validate_linked_terms(cycle, 'emissions', 'inputs', 'inputs', True),
            validate_linked_terms(cycle, 'emissions', 'transformation', 'transformations', True),
            validate_method_not_relevant(cycle, 'emissions'),
            validate_methodTier_not_relevant(cycle, 'emissions'),
            validate_other_model(cycle, 'emissions')
        ] if len(cycle.get('emissions', [])) > 0 else []) +
        ([
            validate_list_country_region(cycle, 'inputs'),
            validate_list_dates(cycle, 'inputs'),
            validate_list_dates_after(cycle, 'startDate', 'inputs', ['startDate', 'endDate', 'dates']),
            validate_list_dates_format(cycle, 'inputs'),
            validate_list_dates_length(cycle, 'inputs'),
            validate_list_date_lt_today(cycle, 'inputs', ['startDate', 'endDate']),
            validate_list_min_below_max(cycle, 'inputs'),
            validate_list_value_between_min_max(cycle, 'inputs'),
            validate_list_min_max_lookup(cycle, 'inputs', 'value'),
            validate_list_min_max_lookup(cycle, 'inputs', 'min'),
            validate_list_min_max_lookup(cycle, 'inputs', 'max'),
            validate_list_term_percent(cycle, 'inputs'),
            validate_list_sum_100_percent(cycle, 'inputs'),
            validate_properties(cycle, 'inputs'),
            validate_volatileSolidsContent(cycle, 'inputs'),
            validate_must_include_id(cycle['inputs']),
            validate_input_country(cycle, 'inputs'),
            validate_related_impacts(cycle, 'inputs', node_map),
            validate_input_distribution_value(cycle, site, 'inputs') if site else True,
            validate_list_model_config(cycle, 'inputs', INPUTS_MODEL_CONFIG),
            validate_duplicated_term_units(cycle, 'inputs', DUPLICATED_TERM_UNITS_TERM_TYPES),
            validate_saplings(cycle, 'inputs'),
            validate_input_is_product(cycle, 'inputs'),
        ] if len(cycle.get('inputs', [])) > 0 else []) +
        ([
            # skip validation for aggregated Cycle as we only auto-generate IAs
            is_aggregated or not _VALIDATE_LINKED_IA or validate_linked_impact_assessment(cycle, node_map),
            validate_list_dates(cycle, 'products'),
            validate_list_dates_after(cycle, 'startDate', 'products', ['startDate', 'endDate', 'dates']),
            validate_list_dates_format(cycle, 'products'),
            validate_list_dates_length(cycle, 'products'),
            validate_list_date_lt_today(cycle, 'products', ['startDate', 'endDate']),
            validate_list_min_below_max(cycle, 'products'),
            validate_list_value_between_min_max(cycle, 'products'),
            validate_list_term_percent(cycle, 'products'),
            validate_list_sum_100_percent(cycle, 'products'),
            validate_properties(cycle, 'products'),
            validate_economicValueShare(cycle.get('products')),
            validate_sum_aboveGroundCropResidue(cycle.get('products')),
            validate_value_empty(cycle.get('products')),
            validate_value_0(cycle.get('products')),
            validate_product_primary(cycle.get('products')),
            validate_volatileSolidsContent(cycle, 'products'),
            validate_volatileSolidsContent(cycle, 'products'),
            validate_crop_residue_complete(cycle, site) if site else True,
            validate_crop_residue_incomplete(cycle, site) if site else True,
            validate_list_model_config(cycle, 'products', PRODUCTS_MODEL_CONFIG),
            validate_excreta_product(cycle, 'products'),
            validate_product_ha_functional_unit_ha(cycle, 'products'),
            validate_product_yield(cycle, site, 'products') if site else True,
            validate_has_animals(cycle),
            validate_duplicated_term_units(cycle, 'products', DUPLICATED_TERM_UNITS_TERM_TYPES)
        ] if len(cycle.get('products', [])) > 0 else []) +
        ([
            validate_list_dates(cycle, 'practices'),
            validate_list_dates_after(cycle, 'startDate', 'practices', ['startDate', 'endDate', 'dates']),
            validate_list_dates_format(cycle, 'practices'),
            validate_list_date_lt_today(cycle, 'practices', ['startDate', 'endDate']),
            validate_list_min_below_max(cycle, 'practices'),
            validate_list_value_between_min_max(cycle, 'practices'),
            validate_list_term_percent(cycle, 'practices'),
            validate_list_sum_100_percent(cycle, 'practices'),
            validate_list_percent_requires_value(
                cycle, 'practices', PRACTICE_SUM_100_TERM_TYPES + PRACTICE_SUM_100_MAX_TERM_TYPES
            ),
            validate_list_valueType(cycle, 'practices'),
            validate_properties(cycle, 'practices'),
            validate_defaultValue(cycle, 'practices'),
            validate_longFallowDuration(cycle.get('practices')),
            validate_volatileSolidsContent(cycle, 'practices'),
            validate_list_duplicate_values(cycle, 'practices', 'term.termType', TermTermType.EXCRETAMANAGEMENT.value),
            validate_excretaManagement(cycle, cycle.get('practices')),
            validate_no_tillage(cycle.get('practices')),
            validate_tillage_values(cycle.get('practices')),
            validate_tillage_site_type(cycle.get('practices'), site) if site else True,
            validate_liveAnimal_system(cycle),
            validate_pastureGrass_key_termType(cycle, 'practices'),
            validate_pastureGrass_key_value(cycle, 'practices'),
            validate_has_pastureGrass(cycle, site, 'practices') if site else True,
            validate_waterRegime_rice_products(cycle),
            validate_croppingDuration_riceGrainInHuskFlooded(cycle),
            validate_permanent_crop_productive_phase(cycle, 'practices'),
            validate_processing_operation(cycle, site, 'practices') if site else True,
            validate_landCover_match_products(cycle, site, 'practices') if site else True,
            validate_practices_management(cycle, site, 'practices') if site else True,
        ] if len(cycle.get('practices', [])) > 0 else []) +
        ([
            validate_volatileSolidsContent(cycle, 'animals'),
            validate_properties(cycle, 'animals'),
            validate_has_pregnancyRateTotal(cycle)
        ] if len(cycle.get('animals', [])) > 0 else []) +
        ([
            validate_list_dates(cycle, 'transformations'),
            validate_list_dates_after(cycle, 'startDate', 'transformations', ['startDate', 'endDate']),
            validate_list_dates_format(cycle, 'transformations'),
            validate_list_date_lt_today(cycle, 'transformations', ['startDate', 'endDate']),
            validate_previous_transformation(cycle, 'transformations'),
            validate_transformation_excretaManagement(cycle, 'transformations'),
            validate_linked_emission(cycle, 'transformations')
        ] if len(cycle.get('transformations', [])) > 0 else [])
    )
