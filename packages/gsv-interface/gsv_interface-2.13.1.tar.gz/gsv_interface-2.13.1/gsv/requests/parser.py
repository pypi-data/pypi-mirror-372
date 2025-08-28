from pathlib import Path
import typing as T
from typing import Union

import yaml

from gsv.exceptions import InvalidRequestError
from gsv.requests.checker import check_request
from gsv.requests.processor import process_request


def parse_request(request: Union[str, T.Dict[str, T.Any]],
                  check_and_process: T.Optional[bool]=True,
                  definitions: T.Optional[str]=None
                  ) -> T.Dict[str, T.Any]:
    """
    Interpret user request and convert it to pyfdb-readable dict.

    Arguments:
    ----------
    request : str or dict
        If str, a path to YAML file is interpreted. This file is
        opened to obtain a dict and then processed
        If dict, request in dict form is interpreted, and is
        directly processed.

    check_and_process : bool, optional
        If True, request is checked and processed before returning.

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
        Dictionary containing MARS request in pyfdb-readable format.
    """
    parser = _get_parser(request)
    request = parser(request)

    if check_and_process:
        check_request(request, definitions)
        request = process_request(request, definitions)

    return request


def _get_parser(request):
    if isinstance(request, str) or isinstance(request, Path):
        return _parse_from_yaml
    elif isinstance(request, dict):
        return _parse_from_dict
    else:
        raise InvalidRequestError(request)


def _parse_from_yaml(request_file):
    with open(request_file) as f:
        request = yaml.safe_load(f)
    return request


def _parse_from_dict(request):
    return request
