import json
from typing import List
from functools import reduce, lru_cache
from datetime import datetime
from hestia_earth.schema import NodeType, TermTermType, UNIQUENESS_FIELDS
from hestia_earth.utils.api import download_hestia
from hestia_earth.utils.lookup import download_lookup, get_table_value, column_name
from hestia_earth.utils.tools import list_average, safe_parse_date, non_empty_list, is_number, is_boolean, get_dict_key
from hestia_earth.utils.model import filter_list_term_type, find_primary_product

ANIMAL_TERM_TYPES = [
    TermTermType.LIVEANIMAL,
    TermTermType.LIVEAQUATICSPECIES
]


@lru_cache()
def _download_memory(lookup_name: str):
    return download_lookup(lookup_name)


@lru_cache()
def _get_term_lookup_value(term_id: str, term_type: str, column: str):
    lookup = _download_memory(f"{term_type}.csv")
    return get_table_value(lookup, 'termid', term_id, column_name(column))


def get_lookup_value(lookup_term: dict, column: str):
    value = _get_term_lookup_value(lookup_term.get('@id'), lookup_term.get('termType'), column) if lookup_term else None
    return value


def _next_error(values: list): return next((x for x in values if x is not True), True)


def _filter_list_errors(values: list, return_single=True):
    values = list(filter(lambda x: x is not True, values))
    return True if return_single and len(values) == 0 else (values[0] if return_single and len(values) == 1 else values)


def _list_except_item(values: list, item):
    try:
        idx = values.index(item)
        return values[:idx] + values[idx+1:]
    except ValueError:
        return values


def update_error_path(error: dict, key: str, index=None):
    path = f".{key}[{index}]{error.get('dataPath')}" if index is not None else f".{key}{error.get('dataPath')}"
    return error | {'dataPath': path}


def _safe_cast(val, to_type, default=None):
    try:
        return to_type(val)
    except (ValueError, TypeError):
        return default


def hash_dict(value: dict): return json.dumps(value, sort_keys=True)


def is_same_dict(a: dict, b: dict): return hash_dict(a) == hash_dict(b)


def _dict_without_key(a: dict, key: str):
    no_key = a.copy()
    if key in no_key:
        no_key.pop(key)
    return no_key


def _group_nodes(nodes: List[dict]):
    def group(groups: dict, node: dict):
        type = node.get('type')
        id = node.get('id')
        if type and id:
            groups[type] = groups.get(type, {})
            groups[type][id] = node
        return groups

    return reduce(group, nodes, {})


def _hash_nodes(nodes: List[dict]):
    def group(groups: dict, node: dict):
        type = node.get('type')
        id = node.get('id')
        if type and id:
            # store the hash of the node without the `id` for uniqueness check
            key = hash_dict(_dict_without_key(node, 'id'))
            groups[key] = groups.get(key, []) + [node]
        return groups

    return reduce(group, nodes, {})


def _list_sum(values: list, prop: str): return sum(map(lambda v: _safe_cast(v.get(prop, 0), float, 0.0), values))


def list_sum_terms(values: list, term_ids=[], default=None):
    average_values = non_empty_list([
        _value_average(node, default=default) for node in values if node.get('term', {}).get('@id') in term_ids
    ])
    return sum(average_values) if average_values else None


def _compare_values(x, y):
    return next((True for item in x if item in y), False) if isinstance(x, list) and isinstance(y, list) else x == y


def _same_properties(value: dict, props: List[str]):
    def identical(test: dict):
        same_values = list(filter(lambda x: _compare_values(get_dict_key(value, x), get_dict_key(test, x)), props))
        return test if len(same_values) == len(props) else None
    return identical


def _value_average(node: dict, default=0, key='value'):
    try:
        value = node.get(key)
        return list_average(value, default) if isinstance(value, list) else (value or default)
    except Exception:
        return default


def term_id_prefix(term_id: str): return term_id.split('Kg')[0]


def _download_linked_node(node: dict):
    data = download_hestia(node.get('@id'), node.get('@type')) if node.get('@id') and node.get('@type') else None
    return data if (data or {}).get('@id') == node.get('@id') else None


def find_linked_node(node_map: dict, node: dict):
    """
    Find the Node by type and id in the list of nodes.
    """
    return node_map.get(node.get('type'), {}).get(node.get('id')) or _download_linked_node(node)


def find_related_nodes(node_map: dict, node: dict, related_key: str, related_type: NodeType):
    """
    Find all nodes related to the same node via a key.
    Example: find all Cycles related to a Site via the key "site".

    Parameters
    ----------
    node_map : dict
        The list of all nodes to do cross-validation, grouped by `type` and `id`.
    node : dict
        The node the other nodes should be related to.
    related_key : str
        How the other nodes are related to the `node`.
    related_type : NodeType
        The type of the related nodes.

    Returns
    -------
    List[dict]
        The list of nodes related to the `node`.
    """
    node_id = node.get('@id', node.get('id'))
    nodes = node_map.get(related_type.value, {}).values()
    return [n for n in nodes if n.get(related_key).get('@id', n.get(related_key).get('id')) == node_id]


def _is_before_today(date: str): return safe_parse_date(date).date() <= datetime.now().date()


