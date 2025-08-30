from unittest.mock import patch
import pytest
import os
import json
from hestia_earth.schema import SiteSiteType, CycleFunctionalUnit

from tests.utils import fixtures_path, fake_get_terms
from hestia_earth.validation.utils import _group_nodes
from hestia_earth.validation.validators.cycle import (
    validate_cycle,
    validate_cycle_dates,
    validate_cycleDuration,
    validate_durations,
    validate_economicValueShare,
    validate_sum_aboveGroundCropResidue,
    validate_crop_residue_complete,
    validate_crop_residue_incomplete,
    validate_crop_siteDuration,
    validate_siteDuration,
    validate_possibleCoverCrop,
    validate_set_treatment,
    validate_products_animals,
    validate_linked_impact_assessment,
    validate_functionalUnit_not_1_ha,
    validate_stocking_density,
    validate_animal_product_mapping,
    validate_requires_substrate,
    validate_maximum_cycleDuration,
    validate_riceGrainInHuskFlooded_minimum_cycleDuration
)

fixtures_folder = os.path.join(fixtures_path, 'cycle')
class_path = 'hestia_earth.validation.validators.cycle'


@patch('hestia_earth.validation.validators.completeness.get_terms', return_value=fake_get_terms)
def test_validate_cycle_valid(*args):
    with open(f"{fixtures_folder}/valid.json") as f:
        node = json.load(f)
    results = validate_cycle(node)
    print(results)
    assert all([r is True for r in results])


def test_validate_cycle_dates_valid():
    cycle = {
        'startDate': '2020-01-01',
        'endDate': '2020-01-02'
    }
    assert validate_cycle_dates(cycle) is True
    cycle = {
        'startDate': '2020-01',
        'endDate': '2020-01'
    }
    assert validate_cycle_dates(cycle) is True
    cycle = {
        'startDate': '2020',
        'endDate': '2020'
    }
    assert validate_cycle_dates(cycle) is True


def test_validate_cycle_dates_invalid():
    cycle = {
        'startDate': '2020-01-02',
        'endDate': '2020-01-01'
    }
    assert validate_cycle_dates(cycle) == {
        'level': 'error',
        'dataPath': '.endDate',
        'message': 'must be greater than startDate'
    }
    cycle = {
        'startDate': '2020-01-01',
        'endDate': '2020-01-01'
    }
    assert validate_cycle_dates(cycle) == {
        'level': 'error',
        'dataPath': '.endDate',
        'message': 'must be greater than startDate'
    }


def test_validate_cycleDuration_valid():
    cycle = {
        'startDate': '2020-01-02',
        'endDate': '2021-01-01',
        'cycleDuration': 365
    }
    assert validate_cycleDuration(cycle) is True


def test_validate_cycleDuration_invalid():
    cycle = {
        'startDate': '2020-01-02',
        'endDate': '2021-01-01',
        'cycleDuration': 200
    }
    assert validate_cycleDuration(cycle) == {
        'level': 'error',
        'dataPath': '.cycleDuration',
        'message': 'must equal to endDate - startDate in days (~365.0)'
    }


@pytest.mark.parametrize(
    'cycle,expected',
    [
        (
            {'functionalUnit': '1 ha'}, True
        ),
        (
            {'functionalUnit': 'relative'},
            {
                'level': 'warning',
                'dataPath': '',
                'message': 'should add the fields for a relative cycle',
                'params': {
                    'expected': ['siteDuration', 'siteArea']
                }
            }
        ),
        (
            {'functionalUnit': 'relative', 'otherSites': [{}, {}]},
            {
                'level': 'warning',
                'dataPath': '',
                'message': 'should add the fields for a relative cycle',
                'params': {
                    'expected': ['siteDuration', 'siteArea', 'otherSitesDuration', 'otherSitesArea']
                }
            }
        ),
        (
            {'functionalUnit': 'relative', 'otherSites': [{}, {}], 'otherSitesDuration': [10, 20]},
            {
                'level': 'warning',
                'dataPath': '',
                'message': 'should add the fields for a relative cycle',
                'params': {
                    'expected': ['siteDuration', 'siteArea', 'otherSitesArea']
                }
            }
        ),
    ]
)
def test_validate_durations(cycle: dict, expected):
    assert validate_durations(cycle) == expected


