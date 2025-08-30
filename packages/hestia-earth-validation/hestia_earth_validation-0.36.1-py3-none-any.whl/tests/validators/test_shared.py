from unittest.mock import patch
import pytest
import json
from hestia_earth.schema import TermTermType

from tests.utils import fixtures_path
from hestia_earth.validation.utils import _group_nodes, _hash_nodes
from hestia_earth.validation.validators.shared import (
    validate_dates,
    validate_list_dates,
    validate_list_min_below_max,
    validate_list_min_max_lookup,
    validate_country,
    validate_region_in_country,
    validate_is_region,
    validate_list_country_region,
    validate_area,
    validate_coordinates,
    need_validate_coordinates,
    validate_list_term_percent,
    validate_empty_fields,
    validate_linked_source_privacy,
    validate_list_dates_length,
    validate_date_lt_today,
    validate_list_date_lt_today,
    value_difference,
    is_value_different,
    validate_list_model,
    validate_list_model_config,
    validate_properties_same_length,
    validate_list_duplicate_values,
    validate_nodes_duplicates,
    validate_boundary_area,
    validate_region_size,
    need_validate_region_size,
    validate_private_has_source,
    validate_list_value_between_min_max,
    validate_list_dates_after,
    validate_duplicated_term_units,
    validate_list_sum_100_percent,
    validate_list_percent_requires_value,
    validate_other_model,
    validate_list_valueType,
    validate_nested_existing_node
)
from hestia_earth.validation.validators.cycle import PRODUCTS_MODEL_CONFIG, INPUTS_MODEL_CONFIG

class_path = 'hestia_earth.validation.validators.shared'
fixtures_folder = f"{fixtures_path}/shared"


def test_validate_dates():
    assert validate_dates({
        'startDate': '2020-01-01'
    }) is True

    assert validate_dates({
        'endDate': '2020-01-02'
    }) is True

    assert validate_dates({
        'startDate': '2020-01-01',
        'endDate': '2020-01-02'
    }) is True

    assert not validate_dates({
        'startDate': '2020-01-02',
        'endDate': '2020-01-01'
    })


def test_validate_list_dates_length_valid():
    cycle = {
        'emissions': [{
            'value': [1],
            'dates': [1]
        }]
    }
    assert validate_list_dates_length(cycle, 'emissions') is True


def test_validate_list_dates_length_invalid():
    cycle = {
        'emissions': [{
            'value': [1],
            'dates': [1, 2]
        }]
    }
    assert validate_list_dates_length(cycle, 'emissions') == {
        'level': 'error',
        'dataPath': '.emissions[0].dates',
        'message': 'must contain as many items as values',
        'params': {
            'current': 2,
            'expected': 1
        }
    }


def test_validate_list_dates_valid():
    node = {
        'list': [{
            'startDate': '2020-01-01',
            'endDate': '2020-01-02'
        }]
    }
    assert validate_list_dates(node, 'list') is True


def test_validate_list_dates_invalid():
    node = {
        'list': [{
            'startDate': '2020-01-02',
            'endDate': '2020-01-01'
        }]
    }
    assert validate_list_dates(node, 'list') == {
        'level': 'error',
        'dataPath': '.list[0].endDate',
        'message': 'must be greater than startDate'
    }


def validate_list_dates_after_valid():
    node = {
        'type': 'Cycle',
        'date': '2020-01-01',
        'list': [{
            'start': '2020-01-02',
            'end': '2020-01-03',
            'dates': [
                '2020-01-02',
                '2020-01-03'
            ]
        }]
    }
    assert validate_list_dates_after(node, 'date', 'list', ['start', 'end', 'dates']) is True


def test_validate_list_dates_after_invalid():
    node = {
        'type': 'Cycle',
        'date': '2020-01-01',
        'list': [{
            'start': '2020-01-02',
            'end': '2019-01-01',
            'dates': [
                '2020-01-02',
                '2019-01-01'
            ]
        }]
    }
    assert validate_list_dates_after(node, 'date', 'list', ['start', 'end', 'dates']) == [
        {
            'level': 'warning',
            'dataPath': '.list[0].end',
            'message': 'must be greater than Cycle date'
        },
        {
            'level': 'warning',
            'dataPath': '.list[0].dates[1]',
            'message': 'must be greater than Cycle date'
        }
    ]


def test_validate_list_min_below_max_valid():
    node = {
        'list': [{
            'min': 10,
            'max': 100
        }]
    }
    assert validate_list_min_below_max(node, 'list') is True
    node = {
        'list': [{
            'min': [
                50,
                10
            ],
            'max': [
                60,
                20
            ]
        }]
    }
    assert validate_list_min_below_max(node, 'list') is True


