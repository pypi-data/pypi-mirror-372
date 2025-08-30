import os
import json

from tests.utils import fixtures_path
from hestia_earth.validation.validators.aggregated_cycle import (
    validate_linked_impactAssessment
)

class_path = 'hestia_earth.validation.validators.aggregated_cycle'
fixtures_folder = os.path.join(fixtures_path, 'aggregated', 'cycle')


def test_validate_linked_impactAssessment_valid():
    # no inputs should be valid
    assert validate_linked_impactAssessment({}) is True

    with open(f"{fixtures_folder}/inputs-impactAssessment/valid.json") as f:
        data = json.load(f)
    assert validate_linked_impactAssessment(data, 'inputs') is True


def test_validate_linked_impactAssessment_invalid():
    with open(f"{fixtures_folder}/inputs-impactAssessment/invalid-world.json") as f:
        data = json.load(f)
    assert validate_linked_impactAssessment(data, 'inputs') == {
        'level': 'error',
        'dataPath': '.inputs[0].impactAssessment',
        'message': 'must be linked to a verified country-level Impact Assessment',
        'params': {
            'expected': {
                '@type': 'Term',
                '@id': 'GADM-BRA'
            },
            'current': 'oilPalmFruit-world-2010-2025'
        }
    }

    with open(f"{fixtures_folder}/inputs-impactAssessment/invalid-no-impactAssessment.json") as f:
        data = json.load(f)
    assert validate_linked_impactAssessment(data, 'inputs') == {
        'level': 'error',
        'dataPath': '.inputs[0]',
        'message': 'must be linked to a verified country-level Impact Assessment',
        'params': {
            'expected': None,
            'current': ''
        }
    }
