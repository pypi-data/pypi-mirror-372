from unittest.mock import patch
import json
import os

from tests.utils import fixtures_path
from hestia_earth.validation.validators.product import (
    validate_economicValueShare, validate_value_empty, validate_value_0, validate_primary,
    validate_product_ha_functional_unit_ha, validate_product_yield, validate_excreta_product
)


class_path = 'hestia_earth.validation.validators.product'
distribution_class_path = 'hestia_earth.validation.validators.distribution'
fixtures_folder = os.path.join(fixtures_path, 'product')


def test_validate_economicValueShare_valid():
    # no products should be valid
    assert validate_economicValueShare([]) is True

    with open(f"{fixtures_folder}/economicValueShare/valid.json") as f:
        data = json.load(f)
    assert validate_economicValueShare(data.get('nodes')) is True


def test_validate_economicValueShare_invalid():
    with open(f"{fixtures_folder}/economicValueShare/invalid.json") as f:
        data = json.load(f)
    assert validate_economicValueShare(data.get('nodes')) == {
        'level': 'error',
        'dataPath': '.products',
        'message': 'economicValueShare should sum to 100 or less across all products',
        'params': {
            'sum': 110
        }
    }


def test_validate_value_empty_valid():
    # no products should be valid
    assert validate_value_empty([]) is True

    with open(f"{fixtures_folder}/value/valid.json") as f:
        data = json.load(f)
    assert validate_value_empty(data.get('nodes')) is True


def test_validate_value_empty_warning():
    with open(f"{fixtures_folder}/value/value-empty/warning.json") as f:
        data = json.load(f)
    assert validate_value_empty(data.get('nodes')) == {
        'level': 'warning',
        'dataPath': '.products[1]',
        'message': 'may not be 0'
    }


def test_validate_value_0_valid():
    # no products should be valid
    assert validate_value_0([]) is True

    with open(f"{fixtures_folder}/value/valid.json") as f:
        data = json.load(f)
    assert validate_value_0(data.get('nodes')) is True


def test_validate_value_0_error():
    with open(f"{fixtures_folder}/value/value-0/error.json") as f:
        data = json.load(f)
    assert validate_value_0(data.get('nodes')) == [
        {
            'level': 'error',
            'dataPath': '.products[1].value',
            'message': 'economicValueShare must be 0 for product value 0',
            'params': {
                'value': 100,
                'term': {
                    "@type": "Term",
                    "name": "Generic Crop, seed",
                    "@id": "genericCropSeed"
                }
            }
        },
        {
            'level': 'error',
            'dataPath': '.products[1].value',
            'message': 'revenue must be 0 for product value 0',
            'params': {
                'value': 100,
                'term': {
                    "@type": "Term",
                    "name": "Generic Crop, seed",
                    "@id": "genericCropSeed"
                }
            }
        }
    ]


def test_validate_primary_valid():
    # no products should be valid
    assert validate_primary([]) is True

    with open(f"{fixtures_folder}/primary/valid.json") as f:
        data = json.load(f)
    assert validate_primary(data.get('nodes')) is True


def test_validate_primary_error():
    with open(f"{fixtures_folder}/primary/invalid.json") as f:
        data = json.load(f)
    assert validate_primary(data.get('nodes')) == {
        'level': 'error',
        'dataPath': '.products',
        'message': 'only 1 primary product allowed'
    }


def test_validate_product_ha_functional_unit_ha_valid():
    # no products should be valid
    assert validate_product_ha_functional_unit_ha({'products': []}, 'products') is True

    with open(f"{fixtures_folder}/fu_ha/valid.json") as f:
        cycle = json.load(f)
    assert validate_product_ha_functional_unit_ha(cycle, 'products') is True


def test_validate_product_ha_functional_unit_ha_error():
    with open(f"{fixtures_folder}/fu_ha/invalid.json") as f:
        cycle = json.load(f)
    assert validate_product_ha_functional_unit_ha(cycle, 'products') == {
        'level': 'error',
        'dataPath': '.products[0].value',
        'message': 'must be below or equal to 1 for unit in ha',
        'params': {
            'term': {
                '@type': 'Term',
                '@id': 'adzukiBeanVines',
                'units': 'ha'
            }
        }
    }


MU = 8000
SD = 1000


@patch(f"{distribution_class_path}.get_post_yield", return_value=(MU, SD))
def test_validate_product_yield_valid(*args):
    # no products should be valid
    assert validate_product_yield({'products': []}, {}, 'products') is True

    # no value on products should be valid
    with open(f"{fixtures_folder}/yield/no-value.json") as f:
        cycle = json.load(f)
    assert validate_product_yield(cycle, cycle.get('site')) is True


@patch(f"{distribution_class_path}.get_post_yield", return_value=(MU, SD))
def test_validate_product_yield_valid_with_posterior(*args):
    with open(f"{fixtures_folder}/yield/valid.json") as f:
        cycle = json.load(f)
    assert validate_product_yield(cycle, cycle.get('site')) is True


