from unittest.mock import patch
import os
import json
from hestia_earth.schema import SiteSiteType

from tests.utils import fixtures_path
from hestia_earth.validation.utils import _group_nodes
from hestia_earth.validation.validators.site import (
    validate_site,
    validate_site_dates,
    validate_site_coordinates,
    validate_siteType,
    validate_cycle_dates,
    validate_cycles_linked_ia
)

fixtures_folder = os.path.join(fixtures_path, 'site')
class_path = 'hestia_earth.validation.validators.site'


@patch(f"{class_path}.validate_boundary_area", return_value=True)
@patch(f"{class_path}.validate_region_size", return_value=True)
@patch(f"{class_path}.validate_coordinates", return_value=True)
def test_validate_site_valid(*args):
    with open(f"{fixtures_folder}/valid.json") as f:
        node = json.load(f)
    results = validate_site(node)
    assert all([r is True for r in results])


def test_validate_site_dates_valid():
    site = {
        'startDate': '2020-01-01',
        'endDate': '2020-01-02'
    }
    assert validate_site_dates(site) is True


def test_validate_site_dates_invalid():
    site = {
        'startDate': '2020-01-02',
        'endDate': '2020-01-01'
    }
    assert validate_site_dates(site) == {
        'level': 'error',
        'dataPath': '.endDate',
        'message': 'must be greater than startDate'
    }


@patch(f"{class_path}.need_validate_coordinates", return_value=True)
def test_validate_site_coordinates(*args):
    site = {'siteType': SiteSiteType.CROPLAND.value}
    assert validate_site_coordinates(site)

    site['siteType'] = SiteSiteType.SEA_OR_OCEAN.value
    assert not validate_site_coordinates(site)


@patch(f"{class_path}.get_cached_data", return_value=25)
def test_validate_siteType_valid(*args):
    site = {
        'siteType': SiteSiteType.FOREST.value,
        'latitude': 44.18753,
        'longitude': -0.62521
    }
    assert validate_siteType(site) is True

    site = {
        'siteType': SiteSiteType.CROPLAND.value,
        'latitude': 44.5096,
        'longitude': 0.40749
    }
    assert validate_siteType(site) is True


@patch(f"{class_path}.get_cached_data", return_value=30)
def test_validate_siteType_invalid(*args):
    site = {
        'siteType': SiteSiteType.CROPLAND.value,
        'latitude': 44.18753,
        'longitude': -0.62521
    }
    assert validate_siteType(site) == {
        'level': 'warning',
        'dataPath': '.siteType',
        'message': 'The coordinates you have provided are not in a known cropland '
        'area according to the MODIS Land Cover classification (MCD12Q1.006, LCCS2, bands 25, 35, 36).'
    }

    site = {
        'siteType': SiteSiteType.FOREST.value,
        'latitude': 44.5096,
        'longitude': 0.40749
    }
    assert validate_siteType(site) == {
        'level': 'warning',
        'dataPath': '.siteType',
        'message': 'The coordinates you have provided are not in a known forest '
        'area according to the MODIS Land Cover classification (MCD12Q1.006, LCCS2, bands 10, 20, 25).'
    }


def test_validate_cycle_dates_valid():
    cycles = [{'endDate': '2020'}, {'endDate': '2021'}]
    assert validate_cycle_dates(cycles) is True

    cycles = [
        {'startDate': '2020-01-01', 'endDate': '2020-06-30'},
        {'startDate': '2020-07-01', 'endDate': '2020-12-31'}
    ]
    assert validate_cycle_dates(cycles) is True


def test_validate_cycle_dates_invalid():
    cycles = [
        {'id': 'cycle1', 'endDate': '2020'},
        {'id': 'cycle2', 'endDate': '2020'},
        {'id': 'cycle3', 'endDate': '2021'}
    ]
    assert validate_cycle_dates(cycles) == {
        'level': 'error',
        'dataPath': '',
        'message': 'multiple cycles on the same site cannot overlap',
        'params': {
            'ids': ['cycle1', 'cycle2']
        }
    }

    cycles = [
        {'id': 'cycle1', 'startDate': '2020-01-01', 'endDate': '2020-07-02'},
        {'id': 'cycle2', 'startDate': '2020-07-01', 'endDate': '2020-12-31'},
        {'id': 'cycle3', 'startDate': '2021-01-01', 'endDate': '2021-12-31'}
    ]
    assert validate_cycle_dates(cycles) == {
        'level': 'error',
        'dataPath': '',
        'message': 'multiple cycles on the same site cannot overlap',
        'params': {
            'ids': ['cycle1', 'cycle2']
        }
    }


def test_validate_cycles_linked_ia_valid():
    with open(f"{fixtures_folder}/cycles-linked-ia/valid.json") as f:
        nodes = json.load(f).get('nodes')
    cycles = [c for c in nodes if c.get('type') == 'Cycle']
    assert validate_cycles_linked_ia(cycles, _group_nodes(nodes)) is True


def test_validate_cycles_linked_ia_invalid():
    with open(f"{fixtures_folder}/cycles-linked-ia/invalid.json") as f:
        nodes = json.load(f).get('nodes')
    cycles = [c for c in nodes if c.get('type') == 'Cycle']
    assert validate_cycles_linked_ia(cycles, _group_nodes(nodes)) == {
        'level': 'error',
        'dataPath': '',
        'message': 'cycles linked together cannot be added to the same site',
        'params': {
            'ids': ['2']
        }
    }
