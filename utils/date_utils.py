import math
from datetime import timedelta


def group_util(start_date, end_date, period=86400):
    _difference = (end_date - start_date)
    if _difference.days == 0 and _difference.seconds == 0:
        yield start_date
    else:
        _diff_seconds = _difference.days * 24 * 60 * 60 + _difference.seconds
        for _index in range(math.ceil(_diff_seconds / period)):
            # using generator function to solve problem
            # returns intermediate result
            yield (start_date + timedelta(seconds=_index * period))
    yield end_date


def group_util_by_days(start_date, end_date, days=1):
    _difference = (end_date - start_date)
    if _difference.seconds == 0:
        yield start_date.replace(hour=0, minute=0, second=0)
    else:
        _diff_days = _difference.days + 1 if _difference.seconds else 0
        for _index in range(_diff_days):
            # using generator function to solve problem
            # returns intermediate result
            yield (start_date + timedelta(days=_index)).replace(hour=0, minute=0, second=0)
    yield end_date


def chunk_time_range_by_periods(start_date, end_date, period=86400):
    _list_of_dates = list(group_util(start_date, end_date, period))
    # using strftime to convert to user friendly format
    result = []
    for _index, _date in enumerate(_list_of_dates, 0):
        if _index > 0:
            result.append([_list_of_dates[_index - 1], _date])
    return result


def chunk_date_range_by_days(start_date, end_date, days=1):
    _list_of_dates = list(group_util_by_days(start_date, end_date, days))
    # using strftime to convert to user friendly format
    result = []
    for _index, _date in enumerate(_list_of_dates, 0):
        if _index > 0:
            result.append([_list_of_dates[_index - 1], _date])
    return result