def _node_year(node: dict):
    date = node.get('endDate', node.get('startDate'))
    date = safe_parse_date(date) if date else None
    return date.year if date else None


def is_live_animal_cycle(cycle: dict):
    blank_nodes = cycle.get('animals', []) + cycle.get('products', [])
    animals = filter_list_term_type(blank_nodes, ANIMAL_TERM_TYPES)
    return len(animals) > 0


def contains_grazing_animals(cycle: dict):
    blank_nodes = cycle.get('animals', []) + cycle.get('products', [])
    animals = filter_list_term_type(blank_nodes, ANIMAL_TERM_TYPES)
    return any([
        v for v in animals if get_lookup_value(v.get('term', {}), 'isGrazingAnimal')
    ])


def _match_list_el(source: list, dest: list, key: str):
    src_values = non_empty_list([get_dict_key(x, key) for x in source])
    dest_values = non_empty_list([get_dict_key(x, key) for x in dest])
    return sorted(src_values) == sorted(dest_values)


def _match_el(source: dict, dest: dict, fields: list):
    def match(key: str):
        keys = key.split('.')
        is_list = len(keys) >= 2 and (
            isinstance(get_dict_key(source, keys[0]), list) or
            isinstance(get_dict_key(dest, keys[0]), list)
        )
        return _match_list_el(
            get_dict_key(source, keys[0]) or [],
            get_dict_key(dest, keys[0]) or [],
            '.'.join(keys[1:])
        ) if is_list else get_dict_key(source, key) == get_dict_key(dest, key)

    return all(map(match, fields))


def find_by_unique_product(node: dict, product: dict, list_key: str = 'products'):
    """
    Fallback to finding a product with unique keys if a single product has the same `term.@id`.
    """
    products = node.get(list_key, [])
    products = [p for p in products if _match_el(p, product, ['term.@id'])]
    return products[0] if len(products) == 1 else None


def find_by_product(node: dict, product: dict, list_key: str = 'products'):
    keys = UNIQUENESS_FIELDS.get(node.get('type', node.get('@type')), {}).get(list_key, ['term.@id'])
    products = node.get(list_key, [])
    return next((p for p in products if _match_el(p, product, keys)), None)


def is_same_product(p1: dict, p2: dict):
    return find_by_product({'type': NodeType.CYCLE.value, 'products': [p1]}, p2)


def _formatDepth(depth: str):
    # handle float values
    return str(int(depth)) if is_number(depth) else ''


def blank_node_properties_group(blank_node: dict):
    def property_group(property: dict):
        return get_lookup_value(property.get('term', {}), 'blankNodesGroup')

    properties = blank_node.get('properties', [])
    return '-'.join(non_empty_list(map(property_group, properties)))


def _blank_node_sum_groups(blank_node: dict, allow_sum_100: bool = True):
    term = blank_node.get('term', {})
    sum_below_100_group = get_lookup_value(term, 'sumMax100Group')
    sum_equal_100_group = get_lookup_value(term, 'sumIs100Group')

    return {
        'sumMax100Group': sum_below_100_group or (sum_equal_100_group if not allow_sum_100 else None),
        'sumIs100Group': sum_equal_100_group if allow_sum_100 else None
    }


def group_blank_nodes(nodes: list, by_sum: bool = True):
    """
    Group a list of blank nodes using:
    - the `depthUpper`, `depthLower`, `startDate`, `endDate`, `dates`
    - the lookup group `sumMax100Group` or `sumIs100Group` if specified
    - the lookup group `blankNodesGroup` on properties if any

    Parameters
    ----------
    nodes : list
        List of blank nodes with their index.
    by_sum : bool
        Group blank nodes using the key to sum to 100% (`sumMax100Group` and `sumIs100Group`).
    """
    def group_by(group: dict, values: tuple):
        index, blank_node = values
        properties_group = blank_node_properties_group(blank_node)
        # note: grouping of `properties` disables the grouping == 100
        sum_groups = _blank_node_sum_groups(blank_node, allow_sum_100=not properties_group)
        keys = non_empty_list([
            _formatDepth(blank_node.get('depthUpper', '')),
            _formatDepth(blank_node.get('depthLower', '')),
            blank_node.get('startDate'),
            blank_node.get('endDate'),
            '-'.join(blank_node.get('dates') or []),
            properties_group
        ] + (list(sum_groups.values()) if by_sum else []))
        key = '-'.join(keys) if len(keys) > 0 else 'default'

        if not by_sum or all([
            blank_node.get('value', []),
            any(list(sum_groups.values()))
        ]):
            group[key] = group.get(key, []) + [{
                'index': index,
                'node': blank_node
            } | (sum_groups if by_sum else {})]

        return group

    return reduce(group_by, nodes, {})


def is_permanent_crop(cycle: dict):
    product = find_primary_product(cycle) or {}
    return get_lookup_value(product.get('term', {}), 'cropGroupingFAO') == 'Permanent crops'


def term_valueType(term: dict): return get_lookup_value(term, 'valueType')


VALUE_TYPE_MATCH = {
    'number': is_number,
    'boolean': is_boolean
}


def match_value_type(value_type: str, value):
    values = non_empty_list(value if isinstance(value, list) else [value])
    return all([
        VALUE_TYPE_MATCH.get(value_type, lambda _: True)(v) for v in values
    ])
