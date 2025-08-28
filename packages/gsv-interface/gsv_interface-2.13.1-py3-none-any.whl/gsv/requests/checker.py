from typing import List, Dict, Union
from datetime import datetime
import re

from gsv.exceptions import (
    InvalidDateError, InvalidTimeError, InvalidStepError,
    InvalidLevelError, UnknownVariableError, MissingKeyError,
    InvalidKeyError, InvalidMonthError, InvalidYearError,
    UnexpectedKeyError, InvalidInterpolationMethodError,
    InvalidTargetGridError, InvalidAreaError
)
from gsv.requests.utils import (
    _get_shortname_dict, IMPLICIT_DATE_PATTERN, IMPLICIT_TIME_PATTERN,
    IMPLICIT_STEP_PATTERN, IMPLICIT_MONTH_PATTERN,
    IMPLICIT_YEAR_PATTERN
)


def check_date_valid(date: str):
    """
    Check that a date is valid.

    Arguments:
    ----------
    date : str
        Date represented as string with format YYYYMMDD.
    """
    try:
        datetime.strptime(date, '%Y%m%d')
    except ValueError:
        raise InvalidDateError(
            date,
            f"Could not interpret string {date} as a date"
            "Dates should follow format YYYYMMDD"
            )


def check_time_valid(time: str):
    """
    Check that a time is valid.

    Arguments:
    ----------
    time : str
        Time represented as string with format hhmm
    """
    try:
        datetime.strptime(time, '%H%M')
    except ValueError:
        raise InvalidTimeError(
            time,
            f"Could not interpret string {time} as a date"
            f"Dates should follow format YYYYMMDD"
            )


def check_month_valid(month: str):
    """
    Improve docstrings
    """
    try:
        month = int(month)
    except ValueError:
        raise InvalidMonthError(month)

    else:
        if month <= 0 or month > 12:
            raise InvalidMonthError(month)


def check_year_valid(year: str):
    """
    Improve docstrings
    """
    try:
        year = int(year)
    except ValueError:
        raise InvalidYearError(year)

    else:
        if year < 1 or year > 9999:
            raise InvalidYearError(year)

# Note: this logic is exactly the same as check_level_valid
# Some refactoring is needed
def check_step_valid(step: str):
    """
    Check vailidity of a given step.

    Arguments
    ---------
    step : str
        Step to be checked. Step must be parsed as str
        representing a positive integer.
    """
    try:
        step = int(step)
    except ValueError:
        raise InvalidStepError(
            step,
            f"Invalid value in 'step': '{step}'. "
            "Steps must be integers or strings representing "
            "positive integer numbers."
        )
    else:
        if step < 0:
            raise InvalidStepError(
                step,
                f"Invalid value in 'step': '{step}'. "
                "Steps must be positive integers."
            )

def check_level_valid(level: str):
    """
    Check vailidity of a given level.

    Arguments
    ---------
    level : str
        Level to be checked. Level must be parsed  as str
        representing a positive integer.
    """
    try:
        level = int(level)
    except ValueError:
        raise InvalidLevelError(
            level,
            f"Invalid value in 'levelist': '{level}'. "
            "Levels must be integers or strings representing "
            "positive integer numbers."
        )
    else:
        if level < 0:
            raise InvalidLevelError(
                level,
                f"Invalid value in 'levelsit': '{level}'. "
                "Pressure levels must be positive integers."
            )


def check_params(params: List[Union[str, int]],
                 definitions=None
                 ):
    """
    Check `param` key of request.

    Params can be either GRIB paramIds or GRIB short names.

    Strings with no alphanumeric characters are interpreted as
    GRIB paramIds. ParamIds can be either parsed either as strings
    or integers.

    Strings with at least one alphanumeric character are interpreted as
    short names. Short names must be parsed as strings.

    By default, only short names in
    `gsv.requests.shortname_to_paramid.yaml` are accepted. More
    variables can be added defining a custom defition YAML file,
    mappint short names and GRIB codes, and parsing through the
    `definitions` argument.

    Arguments:
    ----------
    params : list[str | int]
        List of params to check.

    definitions : str
        Optional. Path to YAML file with defintions of extra
        short names and its GRIB paramIds. Short names not in
        default list will be appended. Short names that are already
        in the default list will be overwritten by the user defined
        ones (be careful with this). If None, only short names on
        default list can be used.
    """
    # Create list for consistency
    shortname2grib = _get_shortname_dict(definitions)

    if not isinstance(params, list):
        params = [params]

    for param in params:

        # Check for unknown shortnames
        if re.search('[a-zA-Z]', str(param)) \
        and str(param) not in shortname2grib:
            raise UnknownVariableError(
                variable=param,
                message=f"Unknown variable with short name {param}. "
                    f"GRIB key shortName must be used."
            )


