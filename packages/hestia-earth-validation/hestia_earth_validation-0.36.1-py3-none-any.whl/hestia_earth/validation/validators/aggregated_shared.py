def validate_quality_score_min(node: dict, max_diff: int = 2):
    node_id = node.get('@id', node.get('id', ''))
    key = 'aggregatedQualityScore'
    value = node.get(key, 0)
    max_value = node.get(key + 'Max', 0)
    min_value = max_value - max_diff
    # ignore nodes that are organic or irrigated as they should not block the upload of other nodes
    level = 'warning' if any(['organic' in node_id, 'irrigated' in node_id]) else 'error'
    return value >= min_value or {
        'level': level,
        'dataPath': f".{key}",
        'message': f"must be at least equal to {min_value}",
        'params': {
            'expected': min_value,
            'current': value,
            'min': min_value,
            'max': max_value
        }
    }
