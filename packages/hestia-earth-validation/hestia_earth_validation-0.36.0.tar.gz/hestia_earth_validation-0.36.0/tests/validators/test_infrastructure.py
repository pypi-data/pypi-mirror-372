import json

from tests.utils import fixtures_path
from hestia_earth.validation.validators.infrastructure import validate_lifespan


def test_validate_lifespan_valid():
    # no infrastructure should be valid
    assert validate_lifespan([]) is True

    with open(f"{fixtures_path}/infrastructure/lifespan/valid.json") as f:
        data = json.load(f)
    assert validate_lifespan(data.get('nodes')) is True


def test_validate_lifespan_invalid():
    with open(f"{fixtures_path}/infrastructure/lifespan/invalid.json") as f:
        data = json.load(f)
    assert validate_lifespan(data.get('nodes')) == {
        'level': 'error',
        'dataPath': '.infrastructure[1].defaultLifespan',
        'message': 'must equal to endDate - startDate in decimal years (~2.6)'
    }
