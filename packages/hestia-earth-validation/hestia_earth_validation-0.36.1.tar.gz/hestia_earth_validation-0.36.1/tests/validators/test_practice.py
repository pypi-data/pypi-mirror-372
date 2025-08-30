import os
from unittest.mock import patch
import json
from hestia_earth.schema import SiteSiteType

from tests.utils import fixtures_path, fake_get_terms
from hestia_earth.validation.validators.practice import (
    validate_defaultValue,
    validate_waterRegime_rice_products,
    validate_croppingDuration_riceGrainInHuskFlooded,
    validate_longFallowDuration,
    validate_excretaManagement,
    validate_no_tillage,
    validate_tillage_site_type,
    validate_tillage_values,
    validate_liveAnimal_system,
    validate_pastureGrass_key_termType,
    validate_pastureGrass_key_value,
    validate_has_pastureGrass,
    validate_permanent_crop_productive_phase,
    validate_processing_operation,
    validate_landCover_match_products,
    validate_practices_management
)

class_path = 'hestia_earth.validation.validators.practice'
fixtures_folder = os.path.join(fixtures_path, 'practice')


def test_validate_defaultValue_valid():
    # no practices should be valid
    assert validate_defaultValue({}) is True

    with open(f"{fixtures_folder}/defaultValue/valid.json") as f:
        data = json.load(f)
    assert validate_defaultValue(data, 'nodes') is True


def test_validate_defaultValue_invalid():
    with open(f"{fixtures_folder}/defaultValue/invalid.json") as f:
        data = json.load(f)
    assert validate_defaultValue(data, 'nodes') == {
        'level': 'warning',
        'dataPath': '.nodes[0]',
        'message': 'should specify a value when HESTIA has a default one',
        'params': {
            'term': {
                '@type': 'Term',
                '@id': 'monocultureSimpleBatchProduction',
                'termType': 'aquacultureManagement'
            },
            'expected': 100
        }
    }


@patch(f"{class_path}.get_terms", side_effect=fake_get_terms)
def test_validate_waterRegime_rice_products_valid(*args):
    # no practices should be valid
    assert validate_waterRegime_rice_products({}, 'practices') is True

    with open(f"{fixtures_folder}/waterRegime/rice/valid.json") as f:
        cycle = json.load(f)
    assert validate_waterRegime_rice_products(cycle) is True

    with open(f"{fixtures_folder}/waterRegime/rice/valid-0-value.json") as f:
        cycle = json.load(f)
    assert validate_waterRegime_rice_products(cycle) is True


@patch(f"{class_path}.get_terms", side_effect=fake_get_terms)
def test_validate_waterRegime_rice_products_invalid(*args):
    with open(f"{fixtures_folder}/waterRegime/rice/invalid.json") as f:
        cycle = json.load(f)
    assert validate_waterRegime_rice_products(cycle) == {
        'level': 'error',
        'dataPath': '.practices[0].term',
        'message': 'rice products not allowed for this water regime practice',
        'params': {
            'term': {
                '@type': 'Term',
                '@id': 'irrigatedTypeUnspecified',
                'termType': 'waterRegime'
            },
            'products': [{
                '@type': 'Term',
                '@id': 'riceMeal',
                'termType': 'crop'
            }]
        }
    }


def test_validate_croppingDuration_riceGrainInHuskFlooded_valid():
    # no practices should be valid
    assert validate_croppingDuration_riceGrainInHuskFlooded({}, 'practices') is True

    with open(f"{fixtures_folder}/croppingDuration//riceGrainInHuskFlooded/valid.json") as f:
        data = json.load(f)
    assert validate_croppingDuration_riceGrainInHuskFlooded(data) is True


def test_validate_croppingDuration_riceGrainInHuskFlooded_invalid():
    with open(f"{fixtures_folder}/croppingDuration//riceGrainInHuskFlooded/invalid.json") as f:
        data = json.load(f)
    assert validate_croppingDuration_riceGrainInHuskFlooded(data) == {
        'level': 'error',
        'dataPath': '.practices[0].value',
        'message': 'croppingDuration must be between min and max',
        'params': {
            'min': 78,
            'max': 150
        }
    }


def test_validate_longFallowDuration_valid():
    # no practices should be valid
    assert validate_longFallowDuration([]) is True

    with open(f"{fixtures_folder}/longFallowDuration/valid.json") as f:
        data = json.load(f)
    assert validate_longFallowDuration(data.get('nodes')) is True


def test_validate_longFallowDuration_invalid():
    with open(f"{fixtures_folder}/longFallowDuration/invalid.json") as f:
        data = json.load(f)
    assert validate_longFallowDuration(data.get('nodes')) == {
        'level': 'error',
        'dataPath': '.practices[1].value',
        'message': 'longFallowDuration must be lower than 5 years'
    }


def test_validate_excretaManagement_valid():
    # no practices should be valid
    assert validate_excretaManagement({}, []) is True

    with open(f"{fixtures_folder}/excretaManagement/valid.json") as f:
        cycle = json.load(f)
    assert validate_excretaManagement(cycle, cycle.get('practices')) is True