def test_validate_economicValueShare_valid():
    products = [{
        'economicValueShare': 10
    }, {
        'economicValueShare': 80
    }]
    assert validate_economicValueShare(products) is True


def test_validate_economicValueShare_invalid():
    products = [{
        'economicValueShare': 10
    }, {
        'economicValueShare': 90
    }, {
        'economicValueShare': 10
    }]
    assert validate_economicValueShare(products) == {
        'level': 'error',
        'dataPath': '.products',
        'message': 'economicValueShare should sum to 100 or less across all products',
        'params': {
            'sum': 110
        }
    }


def test_validate_sum_aboveGroundCropResidue_valid():
    with open(f"{fixtures_folder}/aboveGroundCropResidue/valid.json") as f:
        data = json.load(f)
    assert validate_sum_aboveGroundCropResidue(data.get('products')) is True


def test_validate_sum_aboveGroundCropResidue_invalid():
    with open(f"{fixtures_folder}/aboveGroundCropResidue/invalid.json") as f:
        data = json.load(f)
    assert validate_sum_aboveGroundCropResidue(data.get('products')) == {
        'level': 'error',
        'dataPath': '.products[0].value',
        'message': 'must be more than or equal to '
        '(aboveGroundCropResidueBurnt + aboveGroundCropResidueLeftOnField)'
    }


@patch(f"{class_path}.get_terms", side_effect=fake_get_terms)
def test_validate_crop_residue_complete_valid(*args):
    with open(f"{fixtures_folder}/cropResidue/complete/valid.json") as f:
        data = json.load(f)
    assert validate_crop_residue_complete(data, data.get('site')) is True


@patch(f"{class_path}.get_terms", side_effect=fake_get_terms)
def test_validate_crop_residue_complete_invalid(*args):
    with open(f"{fixtures_folder}/cropResidue/complete/invalid.json") as f:
        data = json.load(f)
    assert validate_crop_residue_complete(data, data.get('site')) == {
        'level': 'error',
        'dataPath': '',
        'message': 'must specify the fate of cropResidue',
        'params': {
            'siteType': ['cropland', 'glass or high accessible cover']
        }
    }


@patch(f"{class_path}.get_terms", side_effect=fake_get_terms)
def test_validate_crop_residue_incomplete_valid(*args):
    with open(f"{fixtures_folder}/cropResidue/incomplete/valid.json") as f:
        data = json.load(f)
    assert validate_crop_residue_incomplete(data, data.get('site')) is True


@patch(f"{class_path}.get_terms", side_effect=fake_get_terms)
def test_validate_crop_residue_incomplete_invalid(*args):
    with open(f"{fixtures_folder}/cropResidue/incomplete/invalid.json") as f:
        data = json.load(f)
    assert validate_crop_residue_incomplete(data, data.get('site')) == {
        'level': 'warning',
        'dataPath': '',
        'message': 'should specify the fate of cropResidue',
        'params': {
            'siteType': ['cropland', 'glass or high accessible cover']
        }
    }


def test_validate_crop_siteDuration_valid():
    with open(f"{fixtures_folder}/siteDuration/crop/valid-same-duration.json") as f:
        data = json.load(f)
    assert validate_crop_siteDuration(data) is True

    with open(f"{fixtures_folder}/siteDuration/crop/valid-different-duration.json") as f:
        data = json.load(f)
    assert validate_crop_siteDuration(data) is True


def test_validate_crop_siteDuration_invalid():
    with open(f"{fixtures_folder}/siteDuration/crop/invalid.json") as f:
        data = json.load(f)
    assert validate_crop_siteDuration(data) == {
        'level': 'error',
        'dataPath': '.siteDuration',
        'message': 'should not be equal to cycleDuration for crop',
        'params': {
            'current': 'one year prior',
            'expected': 'harvest of previous crop'
        }
    }


