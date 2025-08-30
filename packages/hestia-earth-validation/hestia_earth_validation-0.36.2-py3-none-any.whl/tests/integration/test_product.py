import os
import json
from tests.utils import fixtures_path
from hestia_earth.validation.validators.product import validate_product_yield

fixtures_folder = os.path.join(fixtures_path, 'integration', 'distribution')


def test_validate_product_yield():
    with open(os.path.join(fixtures_folder, 'product-yield-invalid.json')) as f:
        cycle = json.load(f)

    result = validate_product_yield(cycle, cycle.get('site'))
    assert result['level'] == 'warning'
    assert result['dataPath'] == '.products[0].value'
    assert result['message'] == 'is outside confidence interval'
    assert result['params']['outliers'] == [1000]
