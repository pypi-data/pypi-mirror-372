import os
import math
from hestia_earth.distribution.utils.cycle import FERTILISER_COLUMNS, PESTICIDE_COLUMN, IRRIGATION_COLUMN, YIELD_COLUMN
from hestia_earth.distribution.posterior_fert import get_post as get_post_fert
from hestia_earth.distribution.prior_fert import get_prior as get_prior_fert
from hestia_earth.distribution.posterior_pest import get_post as get_post_pest
from hestia_earth.distribution.prior_pest import get_prior as get_prior_pest
from hestia_earth.distribution.posterior_irrigation import get_post as get_post_irri
from hestia_earth.distribution.prior_irrigation import get_prior as get_prior_irri
from hestia_earth.distribution.posterior_yield import get_post as get_post_yield
from hestia_earth.distribution.prior_yield import get_prior as get_prior_yield

ENABLED = os.getenv('VALIDATE_DISTRIBUTION', 'true') == 'true'

UNIVARIATE_DEFAULT_THRESHOLD = 0.95
UNIVARIATE_DEFAULT_ZSCORE = 1.96
UNIVARIATE_CI_TO_ZSCORE = {
    0.9: 1.65,
    UNIVARIATE_DEFAULT_THRESHOLD: UNIVARIATE_DEFAULT_ZSCORE,
    0.99: 2.58
}


def _process_fertiliser(country_id: str, product_id: str, input_id: str):
    mu, sd = get_post_fert(country_id, product_id, input_id)
    return (mu, sd) if mu is not None else get_prior_fert(country_id, input_id)


def _process_pesticide(country_id: str, product_id: str, *args):
    mu, sd = get_post_pest(country_id, product_id)
    return (mu, sd) if mu is not None else get_prior_pest(country_id)


def _process_irrigation(country_id: str, product_id: str, *args):
    mu, sd = get_post_irri(country_id, product_id)
    return (mu, sd) if mu is not None else get_prior_irri(country_id)


def _process_yield(country_id: str, product_id: str, *args):
    mu, sd = get_post_yield(country_id, product_id)
    return (mu, sd) if mu is not None else get_prior_yield(country_id, product_id)


_PROCESS_BY_KEY = {
    PESTICIDE_COLUMN: _process_pesticide,
    IRRIGATION_COLUMN: _process_irrigation,
    YIELD_COLUMN: _process_yield
} | {
    key: _process_fertiliser for key in FERTILISER_COLUMNS
}


def get_stats_by_group_key(key: str, country_id: str, product_id: str, input_id: str = None):
    return _PROCESS_BY_KEY[key](country_id, product_id, input_id)


def cycle_completeness_key(key: str):
    return 'fertiliser' if key in FERTILISER_COLUMNS else (
        'pesticideVeterinaryDrug' if key == PESTICIDE_COLUMN
        else 'water' if key == IRRIGATION_COLUMN
        else ''
    )


def validate(values: list, threshold: float, get_mu_sd):
    def exec():
        z = UNIVARIATE_CI_TO_ZSCORE[threshold]
        mu, sd = get_mu_sd()
        _min = mu-(z*sd) if mu is not None else None
        _max = mu+(z*sd) if mu is not None else None
        passes = [_min <= y <= _max if all([mu is not None, not math.isnan(y)]) else True for y in values]
        outliers = [y for y in values if not _min <= y <= _max] if mu is not None else []
        return all(passes), outliers, max(_min or 0, 0), _max
    return exec() if ENABLED else (True, [], None, None)
