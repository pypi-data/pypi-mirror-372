from copy import deepcopy
from datetime import datetime, timedelta, date as ddate
from pathlib import Path
import random
from typing import Dict, List

import numpy as np
import yaml

from gsv.exceptions import (
    InvalidShortNameDefinitionPath,
    DateNotConvertableToMonthlyError
)


IMPLICIT_DATE_PATTERN = r'^(\d{8})(/to/(\d{8})|/to/(\d{8})/by/(\d+))?$'
IMPLICIT_TIME_PATTERN = r'^(\d{4})(/to/(\d{4})|/to/(\d{4})/by/(\d+))?$'
IMPLICIT_STEP_PATTERN = r'^(\d+)(/to/(\d+)|/to/(\d+)/by/(\d+))?$'
IMPLICIT_YEAR_PATTERN = r'^(\d{4})(/to/(\d{4})|/to/(\d{4})/by/(\d+))?$'
IMPLICIT_MONTH_PATTERN = r'^(\d+)(/to/(\d+)|/to/(\d+)/by/(\d+))?$'


def _get_shortname_dict(definitions=None):
    default_shortnames = Path(__file__).parent / "shortname_to_paramid.yaml"
    with open(default_shortnames, 'r') as f:
        short_names = yaml.safe_load(f)

    if definitions is not None:
        try:
            with open(definitions, 'r') as f:
                new_short_names = yaml.safe_load(f)

        except FileNotFoundError:
            raise InvalidShortNameDefinitionPath(definitions)

        else:
            # Add new params and overwrite existing ones
            short_names.update(new_short_names)

    return short_names

# Create alias for backwards compatibility
shortname2grib = _get_shortname_dict()

def expand_request_key(
        request_list: List[Dict], key_to_expand: str
        ) -> List[Dict]:
    """
    Expand a key of a request into different requests.

    Expanding a key refers to taking a dictionary having a list
    of values for a given key and returning a list of request,
    each one having a unique element as a value for that key.
 
    Arguments
    ---------
    request_lsit : list
        List of request to expand. A unique request or
        several requests can be parsed.
    key_to_expand : str
        Key that will be used to expand the request_list
        into a bigger list.

    Returns
    -------
    list
        List of request where the specified key has been expanded
        into different requests.
    """
    new_list = []

    for request in request_list:

        for element in request[key_to_expand]:
            new_request = deepcopy(request)
            new_request[key_to_expand] = element
            new_list.append(new_request)

    return new_list


def split_request(request: Dict, ordered_keys: List) -> List:
    """
    Split a request into a list of requests.

    Keys with more than one value are expanded into different requests,
    each one asking for a single value for that key.The set of keys
    to expand is determined by the user.

    Arguments:
    ----------
    request : dict
        MARS request to split
    ordered_keys : list
        List of keys to expand. Keys of request not present in
        ordered_keys will not be expanded. The order of the keys
        determine the order of the resulting list (first keys
        change slower).

    Returns:
    --------
    list
        List of MARS requets with some (or all) keys expanded into
        different requests.
    """
    request_list = [request]
    for key in ordered_keys:

        if key in request and  isinstance(request[key], list):
            request_list = expand_request_key(request_list, key)

    return request_list


def filter_request(request: Dict, keys: List):
    """
    Filter a request selecting only a subset of keys.

    Arguments:
    ----------
    request : dict
        MARS request to filter
    keys : list[str]
        List of keys to select from request. If some key in
        keys is not present in request, it is just omitted.

    Returns:
    --------
    dict
        Filtered request with only the desired keys.
    """
    return {key: request.get(key, None) for key in request.keys() & keys}

def omit_keys_from_request(request, keys):
    """
    Docstrings
    """
    return {key: value for key, value in request.items() if key not in keys}


def count_combinations(request: Dict, keys: List[str]):
    """
    Count combinations of any subset of keys in a request.

    Arguments:
    ----------
    request : dict
        Request to count combinations on.
    keys : list[str]
        List of keys to consider when counting combinations. Keys
        that are not in this list will not contribute to the counting.

    Returns:
    --------
    int
        Number of combinations on a given subset of a request
    """
    combinations = 1
    for value in filter_request(request, keys).values():
        if isinstance(value, list):
            combinations *= len(value)
    return combinations


def load_yaml(path) -> Dict:
    """
    Read request from YAML file.

    Arguments:
    ----------
    path : str
        Path to YAML file containing the request

    Returns:
    --------
    dict
        Request in a Python dict format
    """
    with open(path) as f:
        request = yaml.load(f, Loader=yaml.loader.SafeLoader)

    return request


