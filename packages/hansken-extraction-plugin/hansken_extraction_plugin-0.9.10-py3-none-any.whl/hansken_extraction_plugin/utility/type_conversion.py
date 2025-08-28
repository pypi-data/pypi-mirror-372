"""This module contains classes and functions related to type conversion."""


def get_type_name(tp):
    """Get the type name in a Python 3.8, 3.9 and 3.10 compatible way."""
    if hasattr(tp, '__name__'):
        return tp.__name__
    elif hasattr(tp, '__origin__') and hasattr(tp.__origin__, '__name__'):
        return tp.__origin__.__name__
    else:
        return str(tp)
