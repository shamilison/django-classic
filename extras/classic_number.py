# coding: utf-8

import re


def parse_number(text):
    """
        Return the first number in the given text for any locale.
        TODO we actually don't take into account spaces for only
        3-digited numbers (like "1 000") so, for now, "1 0" is 10.
        TODO parse cases like "125,000.1,0.2" (125000.1).

        :example:
        >>> parse_number("a 125,00 €")
        125
        >>> parse_number("100.000,000")
        100000
        >>> parse_number("100 000,000")
        100000
        >>> parse_number("100,000,000")
        100000000
        >>> parse_number("100 000 000")
        100000000
        >>> parse_number("100.001 001")
        100.001
        >>> parse_number("$.3")
        0.3
        >>> parse_number(".003")
        0.003
        >>> parse_number(".003 55")
        0.003
        >>> parse_number("3 005")
        3005
        >>> parse_number("1.190,00 €")
        1190
        >>> parse_number("1190,00 €")
        1190
        >>> parse_number("1,190.00 €")
        1190
        >>> parse_number("$1190.00")
        1190
        >>> parse_number("$1 190.99")
        1190.99
        >>> parse_number("$-1 190.99")
        -1190.99
        >>> parse_number("1 000 000.3")
        1000000.3
        >>> parse_number('-151.744122')
        -151.744122
        >>> parse_number('-1')
        -1
        >>> parse_number("1 0002,1.2")
        10002.1
        >>> parse_number("")

        >>> parse_number(None)

        >>> parse_number(1)
        1
        >>> parse_number(1.1)
        1.1
        >>> parse_number("rrr1,.2o")
        1
        >>> parse_number("rrr1rrr")
        1
        >>> parse_number("rrr ,.o")

    """
    try:
        # First we return None if we don't have something in the text:
        if text is None:
            return None
        if isinstance(text, int) or isinstance(text, float):
            return text
        text = text.strip()
        if text == "":
            return None
        # Next we get the first "[0-9,. ]+":
        n = re.search("-?[0-9]*([,. ]?[0-9]+)+", text).group(0)
        n = n.strip()
        if not re.match(".*[0-9]+.*", text):
            return None
        # Then we cut to keep only 2 symbols:
        while " " in n and "," in n and "." in n:
            index = max(n.rfind(','), n.rfind(' '), n.rfind('.'))
            n = n[0:index]
        n = n.strip()
        # We count the number of symbols:
        symbolsCount = 0
        for current in [" ", ",", "."]:
            if current in n:
                symbolsCount += 1
        # If we don't have any symbol, we do nothing:
        if symbolsCount == 0:
            pass
        # With one symbol:
        elif symbolsCount == 1:
            # If this is a space, we just remove all:
            if " " in n:
                n = n.replace(" ", "")
            # Else we set it as a "." if one occurence, or remove it:
            else:
                theSymbol = "," if "," in n else "."
                if n.count(theSymbol) > 1:
                    n = n.replace(theSymbol, "")
                else:
                    n = n.replace(theSymbol, ".")
        else:
            # Now replace symbols so the right symbol is "." and all left are "":
            right_symbol_index = max(n.rfind(','), n.rfind(' '), n.rfind('.'))
            right_symbol = n[right_symbol_index:right_symbol_index + 1]
            if right_symbol == " ":
                return parse_number(n.replace(" ", "_"))
            n = n.replace(right_symbol, "R")
            left_symbol_index = max(n.rfind(','), n.rfind(' '), n.rfind('.'))
            left_symbol = n[left_symbol_index:left_symbol_index + 1]
            n = n.replace(left_symbol, "L")
            n = n.replace("L", "")
            n = n.replace("R", ".")
        # And we cast the text to float or int:
        n = float(n)
        if n.is_integer():
            return int(n)
        else:
            return n
    except:
        pass
    return None


def truncateFloat(f, n=2):
    '''Truncates/pads a float f to n decimal places without rounding'''
    s = '{}'.format(f)
    if 'e' in s or 'E' in s:
        return float('{0:.{1}f}'.format(f, n))
    i, p, d = s.partition('.')
    return float('.'.join([i, (d + '0' * n)[:n]]))


def removeCommasBetweenDigits(text):
    """
        :example:
        >>> removeCommasBetweenDigits("sfeyv dsf,54dsf ef 6, 6 zdgy 6,919 Photos and 3,3 videos6,")
        'sfeyv dsf,54dsf ef 6, 6 zdgy 6919 Photos and 33 videos6,'
    """
    if text is None:
        return None
    else:
        return re.sub(r"([0-9]),([0-9])", "\g<1>\g<2>", text)


def get_all_numbers(text, remove_commas=False):
    if text is None:
        return None
    if remove_commas:
        text = removeCommasBetweenDigits(text)
    all_numbers = []
    if len(text) > 0:
        # Remove space between digits :
        space_number_exists = True
        while space_number_exists:
            text = re.sub('(([^.,0-9]|^)[0-9]+) ([0-9])', '\\1\\3', text, flags=re.UNICODE)
            if re.search('([^.,0-9]|^)[0-9]+ [0-9]', text) is None:
                space_number_exists = False
        number_regex = '[-+]?[0-9]+[.,][0-9]+|[0-9]+'
        all_match_iter = re.finditer(number_regex, text)
        if all_match_iter is not None:
            for current in all_match_iter:
                current_float = current.group()
                current_float = re.sub("\s", "", current_float)
                current_float = re.sub(",", ".", current_float)
                current_float = float(current_float)
                if current_float.is_integer():
                    all_numbers.append(int(current_float))
                else:
                    all_numbers.append(current_float)
    return all_numbers