def check_dates(dates: Union[List, str, int]):
    """
    Check `date` key of request.

    Dates can be parsed as explicit dates or implicit dates.

    Explicit dates must specify all the requested dates in a list
    or a tuple. Dates can be either integer or string. In both cases
    the number of digits must be exactly 8. Dates must follow
    format YYYYMMDD.

    Implicit dates are parsed as strings following a MARS-like syntax:
      - `20050401/to/20050405` will request all dates from `20050401`
      to `20050405`
      - `20050401/to/20050405/by/2` will request dates from `20050401`
      to `20050405` with a timestep of 2 days.
      - To specify a non-equally-spaced set of dates use explicit
      request.

    Arguments:
    ----------
    dates : list | str | int
        Set of dates to check parsed as either explicit or implcit
        dates.
    """
    # Unique explicit date as int
    if isinstance(dates, int):  # Explicit date as int
        dates = [dates]

    # Explicit dates as list or tuple
    if isinstance(dates, list) or isinstance(dates, tuple):
        for date in dates:
            if len(str(date)) !=8 or not re.search('\d{8}', str(date)):
                raise InvalidDateError(
                    date,
                    f"Cannot interpret date string {date}. Date must be "
                    "an 8-digit number with format YYYYMMDD."
                    )
            check_date_valid(str(date))

    # Implicit dates as MARS-like string
    elif isinstance(dates, str):
        match = re.match(
            IMPLICIT_DATE_PATTERN, dates
            )

        if match is None:
            raise InvalidDateError(
                dates,
                f"Could not interpret implicit dates request {dates}. "
                "Use format YYYYMMDD to ask for a unique date. "
                "Use YYYYMMDD/to/YYYYMMDD to ask for a range of dates. "
                "Use YYYYMMDD/to/YYYYMMDD/by/N to ask for a range of dates "
                "with a timestep of N days."
                )

        start_date = match.group(1)
        end_date = match.group(3) or match.group(4)
        step_date = match.group(5)

        check_date_valid(start_date)

        if end_date is not None:
            check_date_valid(end_date)

            if int(start_date) > int(end_date):
                raise InvalidDateError(
                    dates,
                    f"Invalid implicit date {dates}. Start date cannot be "
                    "larger than end date."
                )

            if step_date is not None and int(str(step_date)) == 0:
                raise InvalidDateError(
                    dates,
                    f"Invalid implicit date request {dates}. "
                    "Step between dates cannot be zero."
                )

    else:
        raise InvalidDateError(
            dates,
            "Wrong type for key 'date'. Use list of strings for explicit "
            "dates request or a string for implicit dates request."
        )


