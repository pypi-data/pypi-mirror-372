import os
import json
import re
from hestia_earth.schema import NodeType, SiteSiteType, TermTermType
from hestia_earth.utils.tools import flatten, safe_parse_date, non_empty_list

from hestia_earth.validation.gee import get_cached_data
from hestia_earth.validation.utils import find_linked_node, find_related_nodes
from .shared import (
    validate_dates, validate_list_dates, validate_list_dates_format, validate_list_min_below_max,
    validate_list_min_max_lookup, validate_list_dates_after,
    validate_country_region, validate_coordinates, need_validate_coordinates,
    validate_area, need_validate_area, validate_list_term_percent, validate_linked_source_privacy,
    validate_list_date_lt_today, validate_date_lt_today, validate_boundary_area,
    validate_region_size, need_validate_region_size,
    validate_private_has_source,
    validate_list_value_between_min_max,
    validate_list_sum_100_percent,
    validate_list_percent_requires_value,
    validate_list_valueType
)
from .infrastructure import validate_lifespan
from .measurement import (
    validate_soilTexture, validate_depths, validate_required_depths, validate_term_unique,
    validate_require_startDate_endDate, validate_with_models, validate_value_length,
    validate_water_measurements, validate_water_salinity
)
from .property import (
    validate_all as validate_properties
)

_VALIDATE_SITE_LINKED_NODES = os.getenv('VALIDATE_SITE_LINKED_NODES', 'true') == 'true'


INLAND_TYPES = [
    SiteSiteType.CROPLAND.value,
    SiteSiteType.PERMANENT_PASTURE.value,
    SiteSiteType.RIVER_OR_STREAM.value,
    SiteSiteType.LAKE.value,
    SiteSiteType.ANIMAL_HOUSING.value,
    SiteSiteType.AGRI_FOOD_PROCESSOR.value,
    SiteSiteType.FOOD_RETAILER.value,
    SiteSiteType.FOREST.value,
    SiteSiteType.OTHER_NATURAL_VEGETATION.value
]

SITE_TYPES_VALID_VALUES = {
    SiteSiteType.CROPLAND.value: [25, 35, 36],
    SiteSiteType.FOREST.value: [10, 20, 25]
}
MEASUREMENT_REQUIRES_VALUE_TERM_TYPES = [
    TermTermType.SOILTEXTURE,
    TermTermType.SOILTYPE,
    TermTermType.USDASOILTYPE
]


def validate_site_dates(site: dict):
    return validate_dates(site) or {
        'level': 'error',
        'dataPath': '.endDate',
        'message': 'must be greater than startDate'
    }


def validate_site_coordinates(site: dict):
    return need_validate_coordinates(site) and site.get('siteType') in INLAND_TYPES


def validate_siteType(site: dict):
    site_type = site.get('siteType')
    values = SITE_TYPES_VALID_VALUES.get(site_type, [])
    values_str = ', '.join(map(lambda v: str(v), values))

    def validate():
        value = get_cached_data(site, 'siteType', 2019)
        return value in values

    return len(values) == 0 or validate() or {
        'level': 'warning',
        'dataPath': '.siteType',
        'message': ' '.join([
            'The coordinates you have provided are not in a known',
            site_type,
            f"area according to the MODIS Land Cover classification (MCD12Q1.006, LCCS2, bands {values_str})."
        ])
    }


def _parse_cycle_date(date: str, is_end_date: bool = False):
    value = date if len(date) == 10 else f"{date}-01" if len(date) == 7 else (
        f"{date}-12-31" if is_end_date else f"{date}-01-01"
    )
    return safe_parse_date(value)


def validate_cycle_dates(cycles: list):
    # compute list of all days existing between start and end date of the cycles
    values = [(
        cycle,
        _parse_cycle_date(cycle.get('startDate')) if cycle.get('startDate') else None,
        _parse_cycle_date(cycle.get('endDate'), is_end_date=True)
    ) for cycle in cycles]

    day = 60 * 60 * 24  # 1 day step range
    days = flatten(
        list(range(int(start_date.timestamp()), int(end_date.timestamp()) + day, day))
        if start_date else [int(end_date.timestamp())]
        for _cycle, start_date, end_date in values
    )

    seen = set()
    duplicated_dates = [x for x in days if x in seen or seen.add(x)]
    duplicated_cycles = [cycle for cycle, start_date, end_date in values if any([
        (
            int(start_date.timestamp()) <= date <= int(end_date.timestamp())
            if start_date else date == int(end_date.timestamp())
        ) for date in duplicated_dates
    ])]

    return not len(duplicated_dates) or {
        'level': 'error',
        'dataPath': '',
        'message': 'multiple cycles on the same site cannot overlap',
        'params': {
            'ids': [c.get('@id', c.get('id')) for c in duplicated_cycles]
        }
    }


