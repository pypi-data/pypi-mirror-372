from pkgutil import extend_path
from typing import List
from concurrent.futures import ThreadPoolExecutor
from hestia_earth.utils.tools import current_time_ms

from .log import logger
from .validators import validate_node
from .utils import _group_nodes, _hash_nodes
from .gee import init_gee_by_nodes

__path__ = extend_path(__path__, __name__)


def validate(nodes: List[dict]):
    """
    Validates a list of HESTIA JSON-Nodes against a list of rules.

    Parameters
    ----------
    nodes : List[dict]
        The list of JSON-Nodes to validate.

    Returns
    -------
    List
        The list of errors for each node, which can be empty if no errors detected.
    """
    now = current_time_ms()
    nodes = init_gee_by_nodes(nodes)
    nodes_by_type = _group_nodes(nodes)
    nodes_by_hash = _hash_nodes(nodes)
    with ThreadPoolExecutor() as executor:
        results = list(executor.map(validate_node(nodes_by_type, nodes_by_hash), nodes))
    logger.info('time=%s, unit=ms', current_time_ms() - now)
    return results