def test_validate_excretaManagement_invalid():
    with open(f"{fixtures_folder}/excretaManagement/invalid.json") as f:
        cycle = json.load(f)
    assert validate_excretaManagement(cycle, cycle.get('practices')) == {
        'level': 'error',
        'dataPath': '.practices',
        'message': 'an excreta input is required when using an excretaManagement practice'
    }


def test_validate_no_tillage_valid():
    # no practices should be valid
    assert validate_no_tillage([]) is True

    with open(f"{fixtures_folder}/noTillage/valid.json") as f:
        data = json.load(f)
    assert validate_no_tillage(data.get('nodes')) is True

    # value is not 100
    with open(f"{fixtures_folder}/noTillage/valid-value-not-100.json") as f:
        data = json.load(f)
    assert validate_no_tillage(data.get('nodes')) is True


def test_validate_no_tillage_invalid():
    with open(f"{fixtures_folder}/noTillage/invalid.json") as f:
        data = json.load(f)
    assert validate_no_tillage(data.get('nodes')) == {
        'level': 'error',
        'dataPath': '.practices[1]',
        'message': 'is not allowed in combination with noTillage'
    }


def test_validate_tillage_site_type_valid():
    # no practices should be valid
    assert validate_tillage_site_type([], {}) is True

    with open(f"{fixtures_folder}/tillage-siteType/valid.json") as f:
        cycle = json.load(f)
    assert validate_tillage_site_type(cycle.get('practices'), cycle.get('site')) is True

    # no practice but skipped termType
    with open(f"{fixtures_folder}/tillage-siteType/warning.json") as f:
        cycle = json.load(f)
    site = cycle.get('site')
    site['siteType'] = SiteSiteType.SEA_OR_OCEAN.value
    assert validate_tillage_site_type(cycle.get('practices'), site) is True


def test_validate_tillage_site_type_warning():
    with open(f"{fixtures_folder}/tillage-siteType/warning.json") as f:
        cycle = json.load(f)
    assert validate_tillage_site_type(cycle.get('practices'), cycle.get('site')) == {
        'level': 'warning',
        'dataPath': '.practices',
        'message': 'should contain a tillage practice'
    }


def test_validate_tillage_values_valid():
    # no practices should be valid
    assert validate_tillage_values([]) is True

    with open(f"{fixtures_folder}/tillage-values/valid.json") as f:
        cycle = json.load(f)
    assert validate_tillage_values(cycle.get('practices')) is True


def test_validate_tillage_values_invalid():
    with open(f"{fixtures_folder}/tillage-values/invalid-noTillage.json") as f:
        cycle = json.load(f)
    assert validate_tillage_values(cycle.get('practices')) == {
        'level': 'error',
        'dataPath': '.practices[0]',
        'message': 'cannot use no tillage if depth or number of tillages is not 0'
    }

    with open(f"{fixtures_folder}/tillage-values/invalid-fullTillage.json") as f:
        cycle = json.load(f)
    assert validate_tillage_values(cycle.get('practices')) == {
        'level': 'error',
        'dataPath': '.practices[0]',
        'message': 'cannot use full tillage if depth or number of tillages is 0'
    }


def test_validate_liveAnimal_system_valid():
    # no practices should be valid
    assert validate_liveAnimal_system({}) is True

    with open(f"{fixtures_folder}/liveAnimal-system/valid.json") as f:
        data = json.load(f)
    assert validate_liveAnimal_system(data) is True


def test_validate_liveAnimal_system_invalid():
    with open(f"{fixtures_folder}/liveAnimal-system/invalid.json") as f:
        data = json.load(f)
    assert validate_liveAnimal_system(data) == {
        'level': 'warning',
        'dataPath': '.practices',
        'message': 'should add an animal production system'
    }


def test_validate_pastureGrass_key_termType_valid():
    # no practices should be valid
    assert validate_pastureGrass_key_termType({}) is True

    with open(f"{fixtures_folder}/pastureGrass/key-termType/valid.json") as f:
        practice = json.load(f)
    assert validate_pastureGrass_key_termType({'practices': [practice]}) is True


def test_validate_pastureGrass_key_termType_invalid():
    with open(f"{fixtures_folder}/pastureGrass/key-termType/invalid.json") as f:
        practice = json.load(f)
    assert validate_pastureGrass_key_termType({'practices': [practice]}) == {
        'level': 'error',
        'dataPath': '.practices[0].key',
        'message': "pastureGrass key termType must be 'landCover'",
        'params': {
            'expected': 'landCover',
            'term': {'@id': 'alfalfaFreshForage', '@type': 'Term', 'termType': 'forage'},
            'value': 'forage'
        }
    }


def test_validate_pastureGrass_key_value_valid():
    # no practices should be valid
    assert validate_pastureGrass_key_value({}) is True

    with open(f"{fixtures_folder}/pastureGrass/key-value/valid.json") as f:
        cycle = json.load(f)
    assert validate_pastureGrass_key_value(cycle, 'practices') is True


