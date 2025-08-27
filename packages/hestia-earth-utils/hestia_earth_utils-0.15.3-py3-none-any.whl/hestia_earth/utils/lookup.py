from functools import reduce
from io import StringIO
from typing import Union
import re
import requests
import csv
import numpy

from .storage import _load_from_storage
from .request import request_url, web_url

DELIMITER = '\t'
ENCODING = 'ISO-8859-1'
GLOSSARY_FOLDER = 'glossary/lookups'
_memory = {}
MISSING_VALUE = '-'
MISSING = -99999
_INDEX_COL = 'termid'
# default: " !#$%&'()*+,-./:;<=>?@[\\]^{|}~"
_DELETE_CHARS = " !#$%&'()*,./:;<=>?@^{|}~"


def _is_missing_value(value): return value == MISSING_VALUE or value == MISSING or value == str(MISSING)


def _replace_missing_values(value: str): return str(MISSING) if str(value) == '-' else value


def _rewrite_csv_file_as_tab(filepath: str):
    with open(filepath, 'r', encoding=ENCODING) as fp:
        reader = csv.reader(fp)
        for row in reader:
            yield DELIMITER.join(list(map(_replace_missing_values, row)))


def _rewrite_csv_text_as_tab(text: str):
    reader = csv.reader(StringIO(text))
    for row in reader:
        yield DELIMITER.join(list(map(_replace_missing_values, row)))


def _recfromcsv(data): return numpy.recfromcsv(data,
                                               missing_values=MISSING_VALUE,
                                               filling_values=MISSING,
                                               delimiter=DELIMITER,
                                               encoding=ENCODING,
                                               case_sensitive=True,
                                               deletechars=_DELETE_CHARS)


def _memory_wrapper(key: str, func):
    global _memory  # noqa: F824
    _memory[key] = _memory[key] if key in _memory else func()
    return _memory[key]


def load_lookup(filepath: str, keep_in_memory: bool = False):
    """
    Import local lookup table as csv file into a `numpy.recarray`.

    Parameters
    ----------
    filepath : str
        The path of csv file on the local file system.
    keep_in_memory: bool
        Set to True if you want to store the file in memory for later use.

    Returns
    -------
    numpy.recarray
        The `numpy.recarray` converted from the csv content.
    """
    def load(): return _recfromcsv(_rewrite_csv_file_as_tab(filepath))
    return _memory_wrapper(filepath, load) if keep_in_memory else load()


def _download_lookup_data(filename: str):
    filepath = f"{GLOSSARY_FOLDER}/{filename}"

    def fallback():
        url = request_url(f"{web_url()}/{filepath}")
        return requests.get(url).content.decode('utf-8')

    try:
        data = _load_from_storage(filepath, glossary=True)
        return data.decode('utf-8') if data else None
    except ImportError:
        return fallback()


def _build_index(array: numpy.recarray):
    columns = list(array.dtype.names)
    try:
        return {
            row[_INDEX_COL]: {col: row[col] for col in columns}
            for row in array
        } if _INDEX_COL in columns else array
    except TypeError:
        return {
            array[_INDEX_COL].item(): {col: array[col].item() for col in columns}
        } if _INDEX_COL in columns else array


def download_lookup(filename: str, keep_in_memory: bool = True, build_index: bool = False):
    """
    Download lookup table from HESTIA as csv into a `numpy.recarray`.

    Parameters
    ----------
    filename : str
        The name on the file on the HESTIA lookup repository.
    keep_in_memory: bool
        Set to False if you do NOT want to store the file in memory for later use.
    build_index : bool
        Set to False to skip trying to build an index.

    Returns
    -------
    numpy.recarray
        The `numpy.recarray` converted from the csv content.
    """
    def load():
        data = _download_lookup_data(filename)
        rec = _recfromcsv(_rewrite_csv_text_as_tab(data)) if data else None
        return (_build_index(rec) if build_index else rec) if data else None

    try:
        return _memory_wrapper(filename, load) if keep_in_memory else load()
    except Exception:
        return None


def column_name(key: str):
    """
    Convert the column name to a usable key on a `numpy.recarray`.

    Parameters
    ----------
    key : str
        The column name.

    Returns
    -------
    str
        The column name that can be used in `get_table_value`.
    """
    return re.sub('[' + re.escape(_DELETE_CHARS) + ']', '', key.replace(' ', '_')) if key else ''


def _get_single_table_value(data: Union[dict, numpy.recarray], col_match: str, col_match_with, col_val):
    return (
        data.get(col_match_with, {})[col_val] if isinstance(data, dict) else
        data[data[col_match] == col_match_with][col_val][0]
    )


def _get_multiple_table_values(data: Union[dict, numpy.recarray], col_match: str, col_match_with, col_val):
    def reducer(x, values):
        col = values[1]
        value = col_match_with[values[0]]
        return x.get(value) if isinstance(x, dict) else x[x[col] == value]

    return reduce(reducer, enumerate(col_match), data)[col_val][0]


