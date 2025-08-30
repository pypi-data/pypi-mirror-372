import os
import json
from enum import Enum
from hestia_earth.schema import SchemaType, TermTermType
from hestia_earth.utils.api import search

CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
RESULTS_PATH = os.path.join(CURRENT_DIR, 'search-results.json')

_CACHE = {}


def _load_results(filepath: str) -> dict:
    with open(filepath) as f:
        return json.load(f)


class TERMS_QUERY(Enum):
    FUEL = TermTermType.FUEL.value
    CROP_RESIDUE = TermTermType.CROPRESIDUE.value
    MODEL = TermTermType.MODEL.value
    FORAGE = TermTermType.FORAGE.value
    RICE = 'rice'


_terms_query = {
    TERMS_QUERY.FUEL: {
        'should': [
            {
                'bool': {
                    'must': [
                        {'match': {'termType': TermTermType.FUEL.value}}
                    ],
                    'should': [
                        {'match': {'name': 'gasoline'}},
                        {'match': {'name': 'petrol'}},
                        {'match': {'name': 'diesel'}},
                    ],
                    'minimum_should_match': 1
                }
            }
        ],
        'minimum_should_match': 1
    },
    TERMS_QUERY.CROP_RESIDUE: {
        'should': [
            {'match': {'termType': TermTermType.CROPRESIDUE.value}}
        ],
        'minimum_should_match': 1
    },
    TERMS_QUERY.MODEL: {
        'should': [
            {'match': {'termType': TermTermType.MODEL.value}}
        ],
        'minimum_should_match': 1
    },
    TERMS_QUERY.FORAGE: {
        'should': [
            {'match': {'termType.keyword': TermTermType.CROP.value}},
            {'match': {'termType.keyword': TermTermType.FORAGE.value}},
            {'match': {'name': 'forage'}}
        ],
        'minimum_should_match': 2
    },
    TERMS_QUERY.RICE: {
        'should': [
            {'match': {'termType.keyword': TermTermType.CROP.value}},
            {'match': {'name': 'rice'}}
        ],
        'minimum_should_match': 2
    }
}


def _exec_query(query: dict) -> list[str]:
    terms = search({
        'bool': {
            'must': [{'match': {'@type': SchemaType.TERM.value}}]
        } | query
    }, limit=10000)
    return list(map(lambda n: n['@id'], terms))


def get_terms(query: TERMS_QUERY):
    return _CACHE.get(query.value) or _exec_query(_terms_query[query])


def get_all_terms():
    return {key.value: _exec_query(value) for key, value in _terms_query.items()}


def enable_mock(filepath: str):
    global _CACHE  # noqa: F824
    _CACHE = _load_results(filepath)
    return _CACHE
