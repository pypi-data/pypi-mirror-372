import os
import json
from unittest.mock import patch

from tests.utils import fixtures_path
from hestia_earth.validation.utils import _group_nodes
from hestia_earth.validation.validators.input import (
    validate_must_include_id,
    validate_input_country,
    validate_related_impacts,
    validate_input_distribution_value,
    validate_animalFeed_requires_isAnimalFeed,
    validate_saplings,
    validate_input_is_product
)

class_path = 'hestia_earth.validation.validators.input'
distribution_class_path = 'hestia_earth.validation.validators.distribution'
fixtures_folder = os.path.join(fixtures_path, 'input')


def test_validate_must_include_id_valid():
    # no inputs should be valid
    assert validate_must_include_id([]) is True

    with open(f"{fixtures_folder}/mustIncludeId/valid.json") as f:
        data = json.load(f)
    assert validate_must_include_id(data.get('nodes')) is True

    with open(f"{fixtures_folder}/mustIncludeId/valid-multiple-ids.json") as f:
        data = json.load(f)
    assert validate_must_include_id(data.get('nodes')) is True


def test_validate_must_include_id_invalid():
    with open(f"{fixtures_folder}/mustIncludeId/invalid.json") as f:
        data = json.load(f)
    assert validate_must_include_id(data.get('nodes')) == {
        'level': 'warning',
        'dataPath': '.inputs[0]',
        'message': 'should add missing inputs: potassiumNitrateKgK2O'
    }


def test_validate_input_country_valid():
    # no inputs should be valid
    assert validate_input_country({}) is True

    with open(f"{fixtures_folder}/country/valid.json") as f:
        cycle = json.load(f)
    assert validate_input_country(cycle, 'inputs') is True


def test_validate_input_country_invalid():
    with open(f"{fixtures_folder}/country/invalid.json") as f:
        cycle = json.load(f)
    assert validate_input_country(cycle, 'inputs') == {
        'level': 'error',
        'dataPath': '.inputs[1].country',
        'message': 'must be a country'
    }


def test_validate_related_impacts_valid():
    # no inputs should be valid
    assert validate_related_impacts({}, 'inputs') is True

    with open(f"{fixtures_folder}/impactAssessment/valid.json") as f:
        nodes = json.load(f).get('nodes')
    assert validate_related_impacts(nodes[0], 'inputs', _group_nodes(nodes)) is True


def test_validate_related_impacts_invalid():
    with open(f"{fixtures_folder}/impactAssessment/invalid.json") as f:
        nodes = json.load(f).get('nodes')
    assert validate_related_impacts(nodes[0], 'inputs', _group_nodes(nodes)) == {
        'level': 'error',
        'dataPath': '.inputs[1].impactAssessment',
        'message': 'can not be linked to the same Cycle'
    }


def test_validate_input_distribution_value_incomplete_valid():
    with open(f"{fixtures_folder}/distribution/incomplete/valid.json") as f:
        cycle = json.load(f)
    assert validate_input_distribution_value(cycle, cycle.get('site')) is True


def fake_get_post_fert(_country_id, product_id, fert_id):
    return {
        'inorganicPhosphorusFertiliserUnspecifiedKgP2O5': (44, 4),
        'inorganicPotassiumFertiliserUnspecifiedKgK2O': (84, 8),
        'inorganicNitrogenFertiliserUnspecifiedKgN': (166, 12),
        'ammoniumSulphateKgN': (166, 12),
        'ureaKgN': (166, 12),
    }[fert_id]


fake_post_pest_value = (4, 12)
fake_post_irri_value = (400, 120)