def test_validate_list_min_below_max_invalid():
    node = {
        'list': [{
            'min': 100,
            'max': 10
        }]
    }
    assert validate_list_min_below_max(node, 'list') == {
        'level': 'error',
        'dataPath': '.list[0].max',
        'message': 'must be greater than min'
    }
    node = {
        'list': [{
            'min': [1, 120],
            'max': [10, 20]
        }]
    }
    assert validate_list_min_below_max(node, 'list') == {
        'level': 'error',
        'dataPath': '.list[0].max',
        'message': 'must be greater than min'
    }


def test_validate_list_value_between_min_max_valid():
    node = {
        'list': [{
            'min': 10,
            'value': 50,
            'max': 100
        }]
    }
    assert validate_list_value_between_min_max(node, 'list') is True
    node = {
        'list': [{
            'min': [
                50,
                10
            ],
            'value': [
                55,
                15
            ],
            'max': [
                60,
                20
            ]
        }]
    }
    assert validate_list_value_between_min_max(node, 'list') is True


def test_validate_list_value_between_min_max_invalid():
    node = {
        'list': [{
            'min': 0,
            'value': 20,
            'max': 10
        }]
    }
    assert validate_list_value_between_min_max(node, 'list') == {
        'level': 'error',
        'dataPath': '.list[0].value',
        'message': 'must be between min and max',
        'params': {
            'max': 10,
            'min': 0,
        }
    }
    node = {
        'list': [{
            'min': [1, 10],
            'value': [5, 200],
            'max': [10, 20]
        }]
    }
    assert validate_list_value_between_min_max(node, 'list') == {
        'level': 'error',
        'dataPath': '.list[0].value',
        'message': 'must be between min and max',
        'params': {
            'max': [10, 20],
            'min': [1, 10],
        }
    }


def test_validate_list_min_max_lookup_valid():
    # no measurements should be valid
    assert validate_list_min_max_lookup({}, 'measurements') is True

    with open(f"{fixtures_folder}/min-max/value-valid.json") as f:
        data = json.load(f)
    assert validate_list_min_max_lookup(data, 'measurements') is True


def test_validate_list_min_max_lookup_invalid():
    with open(f"{fixtures_folder}/min-max/value-above.json") as f:
        data = json.load(f)
    assert validate_list_min_max_lookup(data, 'measurements') == {
        'level': 'error',
        'dataPath': '.measurements[0].value',
        'message': 'should be below 25000.0'
    }

    with open(f"{fixtures_folder}/min-max/value-below.json") as f:
        data = json.load(f)
    assert validate_list_min_max_lookup(data, 'measurements') == {
        'level': 'error',
        'dataPath': '.measurements[0].value',
        'message': 'should be above 0.0'
    }


def test_validate_country_valid():
    node = {
        'country': {
            '@id': 'GADM-AUS',
            'name': 'Australia'
        }
    }
    assert validate_country(node) is True
    node['country']['@id'] = 'region-world'
    assert validate_country(node) is True


def test_validate_country_invalid():
    node = {
        'country': {
            '@id': 'random-term'
        }
    }
    assert validate_country(node) == {
        'level': 'error',
        'dataPath': '.country',
        'message': 'must be a country'
    }

    node = {
        'country': {
            '@id': 'GADM-IDN.1_1'
        }
    }
    assert validate_country(node) == {
        'level': 'error',
        'dataPath': '.country',
        'message': 'must be a country'
    }


def test_validate_region_in_country_valid():
    node = {
        'country': {
            '@id': 'GADM-AUS',
            'name': 'Australia'
        },
        'region': {
            '@id': 'GADM-AUS.1_1'
        }
    }
    assert validate_region_in_country(node) is True


def test_validate_region_in_country_invalid():
    node = {
        'country': {
            '@id': 'GADM-AUS',
            'name': 'Australia'
        },
        'region': {
            '@id': 'GADM-FRA.1_1'
        }
    }
    assert validate_region_in_country(node) == {
        'level': 'error',
        'dataPath': '.region',
        'message': 'must be within the country',
        'params': {
            'country': 'Australia'
        }
    }


def test_validate_is_region_valid():
    node = {
        'region': {
            '@id': 'GADM-FRA.1_1'
        }
    }
    assert validate_is_region(node) is True


def test_validate_is_region_invalid():
    node = {
        'region': {
            '@id': 'GADM-FRA'
        }
    }
    assert validate_is_region(node) == {
        'level': 'error',
        'dataPath': '.region',
        'message': 'must not be a country'
    }


