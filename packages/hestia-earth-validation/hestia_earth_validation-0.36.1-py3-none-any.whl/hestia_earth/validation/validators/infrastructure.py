from hestia_earth.utils.date import diff_in_years

from hestia_earth.validation.utils import _filter_list_errors


def validate_lifespan(infrastructure: list):
    def validate(values: tuple):
        index, value = values
        start_date = value.get('startDate')
        end_date = value.get('endDate')
        lifespan = value.get('defaultLifespan', -1)
        diff = diff_in_years(start_date, end_date) if start_date and end_date else -1
        return lifespan == -1 or diff == -1 or diff == round(lifespan, 1) or {
            'level': 'error',
            'dataPath': f".infrastructure[{index}].defaultLifespan",
            'message': f"must equal to endDate - startDate in decimal years (~{diff})"
        }

    return _filter_list_errors(map(validate, enumerate(infrastructure)))
