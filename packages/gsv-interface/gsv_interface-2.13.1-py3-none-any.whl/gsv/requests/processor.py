from typing import List, Dict, Union
import typing as T
from datetime import datetime, timedelta
import re

from gsv.requests.utils import (
    _get_shortname_dict, IMPLICIT_DATE_PATTERN, IMPLICIT_TIME_PATTERN,
    IMPLICIT_STEP_PATTERN
)


def _render_params(
        params: Union[List[Union[str, int]], str],
        definitions=None
        ) -> List[str]:
    """
    Convert shortnames into GRIB parameter numbers
    if needed.

    Arguments:
    ----------
    params : list[str] | str
        Parameter or list of parameters to render. If parameters are
        short_names they are converted into GRIB parameters.
        If parameters are GRIB parameters they are kept as they are.
        If only one parameter is passed, a list containing the rendered
        parameter is returned.

    definitions : str
        Optional. Path to YAML file with defintions of extra
        short names and its GRIB paramIds. Short names not in
        default list will be appended. Short names that are already
        in the default list will be overwritten by the user defined
        ones (be careful with this). If None, only short names on
        default list can be used.

    Returns:
    --------
    list[str]
        List of parameters as GRIB parameter numbers.
    """
    shortname2grib = _get_shortname_dict(definitions)

    if not isinstance(params, list):
        params = [params]

    return list(map(
        lambda param: shortname2grib[param] \
            if re.search('[a-zA-Z]', str(param)) \
            else str(param),
            params
        ))


def _render_dates(dates: Union[List, str, int]) -> List[str]:
    """
    Convert dates into list of explicit dates if needed.

    Arguments:
    ----------
    dates : List | str | int
        Set of dates parsed as either explicit or implcit dates.
        Explicit dates are converted to a list of strings
        for consistency. Implcit dates are first converted to
        explicit dates and returned as list of strings.

    Returns:
    --------
    list[str]
        Set of dates as list of strings.
    """
    # Explicit date as int
    if isinstance(dates, int):
        return [str(dates)]

    # Explicit dates as list or tuple
    if isinstance(dates, list) or isinstance(dates, tuple):
        return [str(date) for date in dates]

    # Implicit dates as MARS-like string
    if isinstance(dates, str):
        match = re.match(IMPLICIT_DATE_PATTERN, dates)
        start_date = match.group(1)
        end_date = match.group(3) or match.group(4)
        end_date = end_date if end_date else start_date
        step_date = int(match.group(5)) if match.group(5) else 1

        date_list = [start_date]

        while True:
            last_date =date_list[-1]
            next_date = datetime.strftime(
                datetime.strptime(last_date, '%Y%m%d')
                + timedelta(days=step_date),
                "%Y%m%d")

            if int(next_date) > int(end_date):
                break

            date_list.append(next_date)

        return date_list


def _render_times(times: Union[List, str, int]) -> List[str]:
    """
    Convert time into list of explicit times if needed.

    Arguments:
    ----------
    times : List | str | int
        Set of times parsed as either explicit or implcit times.
        Explicit times are converted to a list of strings
        for consistency. Implcit times are first converted to
        explicit times and returned as list of strings.

    Returns:
    --------
    list[str]
        Set of times as list of strings.
    """
    # Explicit date as int
    if isinstance(times, int):
        return [str(times)]

    # Explicit dates as list or tuple
    if isinstance(times, list) or isinstance(times, tuple):
        return [str(time) for time in times]

    # Implicit dates as MARS-like string
    if isinstance(times, str):
        match = re.match(IMPLICIT_TIME_PATTERN, times)
        start_time = match.group(1)
        end_time = match.group(3) or match.group(4)
        end_time = end_time if end_time else start_time
        step_time = int(match.group(5)) if match.group(5) else 100 # Otherwise?

        step_hours = step_time // 100
        step_minutes = step_time % 100
        end_time = datetime.strptime(end_time, '%H%M')
        time_list = [start_time]

        while True:
            last_time = datetime.strptime(time_list[-1], '%H%M')
            next_time = last_time \
                + timedelta(hours=step_hours, minutes=step_minutes)

            if (next_time > end_time or
                   next_time > datetime(year=1900, month=1, day=2)
            ):
                break

            time_list.append(datetime.strftime(next_time, '%H%M'))

        return time_list

