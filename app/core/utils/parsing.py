"""
Parsing module:
    1. `parse_int`
    2. `parse_float`
    3. `parse_decimal`

Every method in this module can fail (and return None).
But every method fails on specific conditions.
See methods docstrings to see which condition is
considered as fail for that method.
"""
from decimal import Decimal, InvalidOperation


def parse_int(string):
    """
    Tries to parse string to integer.
    If fails, returns None.

    Fail condition: `ValueError` or `TypeError` is raised.
    """
    try:
        return int(string)
    except (ValueError, TypeError):
        return None


def parse_float(string):
    """
    Tries to parse string to float.
    If fails, returns None.

    Fail condition: `ValueError` or `TypeError` is raised.
    """
    try:
        return float(string)
    except (ValueError, TypeError):
        return None


def parse_decimal(string, round_to=None):
    """
    Tries to convert string to `Decimal` instance.
    If fails, returns None.

    `round_to` argument may be provided to set the rounding.

    Fail condition: `decimal.InvalidOperation` is raised.
    """
    try:
        dec = Decimal(string)
        if round_to is not None:
            dec = round(dec, round_to)
    except InvalidOperation:
        return None
    else:
        return dec
