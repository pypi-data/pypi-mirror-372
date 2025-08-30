import os
import json
from unittest.mock import patch

from tests.utils import MODEL_TERM_IDS, fixtures_path, fake_get_terms
from hestia_earth.validation.validators.indicator import (
    validate_characterisedIndicator_model,
    validate_landTransformation,
    validate_inonising_compounds_waste
)

class_path = 'hestia_earth.validation.validators.indicator'
fixtures_folder = os.path.join(fixtures_path, 'indicator')


@patch(f"{class_path}.get_terms", side_effect=fake_get_terms)
def test_validate_characterisedIndicator_model_valid(*args):
    # no infrastructure should be valid
    assert validate_characterisedIndicator_model({}, 'impacts') is True

    with open(f"{fixtures_folder}/characterisedIndicator-methodModel/valid.json") as f:
        data = json.load(f)
    assert validate_characterisedIndicator_model(data, 'impacts') is True


@patch(f"{class_path}.get_terms", side_effect=fake_get_terms)
def test_validate_characterisedIndicator_model_invalid(*args):
    with open(f"{fixtures_folder}/characterisedIndicator-methodModel/invalid.json") as f:
        data = json.load(f)
    assert validate_characterisedIndicator_model(data, 'impacts') == {
        'level': 'error',
        'dataPath': '.impacts[0].methodModel.@id',
        'message': 'is not allowed for this characterisedIndicator',
        'params': {
            'term': {
                '@type': 'Term',
                '@id': 'gwp20'
            },
            'model': {
                '@type': 'Term',
                '@id': 'ipcc2013'
            },
            'allowedValues': MODEL_TERM_IDS
        }
    }


@patch(f"{class_path}.get_terms", side_effect=fake_get_terms)
def test_validate_landTransformation_valid(*args):
    # no infrastructure should be valid
    assert validate_landTransformation({}) is True

    with open(f"{fixtures_folder}/landTransformation/valid.json") as f:
        data = json.load(f)
    assert validate_landTransformation({'emissionsResourceUse': data['nodes']}, 'emissionsResourceUse') is True

    with open(f"{fixtures_folder}/landTransformation/valid-grouped.json") as f:
        data = json.load(f)
    assert validate_landTransformation(data, 'emissionsResourceUse') is True


@patch(f"{class_path}.get_terms", side_effect=fake_get_terms)
def test_validate_landTransformation_invalid(*args):
    with open(f"{fixtures_folder}/landTransformation/invalid.json") as f:
        data = json.load(f)
    assert validate_landTransformation({'emissionsResourceUse': data['nodes']}, 'emissionsResourceUse') == {
        'level': 'error',
        'dataPath': '.emissionsResourceUse[1].value',
        'message': 'must be less than or equal to land occupation',
        'params': {
            'current': 0.2,
            'max': 0.1
        }
    }

    with open(f"{fixtures_folder}/landTransformation/invalid-grouped.json") as f:
        data = json.load(f)
    assert validate_landTransformation(data, 'emissionsResourceUse') == [
        {
            'level': 'error',
            'dataPath': '.emissionsResourceUse[3].value',
            'message': 'must be less than or equal to land occupation',
            'params': {
                'current': 0.1,
                'max': 0.01
            }
        },
        {
            'level': 'error',
            'dataPath': '.emissionsResourceUse[6].value',
            'message': 'must be less than or equal to land occupation',
            'params': {
                'current': 2,
                'max': 1
            }
        }
    ]


@patch(f"{class_path}.get_terms", side_effect=fake_get_terms)
def test_validate_inonising_compounds_waste_valid(*args):
    # no infrastructure should be valid
    assert validate_inonising_compounds_waste({}) is True

    with open(f"{fixtures_folder}/ionisingCompounds/valid.json") as f:
        data = json.load(f)
    assert validate_inonising_compounds_waste({'emissionsResourceUse': data['nodes']}, 'emissionsResourceUse') is True


@patch(f"{class_path}.get_terms", side_effect=fake_get_terms)
def test_validate_inonising_compounds_waste_invalid(*args):
    with open(f"{fixtures_folder}/ionisingCompounds/invalid.json") as f:
        data = json.load(f)
    assert validate_inonising_compounds_waste({'emissionsResourceUse': data['nodes']}, 'emissionsResourceUse') == {
        'level': 'error',
        'dataPath': '.emissionsResourceUse[0].key.termType',
        'message': 'should be equal to one of the allowed values',
        'params': {
            'allowedValues': ['waste']
        }
    }
