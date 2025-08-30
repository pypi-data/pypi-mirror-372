import json
from unittest.mock import patch

from tests.utils import fixtures_path
from hestia_earth.validation.validators.transformation import (
    validate_previous_transformation,
    validate_transformation_excretaManagement,
    validate_linked_emission,
    validate_excreta_inputs_products
)

class_path = 'hestia_earth.validation.validators.transformation'
fixtures_folder = f"{fixtures_path}/transformation"


def test_validate_previous_transformation_valid():
    # no transformations should be valid
    assert validate_previous_transformation({}, 'transformations') is True

    with open(f"{fixtures_folder}/previousTransformationId/valid.json") as f:
        cycle = json.load(f)
    assert validate_previous_transformation(cycle) is True


def test_validate_previous_transformation_invalid():
    with open(f"{fixtures_folder}/previousTransformationId/invalid-wrong-order.json") as f:
        cycle = json.load(f)
    assert validate_previous_transformation(cycle) == {
        'level': 'error',
        'dataPath': '.transformations[1].previousTransformationId',
        'message': 'must point to a previous transformation in the list'
    }

    with open(f"{fixtures_folder}/previousTransformationId/invalid-no-previous.json") as f:
        cycle = json.load(f)
    assert validate_previous_transformation(cycle) == {
        'level': 'error',
        'dataPath': '.transformations[1].previousTransformationId',
        'message': 'must point to a previous transformation in the list'
    }

    with open(f"{fixtures_folder}/previousTransformationId/invalid-product-input.json") as f:
        cycle = json.load(f)
    assert validate_previous_transformation(cycle) == {
        'level': 'error',
        'dataPath': '.transformations[1].inputs[0].value',
        'message': 'must be equal to previous product multiplied by the share'
    }

    with open(f"{fixtures_folder}/previousTransformationId/invalid-previous-input.json") as f:
        cycle = json.load(f)
    assert validate_previous_transformation(cycle) == [
        {
            'level': 'error',
            'dataPath': '.transformations[0]',
            'message': 'at least one Input must be a Product of the Cycle'
        },
        {
            'level': 'error',
            'dataPath': '.transformations[1]',
            'message': 'at least one Input must be a Product of the previous Transformation'
        }
    ]


def test_validate_transformation_excretaManagement_valid():
    # no transformations should be valid
    assert validate_transformation_excretaManagement({}, 'transformations')

    with open(f"{fixtures_folder}/excretaManagement/valid.json") as f:
        cycle = json.load(f)
    assert validate_transformation_excretaManagement(cycle) is True


def test_validate_transformation_excretaManagement_invalid():
    with open(f"{fixtures_folder}/excretaManagement/invalid.json") as f:
        cycle = json.load(f)
    assert validate_transformation_excretaManagement(cycle) == {
        'level': 'error',
        'dataPath': '.transformations[0].practices',
        'message': 'an excreta input is required when using an excretaManagement practice'
    }


def test_validate_linked_emission_valid():
    # no emissions should be valid
    assert validate_linked_emission({}, 'transformations') is True

    with open(f"{fixtures_folder}/linked-emission/valid.json") as f:
        data = json.load(f)
    assert validate_linked_emission(data, 'transformations') is True


def test_validate_linked_emission_invalid():
    with open(f"{fixtures_folder}/linked-emission/invalid.json") as f:
        data = json.load(f)
    assert validate_linked_emission(data, 'transformations') == {
        'level': 'warning',
        'dataPath': '.transformations[0].emissions[0]',
        'message': 'should be linked to an emission in the Cycle',
        'params': {
            'term': {
                '@type': 'Term',
                '@id': 'ch4ToAirEntericFermentation',
                'termType': 'emission'
            }
        }
    }


def test_validate_excreta_inputs_products_valid():
    # no transformations should be valid
    assert validate_excreta_inputs_products([]) is True

    with open(f"{fixtures_folder}/inputs-products/valid.json") as f:
        data = json.load(f)
    assert validate_excreta_inputs_products(data) is True


def fake_download_excreta(term_id: str, *args):
    return {
        'processedExcretaKgVs': {},
        'excretaBeefCattleExceptFeedlotFedKgMass': {
            'subClassOf': [{}]
        }
    }[term_id]


@patch(f"{class_path}.download_hestia", side_effect=fake_download_excreta)
def test_validate_excreta_inputs_products_invalid(*args):
    with open(f"{fixtures_folder}/inputs-products/invalid.json") as f:
        data = json.load(f)
    assert validate_excreta_inputs_products(data) == {
        'level': 'error',
        'dataPath': '.transformations[0].products[1]',
        'message': 'must be included as an Input',
        'params': {
            'term': {
                '@type': 'Term',
                '@id': 'excretaBeefCattleExceptFeedlotFedKgMass',
                'termType': 'excreta'
            },
            'expected': ['excretaDairyCattle']
        }
    }
