from .shared import (
    validate_date_lt_today
)


def validate_source(source: dict, node_map: dict = {}):
    """
    Validates a single `Source`.

    Parameters
    ----------
    organisation : dict
        The `Source` to validate.
    node_map : dict
        The list of all nodes to do cross-validation, grouped by `type` and `id`.

    Returns
    -------
    List
        The list of errors for the `Source`, which can be empty if no errors detected.
    """
    return [
        validate_date_lt_today(source, 'bibliography.year')
    ]
