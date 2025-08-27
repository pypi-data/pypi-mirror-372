import time
from dateutil.parser import parse
from statistics import mean
from functools import reduce
from math import log10, floor
import numpy
from hestia_earth.schema import NodeType


def to_precision(number: float, digits: int = 3) -> float:
    return round(number, digits - int(floor(log10(abs(number)))) - 1)


def non_empty_value(value) -> bool:
    """
    Check if a value is empty.

    Parameters
    ----------
    value
        Either a string, a list, a number or None.

    Returns
    -------
    bool
        True if the value is not en empty string or an empty list.
    """
    return all([
        value != '',
        value is not None,
        not isinstance(value, list) or value != [],
        not isinstance(value, dict) or value != {}
    ])


def non_empty_list(values: list) -> list:
    """
    Filter list removing empty values.

    Parameters
    ----------
    values
        A list of values.

    Returns
    -------
    list
        List without empty values.
    """
    return list(filter(non_empty_value, values))


def is_node_of(node_type) -> bool:
    """
    Check wether node is of a certain HESTIA Type.

    Parameters
    ----------
    node_type
        The type to check for.
    node
        The node.

    Returns
    -------
    bool
        True if matches type.
    """
    return lambda node: isinstance(node, dict) and node.get('type', node.get('@type')) == node_type.value


def is_term(node: dict) -> bool:
    """
    Check wether node is a `Term`.

    Parameters
    ----------
    node
        The node.

    Returns
    -------
    bool
        True if it is a `Term`.
    """
    return is_node_of(NodeType.TERM)(node)


def current_time_ms():
    """
    Get the time in ms since EPOCH.

    Returns
    -------
    int
        Time in milliseconds.
    """
    return float(time.time() * 1000)


def safe_parse_float(value: str, default=0):
    """
    Parse a string into a float.

    Parameters
    ----------
    value
        The string value to parse.
    default
        The default value if parsing not possible.

    Returns
    -------
    float
        The value as float or default value.
    """
    try:
        value = float(value)
        return default if numpy.isnan(value) else value
    except Exception:
        return default


def safe_parse_date(date=None, default=None):
    """
    Parse a string into a date.

    Parameters
    ----------
    value
        The string value to parse.
    default
        The default value if parsing not possible.

    Returns
    -------
    datetime
        The value as datetime or default value.
    """
    try:
        return parse(str(date), fuzzy=True)
    except Exception:
        return default


def is_number(value):
    """
    Return `True` if the value is either an `int` or a `float`.
    """
    return all([
        not isinstance(value, bool),  # True is apparently considered an `int`
        any([isinstance(value, int), isinstance(value, float)])
    ])


def is_boolean(v):
    """
    Return `True` if the value is a `bool`.
    """
    return isinstance(v, bool)


def list_average(value: list, default=0):
    """
    Returns the average over a list of numbers.

    Parameters
    ----------
    value
        A list of numbers.
    default
        The default value if the value does not contain a list of numbers.

    Returns
    -------
    float
        The average of the values.
    """
    values = non_empty_list(value) if value and isinstance(value, list) and all(map(is_number, value)) else []
    return mean(values) if values else default


def list_sum(value: list, default=0):
    """
    Returns the sum over a list of numbers.

    Parameters
    ----------
    value
        A list of numbers.
    default
        The default value if the value does not contain a list of numbers.

    Returns
    -------
    float
        The sum of the values.
    """
    values = non_empty_list(value) if value and isinstance(value, list) and all(map(is_number, value)) else []
    return sum(values) if values else default


def flatten(values: list):
    """
    Flattens a two-dimensional list into a one-dimensional list.

    Parameters
    ----------
    values
        A list of list.

    Returns
    -------
    list
        A list of single values.
    """
    return list(reduce(lambda x, y: x + (y if isinstance(y, list) else [y]), values, []))


def _get_by_key(x, y):
    return x if x is None else (
        x.get(y) if isinstance(x, dict) else list(map(lambda v: get_dict_key(v, y), x))
    )


def get_dict_key(value: dict, key: str): return reduce(lambda x, y: _get_by_key(x, y), key.split('.'), value)
