from datetime import datetime, timedelta
import typing as T

import eccodes as ecc
import xarray as xr


def read_reference_time(msgid: int) -> datetime:
    """
    Read the time value from ecCodes GRIB handle.

    Time information is taken from the GRIB reference time variables:
    `year`, `month`, `day`, `hour`, `minute` and `second`. The actual
    meaning of this reference time can vary dependending on the
    type of the data.

    Arguments:
    ----------
    msgid : int
        ecCodes message handle.

    Returns:
    --------
    datetime
        Datetime object representing the time encoded in
        the GRIB message.
    """
    year = int(ecc.codes_get(msgid, 'year'))
    month = int(ecc.codes_get(msgid, 'month'))
    day = int(ecc.codes_get(msgid, 'day'))
    hour = int(ecc.codes_get(msgid, 'hour'))
    minute = int(ecc.codes_get(msgid, 'minute'))
    second = int(ecc.codes_get(msgid, 'second'))

    return datetime(
        year=year, month=month, day=day,
        hour=hour, minute=minute, second=second
    )


def read_valid_time(msgid: int) -> datetime:
    """
    Read the time value from ecCodes GRIB handle.

    Valid time is calculated by reading the reference time from
    the GRIB message and adding the quantity on the `step` key
    in hours.

    Step units other than hours are not currently supported.

    Arguments:
    ----------
    msgid : int
        ecCodes message handle.

    Returns:
    --------
    datetime
        Datetime object representing the valid time.
    """
    reference_time = read_reference_time(msgid)
    step = ecc.codes_get(msgid, 'step', ktype=int)
    return reference_time + timedelta(hours=step)


def create_time_coordinate(time: datetime) -> xr.DataArray:
    """
    Create coordinate DataArray with name 'time' and length 1.

    Arguments:
    ----------
    time : datetime
        Datetime object with the value for `time`.

    Returns:
    --------
    xr.DataArray
        Coordinate with name 'time' and length 1.
    """

    return xr.DataArray(
        data=[time], dims={'time': 1},
        attrs={
            "standard_name": "forecast_reference_time"
        },
        name="time"
    )


def create_valid_time_coordinate(time: datetime) -> xr.DataArray:
    """
    Create coordinate DataArray with name 'valid_time' and length 1.

    Arguments:
    ----------
    time : datetime
        Datetime object with the value for `valid_time`.

    Returns:
    --------
    xr.DataArray
        Coordinate with name 'valid_time' and length 1.
    """

    return xr.DataArray(
        data=[time], dims={'time': 1},
        attrs={
            "standard_name": "time"
        },
        name="valid_time"
    )


def _get_time_coords_old_data(msgid) -> T.Dict[str, xr.DataArray]:
    """
    Read time coordinates from ecCodes handle from old data.

    For backwards compatibility only.

    Only 'time' coordinate is reported which is mapped to the
    valid_time.

    Arguments:
    ----------
    msgid : int
        ecCodes message handle.

    Returns:
    --------
    Dict
        Mapping between coordinate name and coordinate xr.DataArray
        for each time coordinate.
    """
    time = read_valid_time(msgid)
    time_coord = create_valid_time_coordinate(time)
    return {
        "time": time_coord
    }


def get_time_coords_new_dgov(msgid: int) -> T.Dict[str, xr.DataArray]:
    """
    Get time coordinates from ecCodes handle.

    Two coordinates are reported: The 'time' coordinate matches
    the GRIB reference time. The 'valid_time' is calculated by adding
    the 'step' key to the reference time.

    For instantaneous variables, this two coordinates match.

    For averaged or accumulated variables 'time' represents the
    start of the time interval, while 'valid_time' represents the
    end of the time interval.

    Arguments:
    ----------
    msgid : int
        ecCodes message handle.

    Returns:
    --------
    Dict
        Mapping between coordinate name and coordinate xr.DataArray
        for each time coordinate.
    """
    reference_time = read_reference_time(msgid)
    valid_time = read_valid_time(msgid)

    time_coord = create_time_coordinate(reference_time)
    valid_time_coord = create_valid_time_coordinate(
        valid_time
    )

    return {
        "time": time_coord,
        "valid_time": valid_time_coord
    }


def read_time_coords(msgid: int) -> T.Dict[str, xr.DataArray]:
    """
    Read time coordinates from ecCodes handle.

    For current data, two coordinates are reported: The 'time'
    coordinate matches the GRIB reference time. The 'valid_time'
    is calculated by adding the 'step' key to the reference time.

    For instantaneous variables, this two coordinates match.

    For averaged or accumulated variables 'time' represents the
    start of the time interval, while 'valid_time' represents the
    end of the time interval.

    For old preproduction data, only 'time' is reported which is
    always mapped to the valid_time. This is meant just for backwards
    compatibility with old data.

    Arguments:
    ----------
    msgid : int
        ecCodes message handle.

    Returns:
    --------
    Dict
        Mapping between coordinate name and coordinate xr.DataArray
        for each time coordinate.
    """
    edition = int(ecc.codes_get(msgid, 'edition'))

    if edition == 1:
        return _get_time_coords_old_data(msgid)

    significance_of_ref_time = int(
        ecc.codes_get(msgid, "significanceOfReferenceTime")
    )

    if significance_of_ref_time == 1:
        return _get_time_coords_old_data(msgid)

    return get_time_coords_new_dgov(msgid)