def convert_to_step_format(request, start_date, start_time):
    """
    Convert a request from 'datetime format' to 'step' format.

    In 'datetime format', the `date` and `time` keys, refer
    to the simulated date and time respectively (and the `step` is
    typically set to 0).

    In the 'step' format, the `date` and `time` are fixed to
    the `start_date` and `start_time` of the simulation, and
    the simulated datetime is encoded in  the `step` key.

    Each integer increment in `step` means one hour from the
    simulation starting point.

    Arguments
    ---------
    request : dict
        Request for the gsv interface in 'datetime format'.
        Request must be a Python dict in explicit form.
    start_date : str
        String representation of the start_date. Format must be
        'YYYYMMDD
    start_time : str
        String representation of the start_time. Format must be
        'hhmm'

    Returns
    ------
    dict
        Request for the gsv interface in 'step' format, already
        processed.
    """
    start_dt = datetime.strptime(
        f"{start_date}:{start_time}", "%Y%m%d:%H%M"
        )

    # Make combinations of date and time
    date, time = request["date"], request["time"]
    combinations = np.array(np.meshgrid(date, time)).T.reshape(-1, 2)

    # Compute step for each combinations
    explicit_steps = []
    dt = [datetime.strptime(f"{date}:{time}", "%Y%m%d:%H%M")
          for date, time in combinations
        ]
    explicit_steps = [
        str(int((current_dt - start_dt).total_seconds() // 3600))
        for current_dt in dt
    ]

    # Update request
    request["date"] = start_date
    request["time"] = start_time
    request["step"] = explicit_steps

    return request


def convert_to_datetime_format(request):
    """
    Convert a request from 'step format' to 'datetime' format.

    In 'datetime format', the `date` and `time` keys, refer
    to the simulated date and time respectively (and the `step` is
    typically set to 0).

    In the 'step' format, the `date` and `time` are fixed to
    the `start_date` and `start_time` of the simulation, and
    the simulated datetime is encoded in  the `step` key.

    Each integer increment in `step` means one hour from the
    simulation starting point.

    Arguments
    ---------
    request : dict
        Request for the gsv interface in 'step' format.
        Request must be a Python dict in explicit form.
    start_date : str
        String representation of the start_date. Format must be
        'YYYYMMDD
    start_time : str
        String representation of the start_time. Format must be
        'hhmm'

    Returns
    ------
    dict
        Request for the gsv interface in 'step' format, already
        processed.
    """
    date, time, step = request["date"], request["time"], request["step"]

    if isinstance(date, list) or isinstance(date, tuple):
        if len(date) != 1:
            raise Exception(
                "Request in step format can only contain one start date."
            )
        date = date[0]

    if isinstance(time, list) or isinstance(date, tuple):
        if len(time) != 1:
            raise Exception(
                "Request in step format can only contain one start time"
            )
        time = time[0]

    if isinstance(step, list) or isinstance(step, tuple):
        if len(step) != 1:
            raise Exception(
                "Only requests of one step can be converted to datetime format"
            )
        step = step[0]


    # Extract start datetime
    start_dt = datetime.strptime(
        f"{date}:{time}", "%Y%m%d:%H%M"
        )

    # Compute valid time
    valid_dt = start_dt + timedelta(hours=int(step))
    valid_date = datetime.strftime(valid_dt, "%Y%m%d")
    valid_time = datetime.strftime(valid_dt, "%H%M")

    # Update request
    request["date"] = valid_date
    request["time"] = valid_time
    request["step"] = "0"

    return request


def convert_date_to_monthly(request, strict=False):
    """
    Convert request format from date/time to month/year.

    If multiple dates are provided, the month/year pair will be computed
    for every element in date and repeated elements will be removed.

    If strict flag is set to True, only request with full months
    (containing all the dates for any appearing month)and with no allowed.
    different months for different years will be allowed. This is done
    to ensure consistency between the request and for being able to
    recover the dates later on.

    TODO: arg explanation
    """
    request = deepcopy(request)
    date = deepcopy(request["date"])

    if not isinstance(date, list) and not isinstance(date, tuple):
        date = [date]

    month = list(set(map(lambda x: datetime.strptime(str(x), "%Y%m%d").month, date)))
    year = list(set(set(map(lambda x: datetime.strptime(str(x), "%Y%m%d").year, date))))
    request["month"] = [str(m) for m in month]
    request["year"] = [str(y) for y in year]

    del(request["date"])
    if "time" in request:
        del(request["time"])


    if strict:
        full_dates = convert_monthly_to_date(request)["date"]
        if set(date) != set(full_dates):
            raise DateNotConvertableToMonthlyError(date)

    return request

def convert_monthly_to_date(request):
    """
    Convert request format from date/time to month/year.

    Args...
    """
    request = deepcopy(request)
    month, year = request["month"], request["year"]

    if not isinstance(month, list) and not isinstance(month, tuple):
        month = [month]

    if not isinstance(year, list) and not isinstance(year, tuple):
        year = [year]

    dates = []
    for y in year:
        for m in month:
            first_date = ddate(year=int(y), month=int(m), day=1)
            current_date = first_date
            for _ in range(32):  # All loops should end in at most 31 steps.
                if current_date.month == int(m):
                    dates.append(datetime.strftime(current_date, "%Y%m%d"))
                    current_date = current_date + timedelta(days=1)
                else:
                    break

    request["date"] = dates
    del(request["month"])
    del(request["year"])
    return request


def pick_random_request(request):
    """Improve function"""
    new_request = {}

    for key, value in request.items():
        if isinstance(value, list) or isinstance(value, tuple):
            new_value = random.choice(value)
        else:
            new_value = value

        new_request[key] = new_value

    return new_request


def pick_random_requests(request, n_requests):
    """
    Improve function
    """
    request_list = []

    for _ in range(n_requests):
        request_list.append(pick_random_request(request))

    return request_list

def subsample_request(request, key, n_splits, split_id):
    new_request = deepcopy(request)
    original_value = new_request[key]
    new_value = original_value[split_id::n_splits]
    new_request[key] = new_value
    return new_request