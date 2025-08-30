from unittest.mock import patch
import os
import json

from tests.utils import fixtures_path, fake_get_terms
from hestia_earth.validation.validators.impact_assessment import (
    validate_impact_assessment,
    validate_empty,
    validate_linked_cycle_product,
    validate_linked_cycle_endDate
)

fixtures_folder = os.path.join(fixtures_path, 'impactAssessment')


@patch('hestia_earth.validation.validators.indicator.get_terms', return_value=fake_get_terms)
def test_validate_impact_assessment_valid(*args):
    with open(f"{fixtures_folder}/valid.json") as f:
        node = json.load(f)
    results = validate_impact_assessment(node)
    assert all([r is True for r in results])


def test_validate_empty_valid():
    # with a cycle => valid
    assert validate_empty({'cycle': {'id': 'test'}}) is True
    # with emissionsResourceUse => valid
    assert validate_empty({'emissionsResourceUse': [{}]}) is True
    # with impacts => valid
    assert validate_empty({'impacts': [{}]}) is True
    # with endpoints => valid
    assert validate_empty({'endpoints': [{}]}) is True


def test_validate_empty_invalid():
    assert validate_empty({}) == {
        'level': 'error',
        'dataPath': '',
        'message': 'should not be empty',
        'params': {
            'type': 'ImpactAssessment'
        }
    }


def test_validate_linked_cycle_product_valid():
    with open(f"{fixtures_folder}/cycle-contains-product/valid.json") as f:
        data = json.load(f)
    assert validate_linked_cycle_product(data, data.get('cycle')) is True


def test_validate_linked_cycle_product_invalid():
    with open(f"{fixtures_folder}/cycle-contains-product/invalid.json") as f:
        data = json.load(f)
    assert validate_linked_cycle_product(data, data.get('cycle')) == {
        'level': 'error',
        'dataPath': '.product',
        'message': 'should be included in the cycle products',
        'params': {
            'product': {
                '@type': 'Term',
                '@id': 'maizeGrain'
            },
            'node': {
                'type': 'Cycle',
                'id': 'fake-cycle'
            }
        }
    }


def test_validate_linked_cycle_endDate_valid():
    with open(f"{fixtures_folder}/cycle-endDate/valid.json") as f:
        data = json.load(f)
    assert validate_linked_cycle_endDate(data, data.get('cycle')) is True


def test_validate_linked_cycle_endDate_invalid():
    with open(f"{fixtures_folder}/cycle-endDate/invalid.json") as f:
        data = json.load(f)
    assert validate_linked_cycle_endDate(data, data.get('cycle')) == {
        'level': 'error',
        'dataPath': '.endDate',
        'message': 'must be equal to the Cycle endDate'
    }