def test_validate_list_country_region_valid():
    with open(f"{fixtures_folder}/list-country-region/valid.json") as f:
        node = json.load(f)
    assert validate_list_country_region(node, 'inputs') is True


def test_validate_list_country_region_invalid():
    with open(f"{fixtures_folder}/list-country-region/invalid.json") as f:
        node = json.load(f)
    assert validate_list_country_region(node, 'inputs') == [
        {
            'level': 'error',
            'dataPath': '.inputs[0].country',
            'message': 'must be a country'
        },
        {
            'level': 'error',
            'dataPath': '.inputs[0].region',
            'message': 'must not be a country'
        },
        {
            'level': 'error',
            'dataPath': '.inputs[0].region',
            'message': 'must be within the country',
            'params': {
                'country': None
            }
        }
    ]


def test_validate_area_valid():
    node = {'area': 4, 'boundaryArea': 4}
    assert validate_area(node) is True


def test_validate_area_invalid():
    node = {'area': 4, 'boundaryArea': 5}
    assert validate_area(node) == {
        'level': 'warning',
        'dataPath': '.area',
        'message': 'should be equal to boundary',
        'params': {
            'current': 4,
            'expected': 5,
            'delta': 20,
            'threshold': 0.05
        }
    }


@patch(f"{class_path}.get_region_id", return_value='GADM-GBR')
def test_validate_coordinates_valid(*args):
    with open(f"{fixtures_folder}/coordinates/valid.json") as f:
        node = json.load(f)
    assert validate_coordinates(node) is True


@patch(f"{class_path}.get_region_distance", return_value=5)
@patch(f"{class_path}.get_region_id", return_value='GADM-GBR')
def test_validate_coordinates_invalid(*args):
    with open(f"{fixtures_folder}/coordinates/invalid.json") as f:
        node = json.load(f)
    assert validate_coordinates(node) == {
        'level': 'error',
        'dataPath': '.country',
        'message': 'does not contain latitude and longitude',
        'params': {
            'current': 'GADM-FRA',
            'expected': 'GADM-GBR',
            'distance': 5
        }
    }


@patch(f"{class_path}.gee_is_enabled", return_value=True)
def test_need_validate_coordinates(*args):
    node = {}
    assert not need_validate_coordinates(node)

    node['latitude'] = 0
    node['longitude'] = 0
    assert need_validate_coordinates(node) is True


def test_validate_list_term_percent_valid():
    with open(f"{fixtures_folder}/unit-percent/valid.json") as f:
        node = json.load(f)
    assert validate_list_term_percent(node, 'measurements') is True


def test_validate_list_term_percent_invalid():
    with open(f"{fixtures_folder}/unit-percent/invalid.json") as f:
        node = json.load(f)
    assert validate_list_term_percent(node, 'measurements') == {
        'level': 'error',
        'dataPath': '.measurements[0].value',
        'message': 'should be between 0 and 100 (percentage)'
    }


def test_validate_list_term_percent_warning():
    with open(f"{fixtures_folder}/unit-percent/warning.json") as f:
        node = json.load(f)
    assert validate_list_term_percent(node, 'measurements') == [{
        'level': 'warning',
        'dataPath': '.measurements[0].value',
        'message': 'may be between 0 and 100'
    }, {
        'level': 'warning',
        'dataPath': '.measurements[1].value',
        'message': 'may be between 0 and 100'
    }]


def test_validate_empty_fields_valid():
    node = {
        'value': 'correct string'
    }
    assert validate_empty_fields(node) == []


def test_validate_empty_fields_warning():
    node = {
        'value1': 'N/A',
        'value2': 'no data',
        'test': None
    }
    assert validate_empty_fields(node) == [{
        'level': 'warning',
        'dataPath': '.value1',
        'message': 'may not be empty'
    }, {
        'level': 'warning',
        'dataPath': '.value2',
        'message': 'may not be empty'
    }]


def test_validate_private_has_source_valid():
    # valid if public
    node = {'dataPrivate': False}
    assert validate_private_has_source(node, 'source') is True

    # valid if private and with Source
    node = {
        'source': {
            'type': 'Source',
            'id': '1'
        },
        'dataPrivate': True
    }
    assert validate_private_has_source(node, 'source') is True


def test_validate_private_has_source_warning():
    node = {'dataPrivate': True}
    assert validate_private_has_source(node, 'source') == {
        'level': 'warning',
        'dataPath': '.dataPrivate',
        'message': 'should add a source',
        'params': {
            'current': 'source'
        }
    }


