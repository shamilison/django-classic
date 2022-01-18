from datetime import timedelta

import math
def group_util(start_date, end_date, period=86400):
    _difference = (end_date - start_date)
    if _difference.seconds == 0:
        yield start_date
    else:
        for _index in range(math.ceil(_difference.seconds/period)):
            # using generator function to solve problem
            # returns intermediate result
            yield (start_date + timedelta(seconds=period))
    yield end_date


def chunk_date_date_range(start_date, end_date, period=86400):
    _list_of_dates = list(group_util(start_date, end_date, period))
    # using strftime to convert to user friendly format
    result = []
    for _index, _date in enumerate(_list_of_dates, 0):
        if _index > 0:
            result.append([_date, _list_of_dates[_index - 1]])
    return result
