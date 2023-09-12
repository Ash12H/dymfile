"""TODO : Describe."""

import calendar
import datetime
import logging

import numpy as np

FILVAL = 1e34


def date_dym2tostr(dym2date: float) -> str:
    """
    Convert a float representation of a date in dym2 format to a string in YYYYMMDD
    format.

    Parameters
    ----------
    dym2date : float
        The float representation of the date in dym2 format.

    Returns
    -------
    str
        A string representation of the date in YYYYMMDD format. If an exception occurs
        during the conversion, returns "xxxxxxxx".

    Notes
    -----
    The dym2 date format is a float where the integer part represents the year, and the
    decimal part represents the day of the year.
    """
    if not isinstance(dym2date, (np.floating, float)):
        msg = f"dym2date expect a float but is a {type(dym2date)}."
        raise TypeError(msg)
    year = int(dym2date)
    daysinyear = 366 if calendar.isleap(year) else 365
    days = round((dym2date - year) * daysinyear)

    try:
        # ! WARNING Jules : if dym2date is "2022.0" then days is 0 and
        # ! datetime.timedelta(days - 1) is -1. In that case 2022 is converted to
        # ! 2021-12-31
        date = datetime.datetime(year, 1, 1) + datetime.timedelta(days - 1)
        return date.strftime("%Y%m%d")
    except Exception as e:
        logging.warning(e)
        return "xxxxxxxx"