def test_validate_siteDuration_valid():
    with open(f"{fixtures_folder}/siteDuration/valid.json") as f:
        data = json.load(f)
    assert validate_siteDuration(data) is True

    with open(f"{fixtures_folder}/siteDuration/valid-no-siteDuration.json") as f:
        data = json.load(f)
    assert validate_siteDuration(data) is True

    with open(f"{fixtures_folder}/siteDuration/valid-otherSites.json") as f:
        data = json.load(f)
    assert validate_siteDuration(data) is True


def test_validate_siteDuration_invalid():
    with open(f"{fixtures_folder}/siteDuration/invalid.json") as f:
        data = json.load(f)
    assert validate_siteDuration(data) == {
        'level': 'error',
        'dataPath': '.siteDuration',
        'message': 'must be less than or equal to cycleDuration'
    }


def test_validate_possibleCoverCrop_valid():
    # no products should be valid
    assert validate_possibleCoverCrop({}) is True

    with open(f"{fixtures_folder}/coverCrop/valid.json") as f:
        data = json.load(f)
    assert validate_possibleCoverCrop(data) is True

    with open(f"{fixtures_folder}/coverCrop/valid-not-coverCrop.json") as f:
        data = json.load(f)
    assert validate_possibleCoverCrop(data) is True


def test_validate_possibleCoverCrop_error():
    with open(f"{fixtures_folder}/coverCrop/invalid.json") as f:
        data = json.load(f)
    assert validate_possibleCoverCrop(data) == {
        'level': 'error',
        'dataPath': '',
        'message': 'cover crop cycle contains non cover crop product'
    }


def test_validate_set_treatment_valid():
    cycle = {'treatment': 'treatment'}

    # no experimentDesign in Source
    source = {}
    validate_set_treatment(cycle, source) is True

    # with experimentDesign and treatment
    source = {'experimentDesign': 'design'}
    validate_set_treatment(cycle, source) is True


def test_validate_set_treatment_warning():
    source = {'experimentDesign': 'design'}
    cycle = {}
    assert validate_set_treatment(cycle, source) == {
        'level': 'warning',
        'dataPath': '.treatment',
        'message': 'should specify a treatment when experimentDesign is specified'
    }


def test_validate_products_animals_valid():
    # no products should be valid
    assert validate_products_animals({}) is True

    with open(f"{fixtures_folder}/products/animals/valid.json") as f:
        data = json.load(f)
    assert validate_products_animals(data) is True


def test_validate_products_animals_invalid():
    with open(f"{fixtures_folder}/products/animals/invalid.json") as f:
        data = json.load(f)
    assert validate_products_animals(data) == {
        'level': 'warning',
        'dataPath': '.products',
        'message': 'should not specify both liveAnimal and animalProduct'
    }


def test_validate_linked_impact_assessment_valid():
    with open(f"{fixtures_folder}/product-linked-ia/cycle.json") as f:
        cycle = json.load(f)
    with open(f"{fixtures_folder}/product-linked-ia/valid.json") as f:
        nodes = json.load(f).get('nodes')
    assert validate_linked_impact_assessment(cycle, _group_nodes(nodes)) is True


def test_validate_linked_impact_assessment_invalid():
    with open(f"{fixtures_folder}/product-linked-ia/cycle.json") as f:
        cycle = json.load(f)

    assert validate_linked_impact_assessment(cycle, {}) == [
        {
            'level': 'error',
            'dataPath': '.products[0].term',
            'message': 'no ImpactAssessment are associated with this Product',
            'params': {
                'product': {
                    '@type': 'Term',
                    '@id': 'maizeGrain',
                    'termType': 'crop'
                },
                'node': {
                    'type': 'Cycle',
                    'id': 'fake-cycle'
                }
            }
        },
        {
            'level': 'error',
            'dataPath': '.products[1].term',
            'message': 'no ImpactAssessment are associated with this Product',
            'params': {
                'product': {
                    '@type': 'Term',
                    '@id': 'maizeGrain',
                    'termType': 'crop'
                },
                'node': {
                    'type': 'Cycle',
                    'id': 'fake-cycle'
                }
            }
        }
    ]

    with open(f"{fixtures_folder}/product-linked-ia/invalid-multiple.json") as f:
        nodes = json.load(f).get('nodes')
    assert validate_linked_impact_assessment(cycle, _group_nodes(nodes)) == [
        {
            'level': 'error',
            'dataPath': '.products[0].term',
            'message': 'no ImpactAssessment are associated with this Product',
            'params': {
                'product': {
                    '@type': 'Term',
                    '@id': 'maizeGrain',
                    'termType': 'crop'
                },
                'node': {
                    'type': 'Cycle',
                    'id': 'fake-cycle'
                }
            }
        },
        {
            'level': 'error',
            'dataPath': '.products[1].term',
            'message': 'multiple ImpactAssessment are associated with this Product',
            'params': {
                'product': {
                    '@type': 'Term',
                    '@id': 'maizeGrain',
                    'termType': 'crop'
                },
                'node': {
                    'type': 'Cycle',
                    'id': 'fake-cycle'
                }
            }
        }
    ]


