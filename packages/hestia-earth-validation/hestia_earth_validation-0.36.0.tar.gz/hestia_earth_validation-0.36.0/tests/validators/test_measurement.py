import os
from unittest.mock import patch
import json
from hestia_earth.schema import SiteSiteType

from tests.utils import fixtures_path
from hestia_earth.validation.validators.measurement import (
    validate_soilTexture, validate_depths, validate_term_unique,
    validate_require_startDate_endDate, validate_with_models, validate_value_length, validate_required_depths,
    validate_water_measurements, validate_water_salinity
)

fixtures_folder = os.path.join(fixtures_path, 'measurement')
class_path = 'hestia_earth.validation.validators.measurement'


def test_validate_soilTexture_invalid_percent():
    with open(f"{fixtures_folder}/soilTexture/percent-invalid.json") as f:
        data = json.load(f)
    assert validate_soilTexture(data.get('nodes')) == [
        {
            'level': 'error',
            'dataPath': '.measurements[0].value',
            'message': 'is outside the allowed range',
            'params': {
                'term': {
                    '@type': 'Term',
                    '@id': 'sandContent',
                    'termType': 'measurement'
                },
                'range': {'min': 86, 'max': 100}
            }
        },
        {
            'level': 'error',
            'dataPath': '.measurements[4].value',
            'message': 'is outside the allowed range',
            'params': {
                'term': {
                    '@type': 'Term',
                    '@id': 'sandContent',
                    'termType': 'measurement'
                },
                'range': {'min': 20, 'max': 45}
            }
        },
        {
            'level': 'error',
            'dataPath': '.measurements[6].value',
            'message': 'is outside the allowed range',
            'params': {
                'term': {
                    '@type': 'Term',
                    '@id': 'clayContent',
                    'termType': 'measurement'
                },
                'range': {'min': 27, 'max': 40}
            }
        }
    ]


def test_validate_soilTexture_valid():
    # no measurements should be valid
    assert validate_soilTexture([]) is True

    # missing value on texture
    with open(f"{fixtures_folder}/soilTexture/missing-texture-value.json") as f:
        data = json.load(f)
    assert validate_soilTexture(data.get('nodes')) is True

    # valid percent
    with open(f"{fixtures_folder}/soilTexture/percent-valid.json") as f:
        data = json.load(f)
    assert validate_soilTexture(data.get('nodes')) is True

    # missing value - cannot validate
    with open(f"{fixtures_folder}/soilTexture/percent-missing-value.json") as f:
        data = json.load(f)
    assert validate_soilTexture(data.get('nodes')) is True


def test_validate_depths_valid():
    # no measurements should be valid
    assert validate_depths([]) is True

    with open(f"{fixtures_folder}/depths/valid.json") as f:
        data = json.load(f)
    assert validate_depths(data.get('nodes')) is True


def test_validate_depths_invalid():
    with open(f"{fixtures_folder}/depths/invalid.json") as f:
        data = json.load(f)
    assert validate_depths(data.get('nodes')) == {
        'level': 'error',
        'dataPath': '.measurements[2].depthLower',
        'message': 'must be greater than or equal to depthUpper'
    }


def test_validate_term_unique_valid():
    # no measurements should be valid
    assert validate_term_unique([]) is True

    with open(f"{fixtures_folder}/unique/valid.json") as f:
        data = json.load(f)
    assert validate_term_unique(data.get('nodes')) is True


def test_validate_term_unique_invalid():
    with open(f"{fixtures_folder}/unique/invalid.json") as f:
        data = json.load(f)
    assert validate_term_unique(data.get('nodes')) == [{
        'level': 'error',
        'dataPath': '.measurements[0].term.name',
        'message': 'must be unique'
    }, {
        'level': 'error',
        'dataPath': '.measurements[1].term.name',
        'message': 'must be unique'
    }]


def test_validate_require_startDate_endDate_valid():
    # no measurements should be valid
    assert validate_require_startDate_endDate({'measurements': []}, 'measurements') is True

    with open(f"{fixtures_folder}/startDate-endDate-required/valid.json") as f:
        data = json.load(f)
    assert validate_require_startDate_endDate(data, 'measurements') is True


def test_validate_require_startDate_endDate_invalid():
    with open(f"{fixtures_folder}/startDate-endDate-required/invalid.json") as f:
        data = json.load(f)
    assert validate_require_startDate_endDate(data, 'measurements') == [{
        'level': 'error',
        'dataPath': '.measurements[0]',
        'message': "should have required property 'startDate'",
        'params': {
            'missingProperty': 'startDate'
        }
    }, {
        'level': 'error',
        'dataPath': '.measurements[0]',
        'message': "should have required property 'endDate'",
        'params': {
            'missingProperty': 'endDate'
        }
    }]