def test_validate_linked_source_privacy_valid():
    node = {
        'source': {
            'type': 'Source',
            'id': '1'
        },
        'dataPrivate': True
    }
    # valid if no connected source
    assert validate_linked_source_privacy(node, 'source') is True

    source = {
        'type': 'Source',
        'id': '1',
        'dataPrivate': True
    }
    assert validate_linked_source_privacy(node, 'source', _group_nodes([source])) is True

    node['dataPrivate'] = False
    source['dataPrivate'] = False
    assert validate_linked_source_privacy(node, 'source', _group_nodes([source])) is True


def test_validate_linked_source_privacy_invalid():
    node = {
        'source': {
            'type': 'Source',
            'id': '1'
        },
        'dataPrivate': False
    }
    source = {
        'type': 'Source',
        'id': '1',
        'dataPrivate': True
    }
    assert validate_linked_source_privacy(node, 'source', _group_nodes([source])) == {
        'level': 'error',
        'dataPath': '.dataPrivate',
        'message': 'should have the same privacy as the related source',
        'params': {
            'dataPrivate': False,
            'source': {
                'dataPrivate': True
            }
        }
    }

    node['dataPrivate'] = True
    source['dataPrivate'] = False
    assert validate_linked_source_privacy(node, 'source', _group_nodes([source])) == {
        'level': 'error',
        'dataPath': '.dataPrivate',
        'message': 'should have the same privacy as the related source',
        'params': {
            'dataPrivate': True,
            'source': {
                'dataPrivate': False
            }
        }
    }


@patch(f"{class_path}.find_linked_node")
def test_validate_linked_source_privacy_indexed(mockfind_linked_node):
    node = {
        'source': {
            '@type': 'Source',
            '@id': '1'
        },
        'dataPrivate': True
    }
    mockfind_linked_node.return_value = {'dataPrivate': True}
    assert validate_linked_source_privacy(node, 'source') is True

    mockfind_linked_node.return_value = {'dataPrivate': False}
    assert validate_linked_source_privacy(node, 'source') == {
        'level': 'error',
        'dataPath': '.dataPrivate',
        'message': 'should have the same privacy as the related source',
        'params': {
            'dataPrivate': True,
            'source': {
                'dataPrivate': False
            }
        }
    }


def test_validate_date_lt_today_valid():
    key = 'date'
    assert validate_date_lt_today({key: '2000-01-01'}, key) is True
    assert validate_date_lt_today({key: '2022'}, key) is True
    assert validate_date_lt_today({'test': {key: '2022'}}, f"test.{key}") is True


def test_validate_date_lt_today_invalid():
    key = 'date'
    node = {key: '2500-01-01'}
    assert validate_date_lt_today(node, key) == {
        'level': 'error',
        'dataPath': '.date',
        'message': 'must be before today'
    }


def test_validate_list_date_lt_today_valid():
    node = {
        'list': [
            {
                'date1': '2001-01-01'
            },
            {
                'date2': '2002-01-01'
            }
        ]
    }
    keys = ['date1', 'date2', 'date3']
    assert validate_list_date_lt_today(node, 'list', keys) is True


def test_validate_list_date_lt_today_invalid():
    node = {
        'list': [
            {
                'date1': '2001-01-01'
            },
            {
                'date2': '2500-01-01'
            }
        ]
    }
    keys = ['date1', 'date2', 'date3']
    assert validate_list_date_lt_today(node, 'list', keys) == {
        'level': 'error',
        'dataPath': '.list[1].date2',
        'message': 'must be before today'
    }


def test_value_difference():
    assert value_difference(125, 100) == 0.25
    assert value_difference(75, 100) == 0.25
    assert value_difference(0, 50) == 1
    assert value_difference(50, 0) == 0
    assert value_difference(67.0, 52.87673036) == 0.2671


def test_is_value_different():
    # default detla is 5%
    assert is_value_different(106, 100) is True
    assert not is_value_different(105, 100)

    assert is_value_different(111, 100, 0.1) is True
    assert not is_value_different(110, 100, 0.1)


@patch('hestia_earth.models.utils.property.get_node_property', return_value=None)
def test_validate_list_model_valid(*args):
    # validating Cycle.emissions
    with open(f"{fixtures_folder}/model/emissions/valid.json") as f:
        cycle = json.load(f)
    assert validate_list_model(cycle, 'emissions') is True

    with open(f"{fixtures_folder}/model/emissions/valid-variable-tolerance.json") as f:
        cycle = json.load(f)
    assert validate_list_model(cycle, 'emissions') is True

    # validating ImpactAssessment.impacts
    with open(f"{fixtures_folder}/model/impacts/valid.json") as f:
        impact = json.load(f)
    assert validate_list_model(impact, 'impacts') is True