def check_times(times: Union[List, str, int]):
    """
    Check `time` key of request.

    Times are parsed as explicit times or implicit times.

    Explicit times must specify all the requested times in a list
    or a tuple. Times can be either integer or string. In both cases
    the number of digits must be exactly 4. Dates must follow
    format hhmm.

    Implicit times are parsed as strings following a MARS-like syntax:
      - `0000/to/1800` will request times from `0000`
      to `1800` with the default timestep of 1 hour
      - `0000/to/1800/by/0600` will request dates from `0000`
      to `1800` with a timestep of 6 hours.
      - To specify a non-equally-spaced set of times use explicit
      request.

    Note: The use of integers to specify times is highly discouraged,
    as integers with three digits will fail the check. This is
    intended to avoid ambigous strings as '120' which could be
    interpreted either as '01:20' or '12:00'.

    Arguments:
    ----------
    times : list | str | int
        Set of dates to check parsed as either explicit or implcit
        dates.
    """
    # Explicit time as int
    if isinstance(times, int):
        times = [times]

    # Explicit times as list or tuple
    if isinstance(times, list) or isinstance(times, tuple):
        for time in times:
            if len(str(time)) !=4 or not re.search('\d{4}', str(time)):
                raise InvalidTimeError(
                    time,
                    f"Cannot interpret time string {time}. Time must be " \
                    "a 4-digit number with format hhmm."
                    )
            check_time_valid(str(time))

    # Implicit times as MARS-like string
    elif isinstance(times, str):  # Implicit dates as MARS-like string
        match = re.match(
            IMPLICIT_TIME_PATTERN, times
            )

        if match is None:
            raise InvalidTimeError(
                times,
                f"Could not interpret implicit times request {times}. " \
                "Use format hhmm to ask for a unique time. "
                "Use hhmm/to/hhmm to ask for a range of times. " \
                "Use hhmm/to/hhmm/by/hhmm to ask for a range of times " \
                "with a timestep of hh hours and mm minutes."
                )

        start_time = match.group(1)
        end_time = match.group(3) or match.group(4)
        step_time = match.group(5)

        check_time_valid(start_time)

        if end_time is not None:
            check_time_valid(end_time)

            if int(start_time) > int(end_time):
                raise InvalidTimeError(
                    end_time,
                    f"Invalid implicit time {times}. Start time cannot be "
                    "larger than end time."
                    )

            if step_time is not None:  # Avoid infinite loops when processing
                check_time_valid(step_time)
                if step_time == "0000":
                    raise InvalidTimeError(
                    times,
                    f"Invalid implicit time request {times}. "
                    "Step between timesteps cannot be zero."
                )

    else:
        raise InvalidTimeError(
            times,
            "Wrong type for key 'time'. Use list of strings for explicit "
            "times request or a string for implicit times request."
            )


def check_months(months: Union[List, str, int]):
    """
    Improve docstrings
    """
    # Explicit month as int
    if isinstance(months, int):
        months = [months]

    # Explicit month as list or tuple
    if isinstance(months, list) or isinstance(months, tuple):
        for month in months:
            check_month_valid(str(month))

    # Implicit months as MARS-like string
    elif isinstance(months, str):  # Implicit months as MARS-like string
        match = re.match(
            IMPLICIT_MONTH_PATTERN, months
            )

        if match is None:
            raise InvalidMonthError(
                months,
                f"Could not interpret implicit months request {months}. " \
                "Use format 'a' to ask for a unique month. "
                "Use 'a/to/b' to ask for a range of months. " \
                "Use 'a/to/b/by/c' to ask for a range of months " \
                "with a timestep of c months. "
                "Months are represented by integers between 1 and 12."
                )

        start_month = match.group(1)
        end_month = match.group(3) or match.group(4)
        step_month = match.group(5)

        check_month_valid(start_month)

        if end_month is not None:
            check_month_valid(end_month)

            if int(start_month) > int(end_month):
                raise InvalidMonthError(
                    end_month,
                    f"Invalid implicit month {months}. Start month cannot be "
                    "larger than end month."
                    )

        if step_month is not None:
            check_month_valid(step_month)

    else:
        raise InvalidMonthError(months)

def check_years(years: Union[List, str, int]):
    """
    Improve docstrings
    """
    # Explicit month as int
    if isinstance(years, int):
        years = [years]

    # Explicit month as list or tuple
    if isinstance(years, list) or isinstance(years, tuple):
        for year in years:
            check_year_valid(str(year))

    # Implicit months as MARS-like string
    elif isinstance(years, str):  # Implicit months as MARS-like string
        match = re.match(
            IMPLICIT_YEAR_PATTERN, years
            )

        if match is None:
            raise InvalidYearError(
                years,
                f"Could not interpret implicit years request {years}. " \
                "Use format 'a' to ask for a unique year. "
                "Use 'a/to/b' to ask for a range of years. " \
                "Use 'a/to/b/by/c' to ask for a range of years " \
                "with a timestep of c years. "
                "Years are represented by integers between 1 and 9999."
                )

        start_year = match.group(1)
        end_year = match.group(3) or match.group(4)
        step_years = match.group(5)

        check_year_valid(start_year)

        if end_year is not None:
            check_year_valid(end_year)

            if int(start_year) > int(end_year):
                raise InvalidYearError(
                    end_year,
                    f"Invalid implicit year {years}. Start year cannot be "
                    "larger than end year."
                    )

        if step_years is not None:
            check_year_valid(step_years)

    else:
        raise InvalidYearError(years)