def remove_all_numbers(text):
    if text is None:
        return None
    if len(text) == 0:
        return ""
    # Remove space between digits :
    spaceNumberExists = True
    while spaceNumberExists:
        text = re.sub('([0-9]) ([0-9])', '\\1\\2', text, flags=re.UNICODE)
        if re.search('[0-9] [0-9]', text) is None:
            spaceNumberExists = False
    numberRegex = '[-+]?[0-9]+[.,][0-9]+|[0-9]+'
    numberExists = True
    while numberExists:
        text = re.sub(numberRegex, "", text)
        if re.search(numberRegex, text) is None:
            numberExists = False

    return text.strip()


def get_first_number(text, *args, **kwargs):
    result = get_all_numbers(text, *args, **kwargs)
    if result is not None and len(result) > 0:
        return result[0]
    return None


def represents_float(text):
    """
        This function return True if the given param (string or float) represents a float

        :Example:
        >>> represents_float("1.0")
        True
        >>> represents_float("1")
        False
        >>> represents_float("a")
        False
        >>> represents_float(".0")
        False
        >>> represents_float("0.")
        False
        >>> represents_float("0.000001")
        True
        >>> represents_float("00000.000001")
        True
        >>> represents_float("0000a0.000001")
        False
    """
    if isinstance(text, float):
        return True
    elif text is None:
        return False
    elif isinstance(text, str):
        if len(text) < 3:
            return False
        text = text.strip()
        return re.search("^[0-9]{1,}\.[0-9]{1,}$", text) is not None
    else:
        return False


def represents_int(s, acceptRoundedFloats=False):
    """
        This function return True if the given param (string or float) represents a int

        :Example:
        >>> represents_int(1)
        True
        >>> represents_int("1")
        True
        >>> represents_int("a")
        False
        >>> represents_int("1.1")
        False
        >>> represents_int(1.1)
        False
        >>> represents_int(42.0, acceptRoundedFloats=True)
        True
        >>> represents_int("42.0", acceptRoundedFloats=True)
        True
    """

    if isinstance(s, float):
        if acceptRoundedFloats:
            return s.is_integer()
    else:
        if acceptRoundedFloats:
            try:
                s = float(s)
                return represents_int(s, acceptRoundedFloats=acceptRoundedFloats)
            except ValueError:
                return False
        else:
            try:
                int(s)
                return True
            except ValueError:
                return False
    return False


def float_as_readable(f):
    """
        source https://stackoverflow.com/questions/8345795/force-python-to-not-output-a-float-in-standard-form-scientific-notation-expo
    """
    _ftod_r = re.compile(br'^(-?)([0-9]*)(?:\.([0-9]*))?(?:[eE]([+-][0-9]+))?$')
    """Print a floating-point number in the format expected by PDF:
    as short as possible, no exponential notation."""
    s = bytes(str(f), 'ascii')
    m = _ftod_r.match(s)
    if not m:
        raise RuntimeError("unexpected floating point number format: {!a}"
                           .format(s))
    sign = m.group(1)
    int_part = m.group(2)
    fract_part = m.group(3)
    exponent = m.group(4)
    if ((int_part is None or int_part == b'') and
            (fract_part is None or fract_part == b'')):
        raise RuntimeError("unexpected floating point number format: {!a}"
                           .format(s))

    # strip leading and trailing zeros
    if int_part is None:
        int_part = b''
    else:
        int_part = int_part.lstrip(b'0')
    if fract_part is None:
        fract_part = b''
    else:
        fract_part = fract_part.rstrip(b'0')

    result = None

    if int_part == b'' and fract_part == b'':
        # zero or negative zero; negative zero is not useful in PDF
        # we can ignore the exponent in this case
        result = b'0'

    # convert exponent to a decimal point shift
    elif exponent is not None:
        exponent = int(exponent)
        exponent += len(int_part)
        digits = int_part + fract_part
        if exponent <= 0:
            result = sign + b'.' + b'0' * (-exponent) + digits
        elif exponent >= len(digits):
            result = sign + digits + b'0' * (exponent - len(digits))
        else:
            result = sign + digits[:exponent] + b'.' + digits[exponent:]

    # no exponent, just reassemble the number
    elif fract_part == b'':
        result = sign + int_part  # no need for trailing dot
    else:
        result = sign + int_part + b'.' + fract_part

    result = result.decode("utf-8")
    if result.startswith("."):
        result = "0" + result
    return result


def digitalize_integers(text, total_digits=100):
    if text is None or not isinstance(text, str) or text == "":
        return text
    result = str(text)
    to_edit = []
    for current in re.finditer("[0-9]+", text):
        the_int = current.group(0)
        start = current.start(0)
        end = current.end(0)
        remaining_digits = total_digits - len(the_int)
        digitalized_int = "0" * remaining_digits + the_int
        to_edit.append((digitalized_int, start, end))
    for digitalized_int, start, end in reversed(to_edit):
        # print(digitalized_int, start, end)
        result = result[:start] + digitalized_int + result[end:]
    return result
