import pandas as pd
import pytz
from timezonefinder import TimezoneFinder
from typing import Union

from sunpeek.common.unit_uncertainty import Q
from sunpeek.common.utils import sp_logger
from sunpeek.common.errors import TimeZoneError

tf = TimezoneFinder()

TIMEZONE_NONE = "UTC offset included in data"   # Example: 2017-05-01 00:01:00+02
TIMEZONE_LOCAL_NO_DST = "Plant local timezone without DST"
TIMEZONE_LOCAL_WITH_DST = "Plant local timezone with DST"

available_timezones = \
    [TIMEZONE_NONE, TIMEZONE_LOCAL_NO_DST, TIMEZONE_LOCAL_WITH_DST] + \
    list(pytz.common_timezones) + ['UTC+' + str(i) for i in range(1, 13)] + ['UTC-' + str(i) for i in range(1, 13)]


def get_data_timezone(tz_offset_minutes: float) -> pytz.FixedOffset:
    """Returns a pytz fixed-offset timezone, corresponding to winter time (no DST) in the given location.

    Parameters
    ----------
    tz_offset_minutes : float, Time zone offset from UTC in minutes. Use get_timezone_offset_minutes() to calculate
    this offset for a given location (latitude and longitude).

    Returns
    -------
    pytz._FixedOffset, the pytz time zone to be used for data.

    Notes
    -----
    To avoid problems switching to DST (daylight saving time) and back, a fixed-offset time zone is used in SunPeek.
    This is equivalent to the winter time zone, in the respective location.
    For a detailed exchange about this, see https://gitlab.com/sunpeek/sunpeek/-/issues/351
    """

    return pytz.FixedOffset(int(tz_offset_minutes))


def get_timezone_string(latitude: Q, longitude: Q) -> str:
    """Returns a time zone string for a given location. Example: 'Europe/Vienna'.
    """
    local_tz_string = tf.timezone_at(lat=latitude.to('deg').magnitude, lng=longitude.to('deg').magnitude)
    return local_tz_string


def get_timezone_offset_minutes(latitude: Q, longitude: Q) -> int:
    """Returns the offset in minutes between UTC and the local time zone (in winter time, no DST).
    Example: For 'Europe/Vienna', it returns 60.
    """
    local_tz_string = get_timezone_string(latitude, longitude)

    return round(pd.to_datetime('2023-01-01').tz_localize(local_tz_string).utcoffset().total_seconds() / 60)


def _get_timezone_string_plots(latitude: Q, longitude: Q) -> str:
    """Returns a string like "UTC+1", to be used in plots etc.
    """
    offset_minutes = get_timezone_offset_minutes(latitude, longitude)
    fmt = "+0.0f" if offset_minutes % 60 == 0 else "+0.2f"

    return f"UTC{offset_minutes / 60:{fmt}}"



def process_timezone(tz: Union[str, pytz.BaseTzInfo, pytz._FixedOffset, None],
                     plant: 'sunpeek.components.Plant' = None):
    if tz is None:
        return None
    if isinstance(tz, pytz.BaseTzInfo):
        return tz
    if isinstance(tz, pytz._FixedOffset):
        return tz

    try:
        return pytz.timezone(tz)
    except pytz.exceptions.UnknownTimeZoneError:
        if tz == TIMEZONE_NONE:
            return None
        if tz == TIMEZONE_LOCAL_NO_DST:
            if plant is None:
                raise TimeZoneError(f'Time zone "{tz}" requires a plant but got a None plant.')
            return pytz.FixedOffset(get_timezone_offset_minutes(plant.latitude, plant.longitude))
        if tz == TIMEZONE_LOCAL_WITH_DST:
            if plant is None:
                raise TimeZoneError(f'Time zone "{tz}" requires a plant but got a None plant.')
            return pytz.timezone(get_timezone_string(plant.latitude, plant.longitude))
        if 'UTC+' in tz:
            return pytz.FixedOffset(int(tz.split('+')[1]) * 60)
        if 'UTC-' in tz:
            return pytz.FixedOffset(-int(tz.split('-')[1]) * 60)
        raise TimeZoneError('Unknown timezone string provided.')


def validate_timezone(idx: pd.DatetimeIndex,
                      timezone: Union[str, pytz.timezone],
                      plant: 'sunpeek.components.Plant' = None) -> pd.DatetimeIndex:
    """Validates timezone information, trying to match DataFrame timezone and timezone string.

    Parameters
    ----------
    idx : pd.DatetimeIndex
    timezone : str or pytz.timezone
        If string, pytz must be able to parse that string into a timezone. Examples of valid inputs:
        'Europe/Berlin' or pytz.timezone('Europe/Berlin') or pytz.timezone('UTC') or pytz.FixedOffset(60)
    plant : sunpeek.components.Plant


    Returns
    -------
    idx : pandas.DatetimeIndex
        timezone-aware index

    Raises
    ------
    TimeZoneError

    Notes
    -----
    Here is how all combinations are handled:
    1. No timezone in df, but timezone string given: ok
    2. Timezone in df, and no timezone string given: ok
    3. No timezone in df, and no timezone string given: error (timezone info is missing)
    4. Timezone both in df and as timezone string: error (because it's hard to check compatibility between a
       dynamically-offset string-based timezone like 'Europe/Vienna' with a FixedOffset timezone info that is the result of
       parsing timezone-aware timestamps).

    See also
    --------
    `pvlib documentation on timezones <https://pvlib-python.readthedocs.io/en/v0.3.0/timetimezones.html>`_
    """

    sp_logger.debug("[validate_timezone] Checking for timezone consistency.")
    original_timezone = timezone

    if isinstance(timezone, str):
        timezone = process_timezone(timezone, plant)
    if (timezone is not None) and not (
            isinstance(timezone, pytz.BaseTzInfo) or isinstance(timezone, pytz._FixedOffset)):
        raise TimeZoneError(f'Expected time zone to be a pytz.timezone object, but got "{type(timezone)}" instead.')

    assert isinstance(idx, pd.DatetimeIndex), \
        'Input index expected to be a pandas DatetimeIndex.'
    tz_idx_none = idx.tzinfo is None

    if (timezone is None) and tz_idx_none:
        # No timezone information available at all -> error
        raise TimeZoneError(
            f"No timezone information found: 'timezone' is set to '{original_timezone}' but no timezone information "
            f"was found in the provided data."
        )

    if (timezone is not None) and not tz_idx_none:
        # Both timezone information available -> error (see docstring)
        raise TimeZoneError(
            'Ambiguous timezone information found: A timezone string (resulting in a dynamic offset) is given, '
            'and timezone information is also given in the pandas index (fixed offset).'
            'These two pieces of timezone information are incompatible. Use only one of them, string or pandas index.')

    if tz_idx_none:
        idx = idx.tz_localize(timezone, ambiguous='NaT', nonexistent='NaT')

    # If df.index is already timezone-aware, we can just simply return it

    return idx