@patch('hestia_earth.models.utils.property.get_node_property', return_value=None)
def test_validate_list_model_invalid(*args):
    # validating Cycle.emissions
    with open(f"{fixtures_folder}/model/emissions/invalid.json") as f:
        cycle = json.load(f)
    assert validate_list_model(cycle, 'emissions') == {
        'level': 'error',
        'dataPath': '.emissions[0].value',
        'message': 'the value provided is not consistent with the model result',
        'params': {
            'model': {
                '@type': 'Term',
                '@id': 'ipcc2019',
                'name': 'IPCC (2019)',
                'termType': 'model'
            },
            'term': {
                '@type': 'Term',
                '@id': 'co2ToAirUreaHydrolysis',
                'name': 'CO2, to air, urea hydrolysis',
                'units': 'kg CO2',
                'termType': 'emission'
            },
            'current': 200,
            'expected': 157.1,
            'delta': 27.310000000000002,
            'threshold': 0.05
        }
    }

    # validating ImpactAssessment.impacts
    with open(f"{fixtures_folder}/model/impacts/invalid.json") as f:
        impact = json.load(f)
    assert validate_list_model(impact, 'impacts') == {
        "level": "error",
        "dataPath": ".impacts[0].value",
        "message": "the value provided is not consistent with the model result",
        "params": {
            "model": {
                "@type": "Term",
                "@id": "ipcc2013IncludingFeedbacks",
                "name": "IPCC (2013) including feedbacks",
                "termType": "model"
            },
            "term": {
                "@type": "Term",
                "@id": "gwp100",
                "name": "GWP100",
                "units": "kg CO2eq",
                "termType": "characterisedIndicator"
            },
            "current": 5,
            "expected": 0.06419170939,
            "delta": 7689.17,
            'threshold': 0.05
        }
    }


def test_validate_list_model_config_valid():
    # validating Cycle.products
    with open(f"{fixtures_folder}/model/products/valid.json") as f:
        data = json.load(f)
    assert validate_list_model_config(data, 'products', PRODUCTS_MODEL_CONFIG) is True

    # missing value should skip validation
    with open(f"{fixtures_folder}/model/products/valid-no-value.json") as f:
        data = json.load(f)
    assert validate_list_model_config(data, 'products', PRODUCTS_MODEL_CONFIG) is True

    # validating Cycle.inputs
    with open(f"{fixtures_folder}/model/inputs/valid.json") as f:
        data = json.load(f)
    assert validate_list_model_config(data, 'inputs', INPUTS_MODEL_CONFIG) is True

    # missing value should skip validation
    with open(f"{fixtures_folder}/model/inputs/valid-no-value.json") as f:
        data = json.load(f)
    assert validate_list_model_config(data, 'inputs', INPUTS_MODEL_CONFIG) is True


def test_validate_list_model_config_invalid():
    # validating Cycle.products
    with open(f"{fixtures_folder}/model/products/warning.json") as f:
        data = json.load(f)
    assert validate_list_model_config(data, 'products', PRODUCTS_MODEL_CONFIG) == {
        'level': 'warning',
        'dataPath': '.products[1].value',
        'message': 'the value provided is not consistent with the model result',
        'params': {
            'model': {
                '@type': 'Term',
                '@id': 'ipcc2006',
                'name': 'IPCC (2006)',
                'termType': 'model'
            },
            'term': {
                '@type': 'Term',
                'name': 'Above Ground Crop Residue Total',
                '@id': 'aboveGroundCropResidueTotal'
            },
            'current': 150,
            'expected': 3451.52155,
            'delta': 95.65,
            'threshold': 0.5
        }
    }

    # validating Cycle.inputs
    with open(f"{fixtures_folder}/model/inputs/warning.json") as f:
        data = json.load(f)
    assert validate_list_model_config(data, 'inputs', INPUTS_MODEL_CONFIG) == {
        'level': 'warning',
        'dataPath': '.inputs[0].value',
        'message': 'the value provided is not consistent with the model result',
        'params': {
            'model': {
                '@type': 'Term',
                '@id': 'pooreNemecek2018',
                'name': 'Poore & Nemecek (2018)',
                'termType': 'model'
            },
            'term': {
                '@type': 'Term',
                'name': 'Saplings, depreciated amount per Cycle',
                '@id': 'saplingsDepreciatedAmountPerCycle'
            },
            'current': 8.25,
            'expected': 16.5,
            'delta': 50,
            'threshold': 0.25
        }
    }


def test_validate_properties_same_length_valid():
    with open(f"{fixtures_folder}/properties-same-length/valid.json") as f:
        data = json.load(f)
    assert validate_properties_same_length(data, 'products', 'endDate', ['startDate']) is True

    cycle = {'products': [{'endDate': '2019'}]}
    assert validate_properties_same_length(cycle, 'products', 'endDate', ['startDate']) is True

    cycle = {'products': [{'startDate': '2019'}]}
    assert validate_properties_same_length(cycle, 'products', 'endDate', ['startDate']) is True


