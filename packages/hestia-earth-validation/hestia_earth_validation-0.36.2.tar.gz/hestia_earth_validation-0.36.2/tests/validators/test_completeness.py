import os
import json
from unittest.mock import patch
from hestia_earth.schema import SiteSiteType, TermTermType, CompletenessField

from tests.utils import FUEL_TERM_IDS, fixtures_path, fake_get_terms
from hestia_earth.validation.validators.completeness import (
    validate_completeness,
    _validate_all_values,
    _validate_cropland,
    _validate_material,
    _validate_animalPopulation,
    _validate_freshForage,
    _validate_ingredient,
    validate_completeness_blank_nodes
)

fixtures_folder = os.path.join(fixtures_path, 'completeness')
class_path = 'hestia_earth.validation.validators.completeness'


@patch(f"{class_path}.get_terms", side_effect=fake_get_terms)
def test_validate_completeness_valid(*args):
    with open(f"{fixtures_folder}/valid.json") as f:
        data = json.load(f)
    assert validate_completeness({'completeness': data}) is True


def test_validate_all_values_valid():
    with open(f"{fixtures_folder}/valid.json") as f:
        data = json.load(f)
    assert _validate_all_values(data) is True


def test_validate_all_values_warning():
    with open(f"{fixtures_folder}/all-values/warning.json") as f:
        data = json.load(f)
    assert _validate_all_values(data) == {
        'level': 'warning',
        'dataPath': '.completeness',
        'message': 'may not all be set to false'
    }


def test_validate_cropland_valid():
    with open(f"{fixtures_folder}/cropland/site.json") as f:
        site = json.load(f)
    with open(f"{fixtures_folder}/cropland/valid.json") as f:
        data = json.load(f)
    assert _validate_cropland(data, site) is True

    # also works if siteType is not cropland
    site['siteType'] = SiteSiteType.LAKE.value
    data[TermTermType.EXCRETA.value] = False
    assert _validate_cropland(data, site) is True


def test_validate_cropland_warning():
    with open(f"{fixtures_folder}/cropland/site.json") as f:
        site = json.load(f)
    with open(f"{fixtures_folder}/cropland/warning.json") as f:
        data = json.load(f)
    assert _validate_cropland(data, site) == [
        {
            'level': 'warning',
            'dataPath': '.completeness.animalFeed',
            'message': 'should be true for site of type cropland'
        },
        {
            'level': 'warning',
            'dataPath': '.completeness.excreta',
            'message': 'should be true for site of type cropland'
        }
    ]


@patch(f"{class_path}.get_terms", side_effect=fake_get_terms)
def test_validate_material_valid(*args):
    with open(f"{fixtures_folder}/{CompletenessField.MATERIAL.value}/valid-incomplete.json") as f:
        data = json.load(f)
    assert _validate_material(data) is True

    with open(f"{fixtures_folder}/{CompletenessField.MATERIAL.value}/valid-no-fuel.json") as f:
        data = json.load(f)
    assert _validate_material(data) is True

    with open(f"{fixtures_folder}/{CompletenessField.MATERIAL.value}/valid-fuel-material.json") as f:
        data = json.load(f)
    assert _validate_material(data) is True


@patch(f"{class_path}.get_terms", side_effect=fake_get_terms)
def test_validate_material_error(*args):
    with open(f"{fixtures_folder}/{CompletenessField.MATERIAL.value}/error.json") as f:
        data = json.load(f)
    assert _validate_material(data) == {
        'level': 'error',
        'dataPath': f".completeness.{CompletenessField.MATERIAL.value}",
        'message': 'must be set to false when specifying fuel use',
        'params': {
            'allowedValues': FUEL_TERM_IDS
        }
    }


def test_validate_animalPopulation_valid(*args):
    with open(f"{fixtures_folder}/{CompletenessField.ANIMALPOPULATION.value}/valid-incomplete.json") as f:
        data = json.load(f)
    assert _validate_animalPopulation(data) is True

    with open(f"{fixtures_folder}/{CompletenessField.ANIMALPOPULATION.value}/valid-no-liveAnimals.json") as f:
        data = json.load(f)
    assert _validate_animalPopulation(data) is True

    with open(f"{fixtures_folder}/{CompletenessField.ANIMALPOPULATION.value}/valid-animals.json") as f:
        data = json.load(f)
    assert _validate_animalPopulation(data) is True


def test_validate_animalPopulation_error(*args):
    with open(f"{fixtures_folder}/{CompletenessField.ANIMALPOPULATION.value}/invalid.json") as f:
        data = json.load(f)
    assert _validate_animalPopulation(data) == {
        'level': 'error',
        'dataPath': f".completeness.{CompletenessField.ANIMALPOPULATION.value}",
        'message': 'animal population must not be complete'
    }


@patch(f"{class_path}.get_terms", side_effect=fake_get_terms)
def test_validate_freshForage_valid(*args):
    with open(f"{fixtures_folder}/{CompletenessField.FRESHFORAGE.value}/valid-animals.json") as f:
        data = json.load(f)
    assert _validate_freshForage(data, data.get('site')) is True

    with open(f"{fixtures_folder}/{CompletenessField.FRESHFORAGE.value}/valid-animal-inputs.json") as f:
        data = json.load(f)
    assert _validate_freshForage(data, data.get('site')) is True

    with open(f"{fixtures_folder}/{CompletenessField.FRESHFORAGE.value}/valid-products.json") as f:
        data = json.load(f)
    assert _validate_freshForage(data, data.get('site')) is True

    with open(f"{fixtures_folder}/{CompletenessField.FRESHFORAGE.value}/valid-not-liveAnimal.json") as f:
        data = json.load(f)
    assert _validate_freshForage(data, data.get('site')) is True

    with open(f"{fixtures_folder}/{CompletenessField.FRESHFORAGE.value}/valid-not-grazing-liveAnimal.json") as f:
        data = json.load(f)
    assert _validate_freshForage(data, data.get('site')) is True


