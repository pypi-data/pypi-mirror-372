import importlib
import os
from functools import lru_cache
from hestia_earth.utils.tools import list_sum

from .log import logger

ENABLED = os.getenv('VALIDATE_MODELS', 'true') == 'true'


@lru_cache()
def is_enabled():
    if ENABLED:
        try:
            from hestia_earth.models.version import VERSION
            logger.debug("Using models version %s", VERSION)
            return True
        except ImportError:
            logger.error("Run `pip install hestia_earth.models` to use models validation")

    return False


def _model_value_from_list(results: list, default_value: float):
    return results[0].get('value', [default_value]) if len(results) > 0 else default_value


def _model_value(result, default_value=0):
    return default_value if result is None else (
        _model_value_from_list(result, default_value) if isinstance(result, list) else (
            result.get('value', [default_value]) if isinstance(result, dict) else default_value
        )
    )


def value_from_model(result):
    value = _model_value(result)
    try:
        # fix numpy.float64
        # TODO: find a better way to handle this
        return list_sum(value, float(value))
    except Exception:
        return list_sum(value, value)


def method_tier_from_model(result):
    return None if result is None else (
        method_tier_from_model(result[0]) if isinstance(result, list) and len(result) > 0 else (
            result.get('methodTier') if isinstance(result, dict) else None
        )
    )


def _import_model(name: str):
    return importlib.import_module(f"hestia_earth.models.{name}").run


def run_model(model: str, term_id: str, data: dict):
    """
    Run a HESTIA model from the engine models library.

    Parameters
    ----------
    model : str
        The name of the model to run.
    term_id : str
        The term to run the model on.
    data : dict
        The data used to run the model.

    Returns
    -------
    Any
        The result of the model, which can be a single `dict` or a list of `dict`s.
    """
    return _import_model(model)(term_id, data)


def run_model_from_node(node: dict, data: dict):
    """
    Run a HESTIA model from the engine models library.
    To use this function, you need to use a Blank Node that contains a `methodModel` and a `term`,
    otherwise you need to use the `run_model` method.

    Parameters
    ----------
    node : dict
        The Blank Node containing a `methodModel` and a `Term`.
    data : dict
        The data used to run the model.

    Returns
    -------
    Any
        The result of the model, which can be a single `dict` or a list of `dict`s.
    """
    methodModel = node.get('methodModel', {}).get('@id')
    term_id = node.get('term', {}).get('@id')
    return run_model(methodModel, term_id, data)


def run_models(node: dict, models: list):
    """
    Run a list of models, using the orchestrator, and return the updated node.

    Parameters
    ----------
    node : dict
        The Blank Node containing a `methodModel` and a `Term`.
    models : list
        List of models as defined in the orchestrator configurations.

    Returns
    -------
    Any
        The recalculated node after running all models
    """
    try:
        from hestia_earth.orchestrator import run
        return run(node, {'models': models})
    except Exception as e:
        logger.error(f"Error running models: {str(e)}")
        return node