def _extract_linked_data(cycle: dict, node_map: dict = {}):
    cycle_str = json.dumps(cycle)
    match = re.search(r'"impactAssessment":[\s]{([^}]*)}', cycle_str)
    nodes = [json.loads('{' + v + '}') for v in match.groups()] if match else []
    linked_impact_asessments = non_empty_list([find_linked_node(node_map, {
        'type': NodeType.IMPACTASSESSMENT.value,
        'id': n.get('@id', n.get('id'))
    }) for n in nodes])
    linked_cycles = [n.get('cycle', {}) for n in linked_impact_asessments]
    linked_cycle_ids = set([n.get('@id', n.get('id')) for n in linked_cycles])
    return (cycle.get('@id', cycle.get('id')), linked_cycle_ids)


def validate_cycles_linked_ia(cycles: list, node_map: dict = {}):
    linked_data = [_extract_linked_data(cycle, node_map) for cycle in cycles]

    cycle_ids = set([n.get('@id', n.get('id')) for n in cycles])
    incorrect_cycle_ids = set(flatten([
        [cycle_id] + list(linked_cycle_ids.intersection(cycle_ids))
        for cycle_id, linked_cycle_ids in linked_data if linked_cycle_ids.intersection(cycle_ids)
    ]))

    return not incorrect_cycle_ids or {
        'level': 'error',
        'dataPath': '',
        'message': 'cycles linked together cannot be added to the same site',
        'params': {
            'ids': list(incorrect_cycle_ids)
        }
    }


def validate_site(site: dict, node_map: dict = {}):
    """
    Validates a single `Site`.

    Parameters
    ----------
    site : dict
        The `Site` to validate.
    node_map : dict
        The list of all nodes to do cross-validation, grouped by `type` and `id`.

    Returns
    -------
    List
        The list of errors for the `Site`, which can be empty if no errors detected.
    """
    cycles = find_related_nodes(node_map, site, related_key='site', related_type=NodeType.CYCLE)
    return [
        validate_site_dates(site),
        validate_date_lt_today(site, 'startDate'),
        validate_date_lt_today(site, 'endDate'),
        validate_linked_source_privacy(site, 'defaultSource', node_map),
        validate_private_has_source(site, 'defaultSource'),
        validate_siteType(site) if need_validate_coordinates(site) else True,
        validate_country_region(site),
        validate_coordinates(site) if validate_site_coordinates(site) else True,
        validate_area(site) if need_validate_area(site) else True,
        validate_boundary_area(site),
        validate_region_size(site) if need_validate_region_size(site) else True,
        validate_cycle_dates(cycles) if cycles else True,
        not _VALIDATE_SITE_LINKED_NODES or (
            validate_cycles_linked_ia(cycles, node_map) if cycles else True
        )
    ] + flatten(
        ([
            validate_list_dates(site, 'infrastructure'),
            validate_list_dates_format(site, 'infrastructure'),
            validate_list_date_lt_today(site, 'infrastructure', ['startDate', 'endDate']),
            validate_lifespan(site.get('infrastructure'))
        ] if 'infrastructure' in site else []) +
        ([
            validate_list_dates(site, 'measurements'),
            validate_list_dates_after(site, 'startDate', 'measurements', ['startDate', 'endDate', 'dates']),
            validate_list_dates_format(site, 'measurements'),
            validate_list_date_lt_today(site, 'measurements', ['startDate', 'endDate']),
            validate_list_min_below_max(site, 'measurements'),
            validate_list_value_between_min_max(site, 'measurements'),
            validate_list_min_max_lookup(site, 'measurements', 'value'),
            validate_list_min_max_lookup(site, 'measurements', 'min'),
            validate_list_min_max_lookup(site, 'measurements', 'max'),
            validate_list_term_percent(site, 'measurements'),
            validate_list_sum_100_percent(site, 'measurements'),
            validate_list_percent_requires_value(site, 'measurements', MEASUREMENT_REQUIRES_VALUE_TERM_TYPES),
            validate_list_valueType(site, 'measurements'),
            validate_soilTexture(site.get('measurements')),
            validate_depths(site.get('measurements')),
            validate_required_depths(site, 'measurements'),
            validate_term_unique(site.get('measurements')),
            validate_properties(site, 'measurements'),
            validate_require_startDate_endDate(site, 'measurements'),
            validate_with_models(site, 'measurements'),
            validate_value_length(site, 'measurements'),
            validate_water_measurements(site, 'measurements'),
            validate_water_salinity(site, 'measurements'),
        ] if len(site.get('measurements', [])) > 0 else []) +
        ([
            validate_list_sum_100_percent(site, 'management'),
            validate_list_valueType(site, 'management'),
            validate_properties(site, 'management'),
        ] if len(site.get('management', [])) > 0 else [])
    )