def test_validate_functionalUnit_not_1_ha_valid():
    cycle = {
        'functionalUnit': CycleFunctionalUnit.RELATIVE.value
    }
    site = {
        'siteType': SiteSiteType.AGRI_FOOD_PROCESSOR.value
    }
    assert validate_functionalUnit_not_1_ha(cycle, site) is True


def test_validate_functionalUnit_not_1_ha_invalid():
    cycle = {
        'functionalUnit': CycleFunctionalUnit._1_HA.value
    }
    site = {
        'siteType': SiteSiteType.AGRI_FOOD_PROCESSOR.value
    }
    assert validate_functionalUnit_not_1_ha(cycle, site) == {
        'level': 'error',
        'dataPath': '.functionalUnit',
        'message': 'must not be equal to 1 ha',
        'params': {
            'siteType': site.get('siteType')
        }
    }


def test_validate_stocking_density_valid():
    # no products should be valid
    assert validate_stocking_density({}, {}) is True

    with open(f"{fixtures_folder}/practices/stockingDensityPermanentPastureAverage/valid.json") as f:
        cycle = json.load(f)

    # not permanent pasture is valid
    site = {'siteType': SiteSiteType.CROPLAND.value}
    assert validate_stocking_density(cycle, site) is True

    # permanent pasture is valid
    site = {'siteType': SiteSiteType.PERMANENT_PASTURE.value}
    assert validate_stocking_density(cycle, site) is True


def test_validate_stocking_density_invalid():
    with open(f"{fixtures_folder}/practices/stockingDensityPermanentPastureAverage/invalid.json") as f:
        cycle = json.load(f)

    # not permanent pasture is valid
    site = {'siteType': SiteSiteType.CROPLAND.value}
    assert validate_stocking_density(cycle, site) is True

    site = {'siteType': SiteSiteType.PERMANENT_PASTURE.value}
    assert validate_stocking_density(cycle, site) == {
        'level': 'warning',
        'dataPath': '.practices',
        'message': 'should add the term stockingDensityPermanentPastureAverage',
        'params': {
            'expected': 'stockingDensityPermanentPastureAverage'
        }
    }


def test_validate_animal_product_mapping_valid():
    # no products should be valid
    assert validate_animal_product_mapping({}) is True

    with open(f"{fixtures_folder}/liveAnimal-animalProduct-mapping/valid.json") as f:
        cycle = json.load(f)
    assert validate_animal_product_mapping(cycle) is True


def test_validate_animal_product_mapping_invalid():
    with open(f"{fixtures_folder}/liveAnimal-animalProduct-mapping/invalid.json") as f:
        cycle = json.load(f)
    assert validate_animal_product_mapping(cycle) == {
        'level': 'error',
        'dataPath': '.products[0].term',
        'message': 'is not an allowed animalProduct',
        'params': {
            'expected': [
                'fatDairyCattle',
                'hidesDairyCattleFresh',
                'meatDairyCattleColdCarcassWeight',
                'meatDairyCattleColdDressedCarcassWeight',
                'meatDairyCattleLiveweight',
                'offalDairyCattle',
                'offalDairyCattleEdible',
                'offalDairyCattleInedible'
            ]
        }
    }