def get_table_value(lookup: Union[dict, numpy.recarray], col_match: str, col_match_with, col_val):
    """
    Get a value matched by one or more columns from a `numpy.recarray`.

    Parameters
    ----------
    lookup : dict | numpy.recarray
        The value returned by the `download_lookup` function.
    col_match : str
        Which `column` should be used to find data in. This will restrict the rows to search for.
        Can be a single `str` or a list of `str`. If a list is used, must be the same length as `col_match_with`.
    col_match_with
        Which column `value` should be used to find data in. This will restrict the rows to search for.
        Can be a single `str` or a list of `str`. If a list is used, must be the same length as `col_match`.
    col_val: str
        The column which contains the value to look for.

    Returns
    -------
    str
        The value found or `None` if no match.
    """
    single = isinstance(col_match, str) and isinstance(col_match_with, str)
    try:
        value = (
            _get_single_table_value(lookup, col_match, col_match_with, col_val) if single else
            _get_multiple_table_values(lookup, col_match, col_match_with, col_val)
        )
        return None if _is_missing_value(value) else value
    except Exception:
        return None


def find_term_ids_by(lookup: Union[dict, numpy.recarray], col_match: str, col_match_with):
    """
    Find `term.id` values where a column matches a specific value.

    Parameters
    ----------
    lookup : dict | numpy.recarray
        The value returned by the `download_lookup` function.
    col_match : str
        Which `column` should be used to find data in. This will restrict the rows to search for.
        Can be a single `str` or a list of `str`. If a list is used, must be the same length as `col_match_with`.
    col_match_with
        Which column `value` should be used to find data in. This will restrict the rows to search for.
        Can be a single `str` or a list of `str`. If a list is used, must be the same length as `col_match`.

    Returns
    -------
    list[str]
        The list of `term.id` that matched the expected column value.
    """
    term_ids = (
        set([
            key
            for key, value in lookup.items()
            if value.get(col_match) == col_match_with
        ])
    ) if isinstance(lookup, dict) else set(list(lookup[lookup[col_match] == col_match_with].termid))
    return list(map(str, term_ids))


def extract_grouped_data(data: str, key: str) -> str:
    """
    Extract value from a grouped data in a lookup table.

    Example:
    - with data: `Average_price_per_tonne:106950.5556;1991:-;1992:-`
    - get the value for `Average_price_per_tonne` = `106950.5556`

    Parameters
    ----------
    data
        The data to parse. Must be a string in the format `<key1>:<value>;<key2>:<value>`
    key
        The key to extract the data. If not present, `None` will be returned.

    Returns
    -------
    str
        The value found or `None` if no match.
    """
    grouped_data = reduce(lambda prev, curr: {
        **prev,
        **{curr.split(':')[0]: curr.split(':')[1]}
    }, data.split(';'), {}) if data is not None and isinstance(data, str) and len(data) > 1 else {}
    value = grouped_data.get(key)
    return None if _is_missing_value(value) else value


def extract_grouped_data_closest_date(data: str, year: int) -> str:
    """
    Extract date value from a grouped data in a lookup table.

    Example:
    - with data: `2000:-;2001:0.1;2002:0;2003:0;2004:0;2005:0`
    - get the value for `2001` = `0.1`

    Parameters
    ----------
    data
        The data to parse. Must be a string in the format `<key1>:<value>;<key2>:<value>`
    year
        The year to extract the data. If not present, the closest date data will be returned.

    Returns
    -------
    str
        The closest value found.
    """
    data_by_date = reduce(
        lambda prev, curr: {
            **prev,
            **{curr.split(':')[0]: curr.split(':')[1]}
        } if len(curr) > 0 and not _is_missing_value(curr.split(':')[1]) else prev,
        data.split(';'),
        {}
    ) if data is not None and isinstance(data, str) and len(data) > 1 else {}
    dist_years = list(data_by_date.keys())
    closest_year = min(dist_years, key=lambda x: abs(int(x) - year)) if len(dist_years) > 0 else None
    return None if closest_year is None else data_by_date.get(closest_year)


def lookup_term_ids(lookup: Union[dict, numpy.recarray]):
    """
    Get the `term.id` values from a lookup.

    Parameters
    ----------
    lookup : dict | numpy.recarray
        The value returned by the `download_lookup` function.

    Returns
    -------
    list[str]
        The `term.id` values from the lookup.
    """
    return lookup.keys() if isinstance(lookup, dict) else list(lookup.termid)


def lookup_columns(lookup: Union[dict, numpy.recarray]):
    """
    Get the columns from a lookup.

    Parameters
    ----------
    lookup : dict | numpy.recarray
        The value returned by the `download_lookup` function.

    Returns
    -------
    list[str]
        The columns from the lookup.
    """
    return list(list(lookup.values())[0].keys()) if isinstance(lookup, dict) else list(lookup.dtype.names)