@patch(f"{distribution_class_path}.get_post_fert", side_effect=fake_get_post_fert)
@patch(f"{distribution_class_path}.get_post_pest", return_value=fake_post_pest_value)
@patch(f"{distribution_class_path}.get_post_irri", return_value=fake_post_irri_value)
def test_validate_input_distribution_value_complete_invalid(*args):
    with open(f"{fixtures_folder}/distribution/complete/invalid.json") as f:
        cycle = json.load(f)
    assert validate_input_distribution_value(cycle, cycle.get('site'), 'inputs') == [
        {
            'level': 'warning',
            'dataPath': '.inputs[0].value',
            'message': 'is outside confidence interval',
            'params': {
                'term': {
                    '@type': 'Term',
                    '@id': 'ureaKgN',
                    'termType': 'inorganicFertiliser',
                    'units': 'kg N'
                },
                'group': 'Nitrogen (kg N)',
                'country': {
                    '@type': 'Term',
                    '@id': 'GADM-GBR'
                },
                'outliers': [113],
                'threshold': 0.95,
                'min': 142.48,
                'max': 189.52
            }
        },
        {
            'level': 'warning',
            'dataPath': '.inputs[1].value',
            'message': 'is outside confidence interval',
            'params': {
                'term': {
                    '@type': 'Term',
                    '@id': 'ammoniumSulphateKgN',
                    'termType': 'inorganicFertiliser',
                    'units': 'kg N'
                },
                'group': 'Nitrogen (kg N)',
                'country': {
                    '@type': 'Term',
                    '@id': 'GADM-GBR'
                },
                'outliers': [113],
                'threshold': 0.95,
                'min': 142.48,
                'max': 189.52
            }
        },
        {
            'level': 'warning',
            'dataPath': '.inputs[2].value',
            'message': 'is outside confidence interval',
            'params': {
                'term': {
                    '@type': 'Term',
                    '@id': 'inorganicNitrogenFertiliserUnspecifiedKgN',
                    'termType': 'inorganicFertiliser',
                    'units': 'kg N'
                },
                'group': 'Nitrogen (kg N)',
                'country': {
                    '@type': 'Term',
                    '@id': 'GADM-GBR'
                },
                'outliers': [113],
                'threshold': 0.95,
                'min': 142.48,
                'max': 189.52
            }
        },
        {
            'level': 'warning',
            'dataPath': '.inputs[3].value',
            'message': 'is outside confidence interval',
            'params': {
                'term': {
                    '@type': 'Term',
                    '@id': 'inorganicPotassiumFertiliserUnspecifiedKgK2O',
                    'termType': 'inorganicFertiliser',
                    'units': 'kg K2O'
                },
                'group': 'Potassium (kg K2O)',
                'country': {
                    '@type': 'Term',
                    '@id': 'GADM-GBR'
                },
                'outliers': [217],
                'threshold': 0.95,
                'min': 68.32,
                'max': 99.68
            }
        },
        {
            'level': 'warning',
            'dataPath': '.inputs[4].value',
            'message': 'is outside confidence interval',
            'params': {
                'term': {
                    '@type': 'Term',
                    '@id': 'inorganicPhosphorusFertiliserUnspecifiedKgP2O5',
                    'termType': 'inorganicFertiliser',
                    'units': 'kg P2O5'
                },
                'group': 'Phosphorus (kg P2O5)',
                'country': {
                    '@type': 'Term',
                    '@id': 'GADM-GBR'
                },
                'outliers': [183],
                'threshold': 0.95,
                'min': 36.16,
                'max': 51.84
            }
        },
        {
            'level': 'warning',
            'dataPath': '.inputs[5].value',
            'message': 'is outside confidence interval',
            'params': {
                'term': {
                    '@type': 'Term',
                    '@id': 'CAS-110-17-8',
                    'termType': 'pesticideAI',
                    'units': 'kg active ingredient'
                },
                'group': 'pesticideUnspecifiedAi',
                'country': {
                    '@type': 'Term',
                    '@id': 'GADM-GBR'
                },
                'outliers': [439.64],
                'threshold': 0.95,
                'min': 0,
                'max': 27.52
            }
        },
        {
            'level': 'warning',
            'dataPath': '.inputs[6].value',
            'message': 'is outside confidence interval',
            'params': {
                'term': {
                    '@type': 'Term',
                    '@id': 'CAS-498-15-7',
                    'termType': 'pesticideAI',
                    'units': 'kg active ingredient'
                },
                'group': 'pesticideUnspecifiedAi',
                'country': {
                    '@type': 'Term',
                    '@id': 'GADM-GBR'
                },
                'outliers': [439.64],
                'threshold': 0.95,
                'min': 0,
                'max': 27.52
            }
        },
        {
            'level': 'warning',
            'dataPath': '.inputs[7].value',
            'message': 'is outside confidence interval',
            'params': {
                'term': {
                    '@type': 'Term',
                    '@id': '008MesoFertiliser',
                    'termType': 'pesticideBrandName',
                    'units': 'kg'
                },
                'group': 'pesticideUnspecifiedAi',
                'country': {'@type': 'Term', '@id': 'GADM-GBR'},
                'outliers': [439.64],
                'threshold': 0.95,
                'min': 0,
                'max': 27.52
            }
        },
        {
            'level': 'warning',
            'dataPath': '.inputs[8].value',
            'message': 'is outside confidence interval',
            'params': {
                'term': {
                    '@type': 'Term',
                    '@id': 'waterMarine',
                    'termType': 'water',
                    'units': 'm3'
                },
                'group': 'waterSourceUnspecified',
                'country': {'@type': 'Term', '@id': 'GADM-GBR'},
                'outliers': [2800],
                'threshold': 0.95,
                'min': 164.8,
                'max': 635.2
            }
        },
        {
            'level': 'warning',
            'dataPath': '.inputs[9].value',
            'message': 'is outside confidence interval',
            'params': {
                'term': {
                    '@type': 'Term',
                    '@id': 'waterRiverStream',
                    'termType': 'water',
                    'units': 'm3'
                },
                'group': 'waterSourceUnspecified',
                'country': {'@type': 'Term', '@id': 'GADM-GBR'},
                'outliers': [2800],
                'threshold': 0.95,
                'min': 164.8,
                'max': 635.2
            }
        }
    ]