def test_validate_requires_substrate_valid():
    # no practices should be valid
    assert validate_requires_substrate({}, {}) is True

    # different siteType should be valid
    assert validate_requires_substrate({}, {'siteType': SiteSiteType.CROPLAND.value}) is True

    with open(f"{fixtures_folder}/substrate/required/valid.json") as f:
        cycle = json.load(f)
    assert validate_requires_substrate(cycle, cycle.get('site')) is True


def test_validate_requires_substrate_invalid():
    with open(f"{fixtures_folder}/substrate/required/invalid.json") as f:
        cycle = json.load(f)
    assert validate_requires_substrate(cycle, cycle.get('site')) == {
        'level': 'error',
        'dataPath': '.inputs',
        'message': 'must add substrate inputs',
        'params': {
            'term': {
                '@type': 'Term',
                'termType': 'system',
                '@id': 'protectedCroppingSystemSubstrateBased'
            }
        }
    }


def test_validate_maximum_cycleDuration_valid():
    # no cycleDuration should be valid
    assert validate_maximum_cycleDuration({}) is True

    with open(f"{fixtures_folder}/maximumCycleDuration/valid.json") as f:
        cycle = json.load(f)
    assert validate_maximum_cycleDuration(cycle) is True

    with open(f"{fixtures_folder}/maximumCycleDuration/valid-dates.json") as f:
        cycle = json.load(f)
    assert validate_maximum_cycleDuration(cycle) is True

    with open(f"{fixtures_folder}/maximumCycleDuration/valid-dates-year-only.json") as f:
        cycle = json.load(f)
    assert validate_maximum_cycleDuration(cycle) is True


def test_validate_maximum_cycleDuration_invalid():
    with open(f"{fixtures_folder}/maximumCycleDuration/invalid.json") as f:
        cycle = json.load(f)
    assert validate_maximum_cycleDuration(cycle) == {
        'level': 'error',
        'dataPath': '.cycleDuration',
        'message': 'must be below maximum cycleDuration',
        'params': {
            'comparison': '<=',
            'limit': 731,
            'exclusive': False,
            'current': 1000
        }
    }

    with open(f"{fixtures_folder}/maximumCycleDuration/invalid-dates.json") as f:
        cycle = json.load(f)
    assert validate_maximum_cycleDuration(cycle) == {
        'level': 'error',
        'dataPath': '.startDate',
        'message': 'must be below maximum cycleDuration',
        'params': {
            'comparison': '<=',
            'limit': 731,
            'exclusive': False,
            'current': 3257
        }
    }

    with open(f"{fixtures_folder}/maximumCycleDuration/invalid-dates-year-only.json") as f:
        cycle = json.load(f)
    assert validate_maximum_cycleDuration(cycle) == {
        'level': 'error',
        'dataPath': '.startDate',
        'message': 'must be below maximum cycleDuration',
        'params': {
            'comparison': '<=',
            'limit': 731,
            'exclusive': False,
            'current': 1096
        }
    }


def test_validate_riceGrainInHuskFlooded_minimum_cycleDuration_valid():
    # no cycleDuration should be valid
    assert validate_riceGrainInHuskFlooded_minimum_cycleDuration({}, {}) is True

    with open(f"{fixtures_folder}/riceGrainInHuskFlooded-minimumCycleDuration/valid.json") as f:
        cycle = json.load(f)
    assert validate_riceGrainInHuskFlooded_minimum_cycleDuration(cycle, cycle.get('site')) is True


def test_validate_riceGrainInHuskFlooded_minimum_cycleDuration_invalid():
    with open(f"{fixtures_folder}/riceGrainInHuskFlooded-minimumCycleDuration/invalid.json") as f:
        cycle = json.load(f)
    assert validate_riceGrainInHuskFlooded_minimum_cycleDuration(cycle, cycle.get('site')) == {
        'level': 'warning',
        'dataPath': '.cycleDuration',
        'message': 'should be more than the cropping duration',
        'params': {
            'expected': 111,
            'current': 100
        }
    }