def test_validate_pastureGrass_key_value_invalid():
    with open(f"{fixtures_folder}/pastureGrass/key-value/invalid.json") as f:
        cycle = json.load(f)
    assert validate_pastureGrass_key_value(cycle, 'practices') == {
        'level': 'error',
        'dataPath': '.practices',
        'message': 'the sum of all pastureGrass values must be 100',
        'params': {
            'expected': 100,
            'current': 80
        }
    }

    with open(f"{fixtures_folder}/pastureGrass/key-value/invalid-numbers.json") as f:
        cycle = json.load(f)
    assert validate_pastureGrass_key_value(cycle, 'practices') == {
        'level': 'error',
        'dataPath': '.practices',
        'message': 'all values must be numbers'
    }


def test_validate_has_pastureGrass_valid():
    with open(f"{fixtures_folder}/pastureGrass/permanent-pasture/valid.json") as f:
        data = json.load(f)
    assert validate_has_pastureGrass(data, data.get('site'), 'practices') is True


def test_validate_has_pastureGrass_invalid():
    with open(f"{fixtures_folder}/pastureGrass/permanent-pasture/invalid.json") as f:
        data = json.load(f)
    assert validate_has_pastureGrass(data, data.get('site')) == {
        'level': 'warning',
        'dataPath': '.practices',
        'message': 'should add the term pastureGrass'
    }


def test_validate_permanent_crop_productive_phase_valid():
    # no practices is valid
    assert validate_permanent_crop_productive_phase({}, 'practices') is True

    with open(f"{fixtures_folder}/productivePhasePermanentCrops/valid.json") as f:
        data = json.load(f)
    assert validate_permanent_crop_productive_phase(data, 'practices') is True

    with open(f"{fixtures_folder}/productivePhasePermanentCrops/valid-0-value.json") as f:
        data = json.load(f)
    assert validate_permanent_crop_productive_phase(data, 'practices') is True

    with open(f"{fixtures_folder}/productivePhasePermanentCrops/valid-no-value.json") as f:
        data = json.load(f)
    assert validate_permanent_crop_productive_phase(data, 'practices') is True


def test_validate_permanent_crop_productive_phase_invalid():
    with open(f"{fixtures_folder}/productivePhasePermanentCrops/invalid.json") as f:
        data = json.load(f)
    assert validate_permanent_crop_productive_phase(data) == {
        'level': 'error',
        'dataPath': '.practices',
        'message': 'must add the term productivePhasePermanentCrops'
    }


def test_validate_processing_operation_valid():
    # no practices is valid
    assert validate_processing_operation({}, {}) is True

    with open(f"{fixtures_folder}/processingOperation/valid.json") as f:
        data = json.load(f)
    assert validate_processing_operation(data, data.get('site'), 'practices') is True

    with open(f"{fixtures_folder}/processingOperation/valid-cropland.json") as f:
        data = json.load(f)
    assert validate_processing_operation(data, data.get('site'), 'practices') is True


def test_validate_processing_operation_invalid():
    with open(f"{fixtures_folder}/processingOperation/invalid.json") as f:
        data = json.load(f)
    assert validate_processing_operation(data, data.get('site'), 'practices') == {
        'level': 'error',
        'dataPath': '.practices',
        'message': 'must have a primary processing operation'
    }

    with open(f"{fixtures_folder}/processingOperation/invalid-no-primary.json") as f:
        data = json.load(f)
    assert validate_processing_operation(data, data.get('site'), 'practices') == {
        'level': 'error',
        'dataPath': '.practices',
        'message': 'must have a primary processing operation'
    }


def test_validate_landCover_match_products_valid():
    # no practices is valid
    assert validate_landCover_match_products({}, {}) is True

    with open(f"{fixtures_folder}/landCover-products/valid.json") as f:
        data = json.load(f)
    assert validate_landCover_match_products(data, data.get('site'), 'practices') is True

    with open(f"{fixtures_folder}/landCover-products/valid-coverCrop.json") as f:
        data = json.load(f)
    assert validate_landCover_match_products(data, data.get('site'), 'practices') is True


def test_validate_landCover_match_products_invalid():
    with open(f"{fixtures_folder}/landCover-products/invalid.json") as f:
        data = json.load(f)
    assert validate_landCover_match_products(data, data.get('site'), 'practices') == {
        'level': 'error',
        'dataPath': '.practices',
        'message': 'at least one landCover practice must match an equivalent product',
        'params': {
            'current': ['abacaPlant'],
            'expected': ['wheatPlant']
        }
    }


def test_validate_practices_management_valid():
    # no practices is valid
    assert validate_practices_management({}, {}) is True

    with open(f"{fixtures_folder}/site-management/valid.json") as f:
        data = json.load(f)
    assert validate_practices_management(data, data.get('site'), 'practices') is True


def test_validate_practices_management_invalid():
    with open(f"{fixtures_folder}/site-management/invalid.json") as f:
        data = json.load(f)
    assert validate_practices_management(data, data.get('site'), 'practices') == {
        'level': 'error',
        'dataPath': '.practices[0].value',
        'message': 'should match the site management node value',
        'params': {
            'current': 50,
            'expected': 100
        }
    }
