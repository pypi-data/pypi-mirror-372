from unittest.mock import patch
import json
from hestia_earth.schema import NodeType

from tests.utils import fixtures_path
from hestia_earth.validation.validators import validate_node, _should_run

class_path = 'hestia_earth.validation.validators'


def test_should_run():
    ntype = NodeType.CYCLE.value
    node = {
        '@type': ntype,
        '@id': 'cycle'
    }
    assert not _should_run(ntype, node)

    node = {
        '@type': ntype,
        '@id': 'cycle',
        'name': 'Cycle 1'
    }
    assert not _should_run(ntype, node)

    node = {
        '@type': ntype,
        '@id': 'cycle',
        'name': 'Cycle 1',
        'endDate': '2020-01-01'
    }
    assert _should_run(ntype, node) is True


@patch(f"{class_path}.validate_site")
def test_validate_node_type_validation(mock_validate_site):
    node = {'type': NodeType.SITE.value, 'id': 'id', 'siteType': 'cropland', 'country': {'@id': 'GADM-GBR'}}
    validate_node()(node)
    mock_validate_site.assert_called_once()

    # no validation on existing nodes
    mock_validate_site.reset_mock()
    node = {'@type': NodeType.SITE.value}
    validate_node()(node)
    mock_validate_site.assert_not_called()


def test_validate_node_no_validation():
    # no validation on uploaded Actor
    node = {'type': NodeType.ACTOR.value}
    assert validate_node([])(node) == []


@patch(f"{class_path}.validate_cycle")
@patch(f"{class_path}.validate_impact_assessment")
@patch(f"{class_path}.validate_site")
def test_validate_nested(mock_validate_site, mock_validate_impact_assessment, mock_validate_cycle):
    with open(f"{fixtures_path}/impactAssessment/valid.json") as f:
        node = json.load(f)
    assert validate_node()(node) == []
    assert mock_validate_cycle.call_count == 1
    assert mock_validate_impact_assessment.call_count == 1
    assert mock_validate_site.call_count == 2
