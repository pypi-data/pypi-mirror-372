import os
import json

from tests.utils import fixtures_path
from hestia_earth.validation.validators.source import (
    validate_source
)

fixtures_folder = os.path.join(fixtures_path, 'source')
class_path = 'hestia_earth.validation.validators.source'


def test_validate_valid():
    with open(f"{fixtures_path}/source/valid.json") as f:
        node = json.load(f)
    results = validate_source(node)
    assert all([r is True for r in results])
