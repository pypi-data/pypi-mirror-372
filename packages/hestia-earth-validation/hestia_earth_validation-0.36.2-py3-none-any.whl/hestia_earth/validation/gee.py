import os
from hestia_earth.utils.tools import current_time_ms
from hestia_earth.schema import NodeType

from .log import logger

_ENABLED = os.getenv('VALIDATE_SPATIAL', 'true') == 'true'
_ENABLE_TYPES = [NodeType.SITE.value, NodeType.ORGANISATION.value]
MAX_AREA_SIZE = int(os.getenv('MAX_AREA_SIZE', '5000'))
_CACHE_BATCH_SIZE = int(os.getenv('CACHE_SITES_BATCH_SIZE', '5000'))

_caching = {}
_RASTERS = [
    {
        'name': 'siteType',
        'collection': 'MODIS/006/MCD12Q1',
        'band_name': 'LC_Prop2',
        'year': '2019'
    }
]
_VECTORS = [
    {
        'name': f"region-{level}",
        'collection': f"users/hestiaplatform/gadm36_{level}",
        'fields': f"GID_{level}"
    } for level in range(0, 6)
]


def _caching_key(func_name: str, args: dict):
    return '-'.join([func_name, str(args)])


def _run_with_cache(func_name: str, args: dict, func):
    global _caching  # noqa: F824
    key = _caching_key(func_name, args)
    _caching[key] = _caching.get(key, func())
    return _caching[key]


def _should_cache_node(node: dict):
    return all([
        node.get('@type', node.get('type')) in _ENABLE_TYPES,
        not node.get('aggregated', False),
        'latitude' in node and 'longitude' in node
    ])


def _node_key(node: dict): return '/'.join([node.get('type', node.get('@type')), node.get('id', node.get('@id'))])


def _pop_items(values: list, nb_items: int):
    if len(values) < nb_items:
        removed_items = values[:]  # Get a copy of the entire array
        values.clear()  # Remove all items from the original array
    else:
        removed_items = values[:nb_items]  # Get the first N items
        del values[:nb_items]  # Remove the first N items from the original array

    return removed_items


def _cache_nodes(nodes: list, batch_size: int):
    from hestia_earth.models.cache_sites import ParamType, _run_values

    now = current_time_ms()

    nodes_mapping = {_node_key(n): n for n in nodes}

    cache_nodes = list(filter(_should_cache_node, nodes))
    while len(cache_nodes) > 0:
        batch_values = _pop_items(cache_nodes, batch_size)
        logger.info(f"Caching {len(batch_values)} nodes. {len(cache_nodes)} remaining.")
        results = _run_values([
            (n, 0) for n in batch_values  # expecting tuple with area_size
        ], ParamType.COORDINATES, _RASTERS, _VECTORS, years=[])

        for result in results:
            nodes_mapping[_node_key(result)] = result

    logger.info('Done caching in %sms', current_time_ms() - now)

    return list(nodes_mapping.values())


def _init_gee_by_nodes(nodes: list):
    from hestia_earth.earth_engine import init_gee
    init_gee()
    try:
        return _cache_nodes(nodes, _CACHE_BATCH_SIZE)
    except Exception as e:
        logger.error(f"An error occured while caching nodes on EE: {str(e)}")
        if 'User memory limit exceeded' in str(e) or 'query aborted' in str(e):
            return _cache_nodes(nodes, 100)


def init_gee_by_nodes(nodes: list):
    # need to validate for non-aggregated Site or Oganisation with coordinates
    enabled_nodes = list(filter(_should_cache_node, nodes))
    should_init = len(enabled_nodes) > 0
    return _init_gee_by_nodes(nodes) if should_init and is_enabled() else nodes


def is_enabled():
    if _ENABLED:
        try:
            from hestia_earth.earth_engine.version import VERSION
            return isinstance(VERSION, str)
        except ImportError:
            logger.error("Run `pip install hestia_earth.earth_engine` to use geospatial validation")

    return False


def id_to_level(id: str): return id.count('.')


def get_cached_data(site: dict, key: str, year: int = None):
    from hestia_earth.models.geospatialDatabase.utils import _cached_value
    value = _cached_value(site, key)
    return value.get(str(year)) if value and year else value


def get_region_id(node: dict):
    level = id_to_level(node.get('region', node.get('country')).get('@id'))
    id = get_cached_data(node, f"region-{level}")
    return None if id is None else f"GADM-{id}"


def get_region_distance(gid: str, latitude: float, longitude: float):
    def exec_func():
        return round(get_distance_to_coordinates(gid, latitude=latitude, longitude=longitude) / 1000)

    try:
        from hestia_earth.earth_engine.gadm import get_distance_to_coordinates
        return _run_with_cache('get_region_distance',
                               {'gid': gid, 'latitude': latitude, 'longitude': longitude},
                               exec_func)
    except Exception:
        return None