# Note: this logic is basically the same as check_levelist.
# Some refactoring needed here.
def check_steps(steps: Union[List, str, int]):
    """
    UPDATE DOCSTRINGS
    Check `time` key of request.

    Times are parsed as explicit times or implicit times.

    Explicit times must specify all the requested times in a list
    or a tuple. Times can be either integer or string. In both cases
    the number of digits must be exactly 4. Dates must follow
    format hhmm.

    Implicit times are parsed as strings following a MARS-like syntax:
      - `0000/to/1800` will request times from `0000`
      to `1800` with the default timestep of 1 hour
      - `0000/to/1800/by/0600` will request dates from `0000`
      to `1800` with a timestep of 6 hours.
      - To specify a non-equally-spaced set of times use explicit
      request.

    Note: The use of integers to specify times is highly discouraged,
    as integers with three digits will fail the check. This is
    intended to avoid ambigous strings as '120' which could be
    interpreted either as '01:20' or '12:00'.

    Arguments:
    ----------
    times : list | str | int
        Set of dates to check parsed as either explicit or implcit
        dates.
    """
    # Explicit step as int
    if isinstance(steps, int):
        steps = [steps]

    # Explicit steps as list or tuple
    if isinstance(steps, list) or isinstance(steps, tuple):
        for step in steps:
            check_step_valid(str(step))

    # Implicit steps as MARS-like string
    elif isinstance(steps, str):  # Implicit dates as MARS-like string
        match = re.match(
            IMPLICIT_STEP_PATTERN, steps
            )

        if match is None:
            raise InvalidStepError(
                steps,
                f"Could not interpret implicit steps request {steps}. " \
                "Use format 'a' to ask for a unique step. "
                "Use 'a/to/b' to ask for a range of steps. " \
                "Use 'a/to/b/by/c' to ask for a range of steps " \
                "with a timestep of c steps."
                )

        start_step = match.group(1)
        end_step = match.group(3) or match.group(4)

        check_step_valid(start_step)

        if end_step is not None:
            check_step_valid(end_step)

            if int(start_step) > int(end_step):
                raise InvalidStepError(
                    end_step,
                    f"Invalid implicit step {steps}. Start step cannot be "
                    "larger than end step."
                    )

    else:
        raise InvalidStepError(
            steps,
            "Wrong type for key 'step'. Use list of strings for explicit "
            "steps request or a string for implicit steps request."
            )


def check_levtype(levtype: str):
    """
    Check validity of key 'levtype'.

    Arguments
    ---------
    levtype : str
        Type of level for the requested variable(s). Levtype must be
        either 'sfc' or 'pl'.
    """
    # Check only one element is provided
    if isinstance(levtype, list):
        if len(levtype) > 1:
            raise NotImplementedError(
                "Requesting more than one 'levtype' is not supported. " \
                "Please, specify a unique 'levtype': 'sfc' or'pl'."
            )
        else:
            levtype = levtype[0]

    # Check disabled in order to admit some unplanned levtypes
    # # Check element is either 'sfc' or 'pl'
    # if levtype not in {"sfc", "pl"}:
    #     raise InvalidKeyError(
    #         levtype,
    #         f"Invalid value '{levtype}' for key 'levtype'. " \
    #         "'levtype' must be 'sfc' (surface) or 'pl' (pressure levels)."
    #     )


def check_levelist(levelist: Union[list, str, int]):
    """
    Check validity of the 'levleist' key.

    Arguments
    ---------
    levelsit : list | str | int
        Level or set of levels to request. A single level can be
        parsed either as string or integer. A set of discrete
        levels can be parsed as list (or tuple) of integers or
        strings. Mixed lists of strings and integers are also
        allowed. Implicit level requests are not supported.
    """
    # Ensure single level in list
    if isinstance(levelist, int) or isinstance(levelist, str):
        levelist = [levelist]

    # Explicit levels as list
    if isinstance(levelist, list) or isinstance(levelist, tuple):
        for level in levelist:
            check_level_valid(str(level))

    else:
        raise InvalidLevelError(
            levelist,
            f"Invalid value {levelist} of type {type(levelist)} "
            "for key 'levelist'. "
            "Levels must be parsed as integer or strings. "
            "A set of discrete levels can be specified with a list "
            "(or tuple) of either integers or strings."
        )