@patch(f"{distribution_class_path}.get_prior_fert", side_effect=fake_get_post_fert)
@patch(f"{distribution_class_path}.get_post_fert", return_value=(None, None))
@patch(f"{distribution_class_path}.get_prior_pest", return_value=fake_post_pest_value)
@patch(f"{distribution_class_path}.get_post_pest", return_value=(None, None))
@patch(f"{distribution_class_path}.get_prior_irri", return_value=fake_post_irri_value)
@patch(f"{distribution_class_path}.get_post_irri", return_value=(None, None))
def test_validate_input_distribution_value_complete_valid_with_prior_no_posterior(*args):
    with open(f"{fixtures_folder}/distribution/complete/valid.json") as f:
        cycle = json.load(f)
    assert validate_input_distribution_value(cycle, cycle.get('site')) is True


@patch(f"{distribution_class_path}.get_prior_fert", return_value=(None, None))
@patch(f"{distribution_class_path}.get_post_fert", return_value=(None, None))
@patch(f"{distribution_class_path}.get_prior_pest", return_value=(None, None))
@patch(f"{distribution_class_path}.get_post_pest", return_value=(None, None))
@patch(f"{distribution_class_path}.get_prior_irri", return_value=(None, None))
@patch(f"{distribution_class_path}.get_post_irri", return_value=(None, None))
def test_validate_input_distribution_value_complete_valid_no_prior_no_posterior(*args):
    with open(f"{fixtures_folder}/distribution/complete/valid.json") as f:
        cycle = json.load(f)
    assert validate_input_distribution_value(cycle, cycle.get('site')) is True


@patch(f"{distribution_class_path}.get_post_fert", return_value=Exception)
@patch(f"{distribution_class_path}.get_post_pest", return_value=Exception)
@patch(f"{distribution_class_path}.get_post_irri", return_value=Exception)
def test_validate_input_distribution_value_handle_exception(*args):
    with open(f"{fixtures_folder}/distribution/complete/valid.json") as f:
        cycle = json.load(f)
    assert validate_input_distribution_value(cycle, cycle.get('site')) is True


def test_validate_input_distribution_value_non_cropland(*args):
    with open(f"{fixtures_folder}/distribution/animalHousing.json") as f:
        cycle = json.load(f)
    assert validate_input_distribution_value(cycle, cycle.get('site')) is True


def test_validate_animalFeed_requires_isAnimalFeed_valid():
    # no inputs should be valid
    assert validate_animalFeed_requires_isAnimalFeed({}, {}) is True

    with open(f"{fixtures_folder}/animalFeed-fate/valid.json") as f:
        cycle = json.load(f)
    assert validate_animalFeed_requires_isAnimalFeed(cycle, cycle.get('site')) is True


def test_validate_animalFeed_requires_isAnimalFeed_invalid():
    with open(f"{fixtures_folder}/animalFeed-fate/invalid.json") as f:
        cycle = json.load(f)
    assert validate_animalFeed_requires_isAnimalFeed(cycle, cycle.get('site')) == [
        {
            'level': 'error',
            'dataPath': '.inputs[0]',
            'message': 'must specify is it an animal feed'
        },
        {
            'level': 'error',
            'dataPath': '.animals[0].inputs[0]',
            'message': 'must specify is it an animal feed'
        }
    ]


def test_validate_saplings_valid():
    # no inputs should be valid
    assert validate_saplings({}) is True

    with open(f"{fixtures_folder}/saplings/valid.json") as f:
        cycle = json.load(f)
    assert validate_saplings(cycle, 'inputs') is True

    with open(f"{fixtures_folder}/saplings/valid-not-plantation.json") as f:
        cycle = json.load(f)
    assert validate_saplings(cycle, 'inputs') is True

    with open(f"{fixtures_folder}/saplings/valid-no-saplings.json") as f:
        cycle = json.load(f)
    assert validate_saplings(cycle, 'inputs') is True


def test_validate_saplings_invalid():
    with open(f"{fixtures_folder}/saplings/invalid.json") as f:
        cycle = json.load(f)
    assert validate_saplings(cycle, 'inputs') == [{
        'level': 'error',
        'dataPath': '.inputs[0].term',
        'message': 'saplings cannot be used as an input here',
        'params': {
            'current': 'saplings',
            'expected': 'saplingsDepreciatedAmountPerCycle'
        }
    }]


def test_validate_input_is_product_valid():
    # no inputs should be valid
    assert validate_input_is_product({}) is True

    with open(f"{fixtures_folder}/input-as-product/valid.json") as f:
        cycle = json.load(f)
    assert validate_input_is_product(cycle, 'inputs') is True


def test_validate_input_is_product_invalid():
    with open(f"{fixtures_folder}/input-as-product/invalid.json") as f:
        cycle = json.load(f)
    assert validate_input_is_product(cycle, 'inputs') == {
        'level': 'error',
        'dataPath': '.inputs[1].term',
        'message': 'must be a product',
        'params': {
            'term': {
                "@id": "nitrogenUptakeWholeCropWeedsAndVolunteers",
                "@type": "Term",
                "termType": "crop"
            }
        }
    }