@patch(f"{class_path}.get_terms", side_effect=fake_get_terms)
def test_validate_freshForage_error(*args):
    with open(f"{fixtures_folder}/{CompletenessField.FRESHFORAGE.value}/error-animals.json") as f:
        data = json.load(f)
    assert _validate_freshForage(data, data.get('site')) == {
        'level': 'error',
        'dataPath': f".completeness.{CompletenessField.FRESHFORAGE.value}",
        'message': 'must have inputs representing the forage when set to true',
        'params': {
            'siteType': 'permanent pasture'
        }
    }

    with open(f"{fixtures_folder}/{CompletenessField.FRESHFORAGE.value}/error-products.json") as f:
        data = json.load(f)
    assert _validate_freshForage(data, data.get('site')) == {
        'level': 'error',
        'dataPath': f".completeness.{CompletenessField.FRESHFORAGE.value}",
        'message': 'must have inputs representing the forage when set to true',
        'params': {
            'siteType': 'permanent pasture'
        }
    }


@patch(f"{class_path}.get_terms", side_effect=fake_get_terms)
def test_validate_ingredient_valid(*args):
    with open(f"{fixtures_folder}/{CompletenessField.INGREDIENT.value}/valid.json") as f:
        data = json.load(f)
    assert _validate_ingredient(data, data.get('site')) is True

    with open(f"{fixtures_folder}/{CompletenessField.INGREDIENT.value}/valid-agri-food-processor-complete.json") as f:
        data = json.load(f)
    assert _validate_ingredient(data, data.get('site')) is True

    with open(f"{fixtures_folder}/{CompletenessField.INGREDIENT.value}/valid-agri-food-processor-incomplete.json") as f:
        data = json.load(f)
    assert _validate_ingredient(data, data.get('site')) is True


@patch(f"{class_path}.get_terms", side_effect=fake_get_terms)
def test_validate_ingredient_error(*args):
    with open(f"{fixtures_folder}/{CompletenessField.INGREDIENT.value}/invalid.json") as f:
        data = json.load(f)
    assert _validate_ingredient(data, data.get('site')) == {
        'level': 'error',
        'dataPath': f".completeness.{CompletenessField.INGREDIENT.value}",
        'message': 'ingredients should be complete',
        'params': {
            'siteType': 'cropland'
        }
    }

    with open(f"{fixtures_folder}/{CompletenessField.INGREDIENT.value}/invalid-agri-food-processor.json") as f:
        data = json.load(f)
    assert _validate_ingredient(data, data.get('site')) == {
        'level': 'error',
        'dataPath': f".completeness.{CompletenessField.INGREDIENT.value}",
        'message': 'must have inputs to represent ingredients',
        'params': {
            'siteType': 'agri-food processor'
        }
    }


def test_validate_completeness_blank_nodes_valid():
    with open(f"{fixtures_folder}/blank-nodes/valid.json") as f:
        data = json.load(f)
    assert validate_completeness_blank_nodes(data) is True


def test_validate_completeness_blank_nodes_invalid():
    with open(f"{fixtures_folder}/blank-nodes/invalid.json") as f:
        data = json.load(f)
    assert validate_completeness_blank_nodes(data) == [
        {
            'dataPath': '.animals[0]',
            'level': 'error',
            'message': 'must not be blank if complete',
            'params': {
                'term': {
                    '@id': 'chicken',
                    '@type': 'Term',
                    'termType': 'liveAnimal',
                },
                'expected': 'animalPopulation'
            }
        },
        {
            'dataPath': '.inputs[2]',
            'level': 'error',
            'message': 'must not be blank if complete',
            'params': {
                'term': {
                    '@id': 'diesel',
                    '@type': 'Term',
                    'termType': 'fuel',
                },
                'expected': 'electricityFuel'
            }
        },
        {
            'dataPath': '.products[0]',
            'level': 'error',
            'message': 'must not be blank if complete',
            'params': {
                'term': {
                    '@id': 'aboveGroundCropResidueTotal',
                    '@type': 'Term',
                    'termType': 'cropResidue',
                },
                'expected': 'cropResidue'
            }
        },
        {
            'dataPath': '.products[1]',
            'level': 'error',
            'message': 'must not be blank if complete',
            'params': {
                'term': {
                    '@id': 'aboveGroundCropResidueBurnt',
                    '@type': 'Term',
                    'termType': 'cropResidue',
                },
                'expected': 'cropResidue'
            }
        },
        {
            'dataPath': '.products[2]',
            'level': 'error',
            'message': 'must not be blank if complete',
            'params': {
                'term': {
                    '@id': 'aboveGroundCropResidueLeftOnField',
                    '@type': 'Term',
                    'termType': 'cropResidue',
                },
                'expected': 'cropResidue'
            }
        }
    ]