def check_output_grid(grid: Union[str, List]):
    """
    Check validity of key 'grid'

    Arguments
    ---------
    grid : str | list
        Pair of float numbers describing resolution of the target grid
        in degrees. If parsed as string, format must be '0.1/0.1'.
        Lists are also allowed (e.g. [0.1, 0.1]).
        """

    # Convert MARS-like string to list
    if isinstance(grid, str):
        grid = list(grid.split("/"))

    # Check length of list is 2
    if  isinstance(grid, list) or isinstance(grid, tuple):
        if len(grid) != 2:
            raise InvalidTargetGridError(
                grid,
                f"Unexpected number of values for key 'grid': {grid}. "
                f"{len(grid)} were given (2 were expected)."
            )

    else:
        raise InvalidTargetGridError(
            grid,
            f"Invalid value {grid} of type {type(grid)} for key 'grid' "
            "in request. Use list of two float values, or MARS-like string "
            "with format 0.1/0.1."
        )

    # Ensure list elements are (or can be converted to) float
    try:
        grid = float(grid[0]), float(grid[1])
    except ValueError:
        raise InvalidTargetGridError(
            grid,
            f"Could not interpret key 'grid': {grid}. Grid must "
            "parsed as a string with format '1.0/1.0' or as tuple of "
            "floats."
        )

    # Exclude negative resolutions
    if grid[0] <= 0 or grid[1] <= 0:
        raise InvalidTargetGridError(
            grid,
            f"Invalid value for key 'grid': {grid}. "
            "Grid values must be positive"
        )


def check_method(method: str):
    """
    Check validity of key 'method'.

    Arguments
    ---------
    method : str
        Description of requested interpolation method.
        Options are: 'nn' (nearest neighbor) and 'con'
        (first order conservative).
    """
    if method not in {'nn', 'con'}:
        raise InvalidInterpolationMethodError(method)


def check_area(area: Union[str, List]):
    """
    Check validity of key 'area'.

    Implicit values must be parsed as string with format N/W/S/E, where
    point represents the boundaries of the selected rectangular area.

    Explicit values are parsed as list (or tuple) of four values.

    Boundary values must meet several conditions:
     - North (N) and South (S) value must be between `90.0` and `-90.0`.
     - North (N) value must be greater or equal than south (S) value.
     - West (W) and East(E) values must be between -180.0 and 360.0.

    Arguments
    ---------
    area : str | list
        Set of four numbers describing boundaries (N,W,S,E) of output
        rectangle. If parsed as strings format must be 'N/W/S/E'.
        List are also allowed (e.g. [90, 0, -90, 360])
    """

    # Convert MARS-like string to list
    if isinstance(area, str):
        area = list(area.split("/"))

    # Check length of list is 4
    if  isinstance(area, list) or isinstance(area, tuple):
        if len(area) != 4:
            raise InvalidAreaError(
                area,
                "Area needs four parameters N/W/S/E."
            )

    else:
        raise InvalidAreaError(
            area,
            "Area cannot be interpeted. Use implicit or explicit formats."
        )

    # Ensure list elements are (or can be converted to) float
    try:
        area = float(area[0]), float(area[1]), float(area[2]), float(area[3])
    except ValueError:
        raise InvalidAreaError(
            area,
            "Area coordinates cannot be converted to float."
        )

    # Exclude invalid areas
    north, west, south, east = area[0], area[1], area[2], area[3]

    if not north >= south:  # A1
        raise InvalidAreaError(
            area,
            f"Invalid area {area}. North coordinate must be greater than "
            "south coordinate."
        )

    if not north <= 90.0:  # A4
        raise InvalidAreaError(
            area,
            f"Invalid area {area}. North coordinate cannot be greater than "
            "90.0."
        )
    if not south >= -90.0:  # A5
        raise InvalidAreaError(
            area,
            f"Invalid area {area}. South coordinate cannot be less than "
            f"-90.0."
        )
    if not west >= -180.0 or not west <= 360.0:  # A6
        raise InvalidAreaError(
            area,
            f"Invalid area {area}. West coordinate cannot be less than "
            "-180.0."
        )
    if not east >= -180.0 or not east <= 360.0:  # A7
        raise InvalidAreaError(
            area,
            f"Invalid area {area}. East coordinate canno be greater than "
            f"360.0."
        )

