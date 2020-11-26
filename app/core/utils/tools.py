"""
This module must provide miscellaneous methods and classes.
Highly recommended to import everything from here into
`utils.__init__.py` file, so user can do:
    from core.utils import some_method
Instead of:
    from core.utils.tools import some_method

NOTE: Do not import in `__init__.py` like:
    from core.utils.tools import *  # DON'T DO THAT

"""

from decimal import Decimal


def convert_to_decimal(x, r):
    return round(Decimal(str(x)), r)


def isiterable(o):
    """Check if passed value is iterable"""
    try:
        _ = (e for e in o)
    except TypeError:
        return False
    else:
        return True


def get_dotted_field(obj, dotted_field):
    """Returns dotted field, will return None on AttributeError!"""
    if isinstance(dotted_field, str):
        fields = dotted_field.split(".")
    else:
        fields = list(dotted_field)

    if len(fields) > 1:
        obj = getattr(obj, fields[0], None)

        if obj:
            return get_dotted_field(obj, fields[1:])
        return None

    elif len(fields) == 1:
        return getattr(obj, fields[0], None)

    return None