def test_validate_properties_same_length_invalid():
    with open(f"{fixtures_folder}/properties-same-length/invalid.json") as f:
        data = json.load(f)
    assert validate_properties_same_length(data, 'products', 'endDate', ['startDate']) == {
        'level': 'error',
        'dataPath': '.products[1].startDate',
        'message': 'must have the same length as endDate'
    }


def test_validate_list_duplicate_values_valid():
    with open(f"{fixtures_folder}/properties-duplicate-values/valid.json") as f:
        data = json.load(f)
    assert validate_list_duplicate_values(data, 'practices', 'term.termType', 'excretaManagement') is True


def test_validate_list_duplicate_values_invalid():
    with open(f"{fixtures_folder}/properties-duplicate-values/invalid.json") as f:
        data = json.load(f)
    prop = 'term.termType'
    value = 'excretaManagement'
    assert validate_list_duplicate_values(data, 'practices', prop, value) == {
        'level': 'error',
        'dataPath': f".practices[1].{prop}",
        'message': f"must have only one entry with the same {prop} = {value}"
    }


def test_validate_nodes_duplicates_valid():
    with open(f"{fixtures_folder}/data-duplicates/valid.json") as f:
        nodes = json.load(f)
    assert validate_nodes_duplicates(nodes[0], _hash_nodes(nodes)) == []


def test_validate_nodes_duplicates_invalid():
    with open(f"{fixtures_folder}/data-duplicates/warning.json") as f:
        nodes = json.load(f)
    assert validate_nodes_duplicates(nodes[0], _hash_nodes(nodes)) == [{
        'level': 'warning',
        'dataPath': '',
        'message': 'might be a duplicate of the Site with id 2'
    }]


def test_validate_boundary_area_valid():
    # no area => valid
    assert validate_boundary_area({}) is True

    area = 5000
    assert validate_boundary_area({'boundaryArea': area}) is True


def test_validate_boundary_area_warning():
    area = 520000
    assert validate_boundary_area({'boundaryArea': area}) == {
        'level': 'warning',
        'dataPath': '.boundaryArea',
        'message': 'should be lower than max size',
        'params': {
            'current': 5200,
            'expected': 5000
        }
    }


@patch(f"{class_path}.gee_is_enabled", return_value=True)
def test_need_validate_region_size(*args):
    node = {}
    assert not need_validate_region_size(node)

    node['region'] = 'GADM'
    assert need_validate_region_size(node) is True

    node['latitude'] = 10
    node['longitude'] = 10
    assert not need_validate_region_size(node)


@patch('hestia_earth.earth_engine.gadm.get_size_km2', return_value=2500)
@patch(f"{class_path}.download_hestia")
def test_validate_region_size_valid(mock_download, *args):
    # no region => valid
    assert validate_region_size({}) is True

    # with region without download => valid
    assert validate_region_size({'area': 2500}) is True

    # with region and download => valid
    data = {'region': {'@id': 'GADM-FRA'}}
    mock_download.return_value = {'area': 2500}
    assert validate_region_size(data) is True


@patch('hestia_earth.earth_engine.gadm.get_size_km2', return_value=10000)
@patch(f"{class_path}.download_hestia", return_value={})
def test_validate_region_size_warning(*args):
    assert validate_region_size({'country': {'@id': True}}) == {
        'level': 'warning',
        'dataPath': '.country',
        'message': 'should be lower than max size',
        'params': {
            'current': 10000,
            'expected': 5000
        }
    }


def test_validate_duplicated_term_units_valid():
    # no blank nodes should be valid
    assert validate_duplicated_term_units({}, 'inputs', [TermTermType.ORGANICFERTILISER]) is True

    with open(f"{fixtures_folder}/duplicated-term-units/valid.json") as f:
        data = json.load(f)
    assert validate_duplicated_term_units(data, 'inputs', [TermTermType.ORGANICFERTILISER]) is True


