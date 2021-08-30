def is_number(string_num):
    try:
        _number = float(string_num.replace(',', ''))
        # check for "nan" floats
        return _number == _number
    except ValueError:
        return False


def parse_number(string_num, return_null=True):
    try:
        _number = float(string_num.replace(',', ''))
        # check for "nan" floats
        return _number if _number == _number else (None if return_null else 0)
    except ValueError:
        return None if return_null else 0
