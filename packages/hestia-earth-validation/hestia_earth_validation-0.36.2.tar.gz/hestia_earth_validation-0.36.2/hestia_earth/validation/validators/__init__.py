import os
from hestia_earth.schema import SchemaType
from hestia_earth.utils.tools import flatten

from ..log import logger
from ..utils import update_error_path
from .shared import validate_empty_fields, validate_nodes_duplicates
from .cycle import validate_cycle
from .impact_assessment import validate_impact_assessment
from .organisation import validate_organisation
from .site import validate_site
from .source import validate_source

# disable validation based on `@type`
VALIDATE_EXISTING_NODES = os.getenv('VALIDATE_EXISTING_NODES', 'false') == 'true'
VALIDATE_TYPE = {
    SchemaType.CYCLE.value: lambda n, nodes: validate_cycle(n, nodes),
    SchemaType.IMPACTASSESSMENT.value: lambda n, nodes: validate_impact_assessment(n, nodes),
    SchemaType.ORGANISATION.value: lambda n, nodes: validate_organisation(n, nodes),
    SchemaType.SITE.value: lambda n, nodes: validate_site(n, nodes),
    SchemaType.SOURCE.value: lambda n, nodes: validate_source(n, nodes)
}
SKIP_VALIDATE_DUPLICATES = [
    SchemaType.ACTOR.value,
    SchemaType.IMPACTASSESSMENT.value,
    SchemaType.TERM.value
]


def _has_keys(node: dict):
    # ignore some keys that are automatically added to nested objects
    ignore_keys = ['type', 'id', '@type', '@id', 'name', 'description', 'siteType']
    node_keys = [k for k in list(node.keys()) if k not in ignore_keys]
    return len(node_keys) > 0


def _should_run(ntype: str, node: dict): return all([ntype in VALIDATE_TYPE, _has_keys(node)])


def _validate_node_type(node_by_type: dict, node_by_hash: dict, ntype: str, node: dict):
    should_run = _should_run(ntype, node)
    if should_run:
        logger.debug('Run validation on: type=%s, id=%s', ntype, node.get('id', node.get('@id')))
    validator = VALIDATE_TYPE.get(ntype)
    validations = validator(node, node_by_type) if should_run else []
    return validations + validate_empty_fields(node) + (
        [] if any([
            ntype in SKIP_VALIDATE_DUPLICATES,
            not should_run
        ]) else validate_nodes_duplicates(node, node_by_hash)
    )


def _validate_node_children(node_by_type: dict, node_by_hash: dict, node: dict):
    validations = []
    for key, value in node.items():
        if isinstance(value, list):
            validations.extend([
                _validate_node_child(node_by_type, node_by_hash, key, value, index) for index, value in enumerate(value)
            ])
        if isinstance(value, dict):
            validations.append(_validate_node_child(node_by_type, node_by_hash, key, value))
    return flatten(validations)


def _validate_node_child(node_by_type: dict, node_by_hash: dict, key: str, value: dict, index=None):
    values = validate_node(node_by_type, node_by_hash)(value)
    return list(map(lambda error: update_error_path(error, key, index) if isinstance(error, dict) else error, values))


def validate_node(node_by_type: dict = {}, node_by_hash: dict = {}):
    def validate(node: dict):
        """
        Validates a single Node.

        Parameters
        ----------
        node : dict
            The JSON-Node to validate.

        Returns
        -------
        List
            The list of errors/warnings for the node, which can be empty if no errors/warnings detected.
        """
        try:
            ntype = node.get(
                'type', node.get('@type') if VALIDATE_EXISTING_NODES else None
            ) if isinstance(node, dict) else None
            return [] if ntype is None else list(filter(lambda v: v is not True, flatten(
                _validate_node_type(node_by_type, node_by_hash, ntype, node) +
                _validate_node_children(node_by_type, node_by_hash, node)
            )))
        except Exception as e:
            logger.error(f"Error validating {ntype} with id '{node.get('id', node.get('@id'))}': {str(e)}")
            raise e
    return validate