def _render_steps(steps: Union[List, str, int]) -> List[str]:
    """
    Convert time into list of explicit times if needed.

    Arguments:
    ----------
    times : List | str | int
        Set of times parsed as either explicit or implcit times.
        Explicit times are converted to a list of strings
        for consistency. Implcit times are first converted to
        explicit times and returned as list of strings.

    Returns:
    --------
    list[str]
        Set of times as list of strings.
    """
    # Explicit step as int
    if isinstance(steps, int):
        return [str(int(steps))]

    # Explicit dates as list or tuple
    if isinstance(steps, list) or isinstance(steps, tuple):
        return [str(int(step)) for step in steps]

    # Implicit dates as MARS-like string
    if isinstance(steps, str):
        match = re.match(IMPLICIT_STEP_PATTERN, steps)
        start_step = int(match.group(1))
        end_step = match.group(3) or match.group(4)
        end_step = int(end_step) if end_step else start_step
        step_step = int(match.group(5)) if match.group(5) else 1 # Otherwise?

        return [str(step) for step in range(start_step, end_step+1, step_step)]


def _render_grid(grid: Union[str, List]):
    """
    Convert grid specification to list of floats, if needed.

    Arguments:
    ----------
    grid : str | list
        Pair of float numbers describing resolution of the target grid
        in degrees. If parsed as string, format must be '0.1/0.1'.
        Lists are also allowed (e.g. [0.1, 0.1]).
    """
    if isinstance(grid, str):
        grid = grid.split('/')

    return list((float(grid[0]), float(grid[1])))


def _render_area(area):
    """
    Convert area specification to list of loats, if needed.

    Arguments
    ---------
    area : str | list
        Set of four numbers describing boundaries (N,W,S,E) of output
        rectangle. If parsed as strings format must be 'N/W/S/E'.
        List are also allowed (e.g. [90, 0, -90, 360])

    Returns:
    List[float] : List of four float numbers describing boundaries
    (N, W, S, E).
    """
    if isinstance(area, str):
        area = area.split('/')

    return list((
        float(area[0]),
        float(area[1]),
        float(area[2]),
        float(area[3])
        ))


def process_request(
        user_request: Dict[str, T.Any],
        definitions: T.Optional[str]=None
        ) -> Dict[str, T.Any]:
    """
    Process user-friendly MARS request to pyfdb-readable syntax.

    Params are converted to list of strings containing GRIB2 codes.
    Dates are converted to explicit list of dates as strings.
    Times are converted to explicit list of times as strings.
    Output grid is converted to a tuple of two float numbers
    representing the resolution in degrees along dimensions lon and lat
    respectively.

    Arguments:
    ----------
    user_request : dict
        Request in user-friendly dict format

    definitions : str
        Optional. Path to YAML file with defintions of extra
        short names and its GRIB paramIds. Short names not in
        default list will be appended. Short names that are already
        in the default list will be overwritten by the user defined
        ones (be careful with this). If None, only short names on
        default list can be used.

    Returns:
    --------
    dict
        Request in pyfdb-readable format
    """
    user_request["param"] = _render_params(user_request["param"],
                                           definitions)

    # Render date and time
    if "date" in user_request:
        user_request["date"] = _render_dates(user_request["date"])
        user_request["time"] = _render_times(user_request["time"])

    # Render year and month
    if "year" in user_request:
        # _render steps is used as logic is exactly the same
        user_request["month"] = _render_steps(user_request["month"])
        user_request["year"] = _render_steps(user_request["year"])

    # Render step
    if "step" in user_request:
        user_request["step"] = _render_steps(user_request["step"])

    # Render output grid specification
    if "grid" in user_request:
        user_request["grid"] = _render_grid(user_request["grid"])
        user_request["method"] = user_request.get("method", "nn")

    if "area" in user_request:
        user_request["area"] = _render_area(user_request["area"])

    return user_request