def test_validate_duplicated_term_units_invalid():
    with open(f"{fixtures_folder}/duplicated-term-units/invalid-organicFertiliser.json") as f:
        data = json.load(f)
    assert validate_duplicated_term_units(data, 'inputs', [TermTermType.ORGANICFERTILISER]) == [
        {
            'level': 'warning',
            'dataPath': '.inputs[0].term',
            'message': 'should not use identical terms with different units',
            'params': {
                'term': {
                    '@type': 'Term',
                    '@id': 'bloodMealKgMass',
                    'termType': TermTermType.ORGANICFERTILISER.value,
                    'units': 'kg'
                },
                'units': ['kg', 'kg N']
            }
        },
        {
            'level': 'warning',
            'dataPath': '.inputs[1].term',
            'message': 'should not use identical terms with different units',
            'params': {
                'term': {
                    '@type': 'Term',
                    '@id': 'bloodMealKgN',
                    'termType': TermTermType.ORGANICFERTILISER.value,
                    'units': 'kg N'
                },
                'units': ['kg', 'kg N']
            }
        }
    ]

    with open(f"{fixtures_folder}/duplicated-term-units/invalid-animalProduct.json") as f:
        data = json.load(f)
    assert validate_duplicated_term_units(data, 'products', [TermTermType.ANIMALPRODUCT]) == [
        {
            'level': 'warning',
            'dataPath': '.products[0].term',
            'message': 'should not use identical terms with different units',
            'params': {
                'term': {
                    '@type': 'Term',
                    '@id': 'meatChickenLiveweight',
                    'termType': TermTermType.ANIMALPRODUCT.value,
                    'units': 'kg liveweight'
                },
                'units': ['kg liveweight', 'kg cold carcass weight']
            }
        },
        {
            'level': 'warning',
            'dataPath': '.products[1].term',
            'message': 'should not use identical terms with different units',
            'params': {
                'term': {
                    '@type': 'Term',
                    '@id': 'meatChickenColdCarcassWeight',
                    'termType': TermTermType.ANIMALPRODUCT.value,
                    'units': 'kg cold carcass weight'
                },
                'units': ['kg liveweight', 'kg cold carcass weight']
            }
        }
    ]


def test_validate_list_sum_100_percent_valid():
    # no practices should be valid
    cycle = {'practices': []}
    assert validate_list_sum_100_percent(cycle, 'practices') is True

    with open(f"{fixtures_folder}/list-values-sum-100/practices/total-90.json") as f:
        cycle = json.load(f)
    assert validate_list_sum_100_percent(cycle, 'practices') is True

    with open(f"{fixtures_folder}/list-values-sum-100/practices/total-100.json") as f:
        cycle = json.load(f)
    assert validate_list_sum_100_percent(cycle, 'practices') is True

    # missing element same depthUpper / depthLower
    with open(f"{fixtures_folder}/list-values-sum-100/measurements/missing-soil.json") as f:
        site = json.load(f)
    assert validate_list_sum_100_percent(site, 'measurements') is True

    # simple no depth
    with open(f"{fixtures_folder}/list-values-sum-100/measurements/no-depth-valid.json") as f:
        site = json.load(f)
    assert validate_list_sum_100_percent(site, 'measurements') is True

    with open(f"{fixtures_folder}/list-values-sum-100/management/with-properties/valid.json") as f:
        site = json.load(f)
    assert validate_list_sum_100_percent(site, 'management') is True


def test_validate_list_sum_100_percent_invalid():
    with open(f"{fixtures_folder}/list-values-sum-100/practices/total-110.json") as f:
        cycle = json.load(f)
    assert validate_list_sum_100_percent(cycle, 'practices') == [
        {
            'level': 'error',
            'dataPath': '.practices[0]',
            'message': 'value should sum to maximum 100 across all values',
            'params': {
                'sum': 110,
                'max': 100.5,
                'termIds': ['residueIncorporated', 'residueLeftOnField']
            }
        },
        {
            'level': 'error',
            'dataPath': '.practices[1]',
            'message': 'value should sum to maximum 100 across all values',
            'params': {
                'sum': 110,
                'max': 100.5,
                'termIds': ['residueIncorporated', 'residueLeftOnField']
            }
        }
    ]

    # 90% on same depthUpper / depthLower
    with open(f"{fixtures_folder}/list-values-sum-100/measurements/with-depth-high-value.json") as f:
        site = json.load(f)
    assert validate_list_sum_100_percent(site, 'measurements') == [
        {
            'level': 'error',
            'dataPath': '.measurements[1]',
            'message': 'value should sum to maximum 100 across all values',
            'params': {
                'sum': 110,
                'max': 100.5,
                'termIds': ['sandContent', 'siltContent', 'clayContent']
            }
        },
        {
            'level': 'error',
            'dataPath': '.measurements[2]',
            'message': 'value should sum to maximum 100 across all values',
            'params': {
                'sum': 110,
                'max': 100.5,
                'termIds': ['sandContent', 'siltContent', 'clayContent']
            }
        },
        {
            'level': 'error',
            'dataPath': '.measurements[3]',
            'message': 'value should sum to maximum 100 across all values',
            'params': {
                'sum': 110,
                'max': 100.5,
                'termIds': ['sandContent', 'siltContent', 'clayContent']
            }
        }
    ]

    # remove all depthUpper / depthLower
    with open(f"{fixtures_folder}/list-values-sum-100/measurements/no-depth-high-value.json") as f:
        site = json.load(f)
    assert validate_list_sum_100_percent(site, 'measurements') == [
        {
            'level': 'error',
            'dataPath': '.measurements[0]',
            'message': 'value should sum to maximum 100 across all values',
            'params': {
                'sum': 120,
                'max': 100.5,
                'termIds': ['sandContent', 'siltContent', 'clayContent']
            }
        },
        {
            'level': 'error',
            'dataPath': '.measurements[1]',
            'message': 'value should sum to maximum 100 across all values',
            'params': {
                'sum': 120,
                'max': 100.5,
                'termIds': ['sandContent', 'siltContent', 'clayContent']
            }
        },
        {
            'level': 'error',
            'dataPath': '.measurements[2]',
            'message': 'value should sum to maximum 100 across all values',
            'params': {
                'sum': 120,
                'max': 100.5,
                'termIds': ['sandContent', 'siltContent', 'clayContent']
            }
        }
    ]


