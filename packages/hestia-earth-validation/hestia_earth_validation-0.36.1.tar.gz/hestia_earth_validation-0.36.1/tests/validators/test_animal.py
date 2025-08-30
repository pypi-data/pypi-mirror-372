import os
import json

from tests.utils import fixtures_path
from hestia_earth.validation.validators.animal import (
    validate_has_animals,
    validate_duplicated_feed_inputs,
    validate_has_pregnancyRateTotal
)


fixtures_folder = os.path.join(fixtures_path, 'animal')
class_path = 'hestia_earth.validation.validators.animal'


def test_validate_has_animals_valid():
    # no products should be valid
    assert validate_has_animals({}) is True

    with open(f"{fixtures_folder}/required/valid.json") as f:
        cycle = json.load(f)
    assert validate_has_animals(cycle) is True


def test_validate_has_animals_invalid():
    with open(f"{fixtures_folder}/required/invalid.json") as f:
        cycle = json.load(f)
    assert validate_has_animals(cycle) == {
        'level': 'warning',
        'dataPath': '',
        'message': 'should specify the herd composition'
    }


def test_validate_duplicated_feed_inputs_valid():
    # no products should be valid
    assert validate_duplicated_feed_inputs({}) is True

    with open(f"{fixtures_folder}/duplicated-input-cycle/valid.json") as f:
        cycle = json.load(f)
    assert validate_duplicated_feed_inputs(cycle) is True


def test_validate_duplicated_feed_inputs_invalid():
    with open(f"{fixtures_folder}/duplicated-input-cycle/invalid.json") as f:
        cycle = json.load(f)
    assert validate_duplicated_feed_inputs(cycle) == {
        'level': 'error',
        'dataPath': '.animals[0].inputs[1]',
        'message': 'must not add the feed input to the Cycle as well',
        'params': {
            'term': {
                '@type': 'Term',
                '@id': 'wheatGrain'
            }
        }
    }


def test_validate_has_pregnancyRateTotal_valid():
    # no animals should be valid
    assert validate_has_pregnancyRateTotal({}) is True

    with open(f"{fixtures_folder}/pregnancyRateTotal/valid.json") as f:
        cycle = json.load(f)
    assert validate_has_pregnancyRateTotal(cycle) is True


def test_validate_has_pregnancyRateTotal_invalid():
    with open(f"{fixtures_folder}/pregnancyRateTotal/invalid.json") as f:
        cycle = json.load(f)
    assert validate_has_pregnancyRateTotal(cycle) == {
        'level': 'warning',
        'dataPath': '.animals[0].properties',
        'message': 'should specify the pregnancy rate',
        'params': {
            'expected': 'pregnancyRateTotal'
        }
    }