@patch('hestia_earth.models.geospatialDatabase.precipitationAnnual._run', return_value={'value': [1000]})
def test_validate_with_models_valid(*args):
    # no measurements should be valid
    assert validate_with_models({}, 'measurements') is True

    with open(f"{fixtures_folder}/models/valid.json") as f:
        data = json.load(f)
    assert validate_with_models(data, 'measurements') is True


@patch('hestia_earth.models.geospatialDatabase.precipitationAnnual._run', return_value={'value': [1000]})
def test_validate_with_models_warning(*args):
    with open(f"{fixtures_folder}/models/warning.json") as f:
        data = json.load(f)
    assert validate_with_models(data, 'measurements') == {
        'level': 'warning',
        'dataPath': '.measurements[0].value',
        'message': 'the measurement provided might be in error',
        'params': {
            'current': 500,
            'expected': 1000,
            'delta': 50,
            'threshold': 0.25,
            'term': {
                '@id': 'precipitationAnnual',
                '@type': 'Term',
                'termType': 'measurement'
            },
            'model': {}
        }
    }

    # with no value warning must be on blank node
    with open(f"{fixtures_folder}/models/warning-no-value.json") as f:
        data = json.load(f)
    assert validate_with_models(data, 'measurements') == {
        'level': 'warning',
        'dataPath': '.measurements[0]',
        'message': 'the measurement provided might be in error',
        'params': {
            'current': None,
            'expected': 1000,
            'delta': 100,
            'threshold': 0.25,
            'term': {
                '@id': 'precipitationAnnual',
                '@type': 'Term',
                'termType': 'measurement'
            },
            'model': {}
        }
    }


def test_validate_value_length_valid():
    # no measurements should be valid
    assert validate_value_length({}, 'measurements') is True

    with open(f"{fixtures_folder}/value-length/valid.json") as f:
        data = json.load(f)
    assert validate_value_length(data, 'measurements') is True


def test_validate_value_length_invalid():
    with open(f"{fixtures_folder}/value-length/invalid.json") as f:
        data = json.load(f)
    assert validate_value_length(data, 'measurements') == {
        'level': 'error',
        'dataPath': '.measurements[1].value',
        'message': 'must not contain more than 1 value'
    }


def test_validate_required_depths_valid():
    # no measurements should be valid
    assert validate_required_depths({}, 'measurements') is True

    with open(f"{fixtures_folder}/required-depths/valid.json") as f:
        data = json.load(f)
    assert validate_required_depths(data, 'measurements') is True


def test_validate_required_depths_warning():
    with open(f"{fixtures_folder}/required-depths/warning.json") as f:
        data = json.load(f)
    assert validate_required_depths(data, 'measurements') == {
        'level': 'warning',
        'dataPath': '.measurements[0]',
        'message': 'should set both depthUpper and depthLower'
    }


def test_validate_required_depths_error():
    with open(f"{fixtures_folder}/required-depths/error.json") as f:
        data = json.load(f)
    assert validate_required_depths(data, 'measurements') == {
        'level': 'error',
        'dataPath': '.measurements[3]',
        'message': 'must set both depthUpper and depthLower'
    }


def test_validate_water_measurements_valid():
    # site is not pond => valid
    node = {'siteType': SiteSiteType.CROPLAND.value}
    assert validate_water_measurements(node, 'measurements') is True

    with open(f"{fixtures_folder}/pond-measurements/valid.json") as f:
        node = json.load(f)
    assert validate_water_measurements(node, 'measurements') is True


def test_validate_water_measurements_invalid():
    with open(f"{fixtures_folder}/pond-measurements/invalid.json") as f:
        node = json.load(f)
    assert validate_water_measurements(node, 'measurements') == {
        'level': 'error',
        'dataPath': '.measurements',
        'message': 'must specify water type for ponds',
        'params': {
            'ids': ['salineWater', 'freshWater', 'brackishWater', 'waterSalinity']
        }
    }


def test_validate_water_salinity_valid():
    # site is not pond => valid
    node = {'siteType': SiteSiteType.CROPLAND.value}
    assert validate_water_salinity(node, 'measurements') is True

    with open(f"{fixtures_folder}/water-salinity/valid.json") as f:
        node = json.load(f)
    assert validate_water_salinity(node, 'measurements') is True


def test_validate_water_salinity_invalid():
    with open(f"{fixtures_folder}/water-salinity/invalid.json") as f:
        node = json.load(f)
    assert validate_water_salinity(node, 'measurements') == {
        'level': 'error',
        'dataPath': '.measurements',
        'message': 'invalid water salinity',
        'params': {
            'current': 'brackishWater',
            'expected': 'freshWater'
        }
    }