_REQUIRES_VALUE_TERM_TYPES = [TermTermType.CROPRESIDUEMANAGEMENT]


def test_validate_list_percent_requires_value_valid():
    # no practices should be valid
    cycle = {'practices': []}
    assert validate_list_percent_requires_value(cycle, 'practices', _REQUIRES_VALUE_TERM_TYPES) is True

    with open(f"{fixtures_folder}/list-percent-value/valid.json") as f:
        cycle = json.load(f)
    assert validate_list_percent_requires_value(cycle, 'practices', _REQUIRES_VALUE_TERM_TYPES) is True


def test_validate_list_percent_requires_value_invalid():
    with open(f"{fixtures_folder}/list-percent-value/invalid.json") as f:
        cycle = json.load(f)
    assert validate_list_percent_requires_value(cycle, 'practices', _REQUIRES_VALUE_TERM_TYPES) == {
        'level': 'error',
        'dataPath': '.practices[0]',
        'message': "should have required property 'value'",
        'params': {
            'term': {
                '@id': 'residueIncorporated',
                '@type': 'Term',
                'name': 'Residue incorporated',
                'termType': 'cropResidueManagement',
                'units': '%',
            },
            'missingProperty': 'value'
        }
    }


def test_validate_other_model_valid():
    with open(f"{fixtures_folder}/otherModel/valid.json") as f:
        cycle = json.load(f)
    assert validate_other_model(cycle, 'emissions') is True


def test_validate_other_model_invalid():
    with open(f"{fixtures_folder}/otherModel/invalid.json") as f:
        cycle = json.load(f)
    assert validate_other_model(cycle, 'emissions') == {
        'level': 'error',
        'dataPath': '.emissions[1].methodModel',
        'message': 'is required when using other model'
    }


def test_validate_list_valueType_valid():
    # blank nodes emtpy should be valid
    node = {'values': []}
    assert validate_list_valueType(node, 'values') is True

    with open(f"{fixtures_folder}/list-valueType/valid.json") as f:
        cycle = json.load(f)
    assert validate_list_valueType(cycle, 'practices') is True


def test_validate_list_valueType_invalid():
    with open(f"{fixtures_folder}/list-valueType/invalid.json") as f:
        cycle = json.load(f)
    assert validate_list_valueType(cycle, 'practices') == {
        'level': 'error',
        'dataPath': '.practices[0].value',
        'message': 'must be a number'
    }


@pytest.mark.parametrize(
    'node,expected',
    [
        (
            {'id': 'id', 'nested': {'id': 'id'}},
            True
        ),
        (
            {'@id': 'id', 'nested': {'@id': 'id'}},
            True
        ),
        (
            {'@id': 'id', 'nested': {'id': 'id'}},
            True
        ),
        (
            {'id': 'id', 'nested': {'@id': 'id'}},
            {
                'level': 'warning',
                'dataPath': '.nested.@id',
                'message': 'should not link to an existing node',
                'params': {
                    'node': {'@id': 'id'}
                }
            }
        ),
        (
            {'id': 'id', 'nested': [{'id': 'id'}, {'@id': 'id'}]},
            {
                'level': 'warning',
                'dataPath': '.nested[1].@id',
                'message': 'should not link to an existing node',
                'params': {
                    'node': {'@id': 'id'}
                }
            }
        ),
    ]
)
def test_validate_nested_existing_node(node: dict, expected):
    assert validate_nested_existing_node(node, 'nested') == expected