@patch(f"{distribution_class_path}.get_post_yield", return_value=(MU, SD))
def test_validate_product_yield_invalid_with_posterior(*args):
    with open(f"{fixtures_folder}/yield/invalid.json") as f:
        cycle = json.load(f)
    assert validate_product_yield(cycle, cycle.get('site')) == {
        'level': 'warning',
        'dataPath': '.products[0].value',
        'message': 'is outside confidence interval',
        'params': {
            'term': {
                '@type': 'Term',
                'termType': 'crop',
                '@id': 'wheatGrain'
            },
            'country': {
                '@type': 'Term',
                '@id': 'GADM-GBR'
            },
            'outliers': [1000],
            'threshold': 0.95,
            'min': 6040,
            'max': 9960
        }
    }


@patch(f"{distribution_class_path}.get_prior_yield", return_value=(MU, SD))
@patch(f"{distribution_class_path}.get_post_yield", return_value=(None, None))
def test_validate_product_yield_valid_with_prior_no_posterior(*args):
    with open(f"{fixtures_folder}/yield/valid.json") as f:
        cycle = json.load(f)
    assert validate_product_yield(cycle, cycle.get('site')) is True


@patch(f"{distribution_class_path}.get_prior_yield", return_value=(MU, SD))
@patch(f"{distribution_class_path}.get_post_yield", return_value=(None, None))
def test_validate_product_yield_invalid_with_prior_no_posterior(*args):
    with open(f"{fixtures_folder}/yield/invalid.json") as f:
        cycle = json.load(f)
    assert validate_product_yield(cycle, cycle.get('site')) == {
        'level': 'warning',
        'dataPath': '.products[0].value',
        'message': 'is outside confidence interval',
        'params': {
            'term': {
                '@type': 'Term',
                'termType': 'crop',
                '@id': 'wheatGrain'
            },
            'country': {
                '@type': 'Term',
                '@id': 'GADM-GBR'
            },
            'outliers': [1000],
            'threshold': 0.95,
            'min': 6040,
            'max': 9960
        }
    }


@patch(f"{distribution_class_path}.get_prior_yield", return_value=(None, None))
@patch(f"{distribution_class_path}.get_post_yield", return_value=(None, None))
def test_validate_product_yield_valid_no_prior_no_posterior(*args):
    with open(f"{fixtures_folder}/yield/valid.json") as f:
        cycle = json.load(f)
    assert validate_product_yield(cycle, cycle.get('site')) is True


@patch(f"{distribution_class_path}.get_post_yield", return_value=Exception)
def test_validate_product_yield_handle_exception(*args):
    with open(f"{fixtures_folder}/yield/invalid.json") as f:
        cycle = json.load(f)
    assert validate_product_yield(cycle, cycle.get('site')) is True


def test_validate_excreta_product_valid():
    # no products should be valid
    assert validate_excreta_product({}, 'products') is True

    with open(f"{fixtures_folder}/excreta/valid.json") as f:
        data = json.load(f)
    assert validate_excreta_product(data) is True

    with open(f"{fixtures_folder}/excreta/with-system/valid.json") as f:
        data = json.load(f)
    assert validate_excreta_product(data) is True


def test_validate_excreta_product_invalid():
    with open(f"{fixtures_folder}/excreta/invalid.json") as f:
        data = json.load(f)
    assert validate_excreta_product(data) == {
        'level': 'error',
        'dataPath': '.products[1].term.@id',
        'message': 'is not an allowed excreta product',
        'params': {
            'current': 'excretaCamelsKgN',
            'expected': ['excretaPoultryKgN']
        }
    }

    with open(f"{fixtures_folder}/excreta/with-system/invalid.json") as f:
        data = json.load(f)
    assert validate_excreta_product(data) == {
        'level': 'error',
        'dataPath': '.products[1].term.@id',
        'message': 'is not an allowed excreta product',
        'params': {
            'current': 'excretaBeefCattleExceptFeedlotFedKgN',
            'expected': ['excretaBeefCattleFeedlotFedKgN']
        }
    }


def test_validate_excreta_product_warning():
    with open(f"{fixtures_folder}/excreta/warning.json") as f:
        data = json.load(f)
    assert validate_excreta_product(data) == {
        'level': 'warning',
        'dataPath': '.products[0]',
        'message': 'should add an excreta product',
        'params': {
            'expected': ['excretaPoultryKgMass', 'excretaPoultryKgN', 'excretaPoultryKgVs']
        }
    }

    with open(f"{fixtures_folder}/excreta/with-system/warning.json") as f:
        data = json.load(f)
    assert validate_excreta_product(data) == {
        'level': 'warning',
        'dataPath': '.products[0]',
        'message': 'should add an excreta product',
        'params': {
            'expected': [
                'excretaBeefCattleFeedlotFedKgMass',
                'excretaBeefCattleFeedlotFedKgN',
                'excretaBeefCattleFeedlotFedKgVs'
            ]
        }
    }