def check_requested_dates(request: dict):
    """
    Improve docstrings
    """
    if 'date' in request and 'time' in request:
        check_dates(request["date"])
        check_times(request["time"])
        if 'year' in request or 'month' in request:
            raise InvalidKeyError(
                'year/month',
                "Cannot have `date/time` and `year/month` keys in the "
                "same request. Requests must follow one of the two "
                "format only."
            )

        if 'step' in request:
            check_steps(request["step"])

    elif 'year' in request and 'month' in request:
        if 'date' in request or 'time' in request:
            raise InvalidKeyError(
                'date/time',
                "Cannot have `date/time` and `year/month` keys in the "
                "same request. Requests must follow one of the two "
                "format only."
            )

        if 'step' in request:
            raise InvalidKeyError(
                'step',
                "Cannot request key `step` when dates are specified "
                "with 'month' and 'year' keys."
            )
        check_years(request["year"])
        check_months(request["month"])

    else:
        raise MissingKeyError(
            'date',
            "Missing date specificaiton. Dates should be specified by "
            "specifyng date/time, date/time/step or month/year."
        )


def check_requested_levels(request: dict):
    """
    Check if requested 'levtype' and 'levelist' keys are coherent.

    For 'levtype'='sfc', no 'levelist' can be requsted.
    For 'levtype'='pl', a 'levelist' key must be provided. In this
    case, validity of 'levelist' key is also checked.

    Arguments
    ---------
    request : dict
        Request to check.
    """
    # Check levelist absent for sfc variables
    if request["levtype"] == "sfc":
        if "levelist" in request:
            raise UnexpectedKeyError(
                key="levelist",
                message="Unexpected key 'levelist' for variable with  "
                    "'levtype': 'sfc'."
            )

    # Check levelist for pressure levels
    elif request["levtype"] == "pl":

        if "levelist" not in request:
            raise MissingKeyError(
                key="levelist",
                message="Missing key 'levelist' for variable with "
                    "'levtype': 'pl'. List of pressure levels must be provided."
            )
        check_levelist(request["levelist"])


def check_requested_interpolation(request):
    """
    Check if requested 'grid' and 'method' are coherent.

    If no 'grid' is requested, 'method' cannot be requested.
    If 'grid' is requested, 'method' is optional. In case it is not
    requested, default value is 'nn'.

    Arguments
    ---------
    request : dict
        Request to check
    """
    if "grid" in request:
        check_output_grid(request["grid"])

        # Check interpolation method
        if "method" in request:
            check_method(request["method"])

    elif "method" in request:
        raise UnexpectedKeyError(
            key="method",
            message=f"Interpolation method {request['method']} was requested "
            "without requested any target grid. Please specify 'grid' "
            "key in request for interpolation."
        )

def check_requested_area(request):
    if "area" in request:

        if "grid" not in request:
            raise UnexpectedKeyError(
                key="area",
                message="Area selection is only supported for "
                "LonLat interpolated requests ."
                "Specify target output with the keyword 'grid'."
            )
        else:
            check_area(request["area"])

def check_request(request: Dict,
                  definitions=None
                  ):
    """
    Check validity of request.

    Arguments:
    ----------
    request : dict
        MARS request to check

    definitions : str
        Optional. Path to YAML file with defintions of extra
        short names and its GRIB paramIds. Short names not in
        default list will be appended. Short names that are already
        in the default list will be overwritten by the user defined
        ones (be careful with this). If None, only short names on
        default list can be used.
    """
    # Check compulsory fields
    COMPULSORY_KEYS = ["param", "levtype"]
    for key in COMPULSORY_KEYS:
        if key not in request:
            raise MissingKeyError(key)

    check_params(request["param"], definitions)
    check_levtype(request["levtype"])

    # Check dates
    check_requested_dates(request)

    # Check levtype and levelist
    check_requested_levels(request)

    # Check output grid and interpolation method
    check_requested_interpolation(request)

    # Check select area
    check_requested_area(request)
