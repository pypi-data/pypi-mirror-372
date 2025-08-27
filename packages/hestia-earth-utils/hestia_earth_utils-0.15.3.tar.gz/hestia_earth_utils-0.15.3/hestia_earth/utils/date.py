from dateutil.parser import parse
import re

SECOND = 1
MINUTE = 60 * SECOND
HOUR = 60 * MINUTE
DAY = 24 * HOUR
YEAR = 365.2425


def diff_in_days(from_date: str, to_date: str) -> float:
    """
    Return the difference in days between two dates.

    Parameters
    ----------
    from_date : str
        Date in string format
    to_date
        Date in string format

    Returns
    -------
    float
        The difference of days between from and to dates with a precision of 1.
    """
    difference = parse(to_date) - parse(from_date)
    return round(difference.days + difference.seconds / DAY, 1)


def diff_in_years(from_date: str, to_date: str) -> float:
    """
    Return the difference in years between two dates.

    Parameters
    ----------
    from_date : str
        Date in string format
    to_date
        Date in string format

    Returns
    -------
    float
        The difference of years between from and to dates with a precision of 1.
    """
    return round(diff_in_days(from_date, to_date) / YEAR, 1)


def is_in_days(date: str) -> bool:
    """
    Check if the date as a string contains year, month and day.

    Parameters
    ----------
    date : str
        Date in string format

    Returns
    -------
    bool
        True if the date contains the year, month and day.
    """
    return date is not None and re.compile(r'^[\d]{4}\-[\d]{2}\-[\d]{2}').match(date) is not None


def is_in_months(date: str) -> bool:
    """
    Check if the date as a string contains year, month but no day.

    Parameters
    ----------
    date : str
        Date in string format

    Returns
    -------
    bool
        True if the date contains the year, month but no day.
    """
    return date is not None and re.compile(r'^[\d]{4}\-[\d]{2}$').match(date) is not None
