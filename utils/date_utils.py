from datetime import timedelta


def group_util(start_date, end_date):
    _difference = (end_date - start_date)
    if _difference.days == 0:
        yield start_date
    else:
        for _index in range(_difference.days):
            # using generator function to solve problem
            # returns intermediate result
            yield (start_date + timedelta(days=_index))
    yield end_date


def chunk_date_date_range(start_date, end_date):
    _list_of_dates = list(group_util(start_date, end_date))
    # using strftime to convert to user friendly format
    result = []
    for _index, _date in enumerate(_list_of_dates, 0):
        if _index > 0:
            result.append([_list_of_dates[_index - 1], _date])
    return result
