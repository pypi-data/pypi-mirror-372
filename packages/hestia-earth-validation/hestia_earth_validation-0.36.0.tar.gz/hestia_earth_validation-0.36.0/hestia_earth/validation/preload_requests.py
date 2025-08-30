"""
Preload all search requests to avoid making the same searches many times while running models.
"""
import json
import os
from hestia_earth.utils.storage import _load_from_storage

from .log import logger
from .terms import RESULTS_PATH, get_all_terms, enable_mock


def _write_results(filepath: str, data: dict):
    with open(filepath, 'w') as f:
        f.write(json.dumps(data, ensure_ascii=False))


def _load_data_from_glossary():
    try:
        return json.loads(_load_from_storage(os.path.join('glossary', 'validation-search-results.json'), glossary=True))
    except Exception:
        return None


def enable_preload(
    filepath: str = RESULTS_PATH,
    overwrite_existing: bool = True,
    use_glossary: bool = False
):
    """
    Prefetch calls to HESTIA API in a local file.

    Parameters
    ----------
    filepath : str
        The path of the file containing the search results. Defaults to current library folder.
    overwrite_existing : bool
        Optional - If the file already exists, the file can be used instead of generating it again.
        Will overwrite by default.
    use_glossary : bool
        Optional - Try to fetch search results from the glossary.
        Only available with access to HESTIA infrastructure.
    """
    should_generate = overwrite_existing or not os.path.exists(filepath)

    if should_generate:
        logger.debug('Preloading search results and storing in %s', filepath)

        # build the search results
        data = (_load_data_from_glossary() if use_glossary else None) or get_all_terms()

        # store in file
        _write_results(filepath, data)

    # enable mock search results from file
    enable_mock(filepath=filepath)
