import typing as T

import eccodes as ecc
from gribapi.errors import KeyValueNotFoundError

from gsv.grids import Grid


xarray_cf_attributes = {
    "long_name": "name",
    "units": "units",
    "standard_name": "cfName",
}


MARS_attributes = {
    "class",
    "dataset",
    "experiment",
    "activity",
    "model",
    "realization",
    "generation",
    "type",
    "stream",
    "resolution",
    "expver",
    "levtype",
}


GRIB_attributes = [
    "paramId",
    "shortName",
    "units",
    "name",
    "cfName",
    "cfVarName",
    "dataType",
    "missingValue",
    "numberOfPoints",
    "totalNumber",
    "typeOfLevel",
    "NV",
    "stepUnits",
    "stepType",
    "gridType",
    "gridDefinitionDescription",
]


def _read_xarray_cf_attributes(
    msgid: int, attributes: T.Dict[str, str]
) -> T.Dict[str, T.Any]:
    """
    Read minimal set of attributes for xarray DataArrays.

    Arguments:
    ----------
    msgid : int
        ecCodes message handle.
    attributes : dict[str, str]
        Mapping between xarray standard name and ecCodes equivalent name.

    Returns:
    --------
    dict[str, Any]
        Mapping of xarray keys with the corresponding values.
    """
    attrs = {}
    for xarray_key, grib_key in attributes.items():
        value = ecc.codes_get(msgid, grib_key)
        attrs[xarray_key] = value

    return attrs


def _read_GRIB_attributes(
    msgid: int, attributes: T.List[str]
) -> T.Dict[str, T.Any]:
    """
    Read the listed GRIB attributes from the ecCodes handle msgid.

    Arguments:
    ----------
    msgid : int
        ecCodes message handle.
    attributes : list[str]
        List of GRIB keys to read from message.

    Returns:
    --------
    dict[str, Any]
        Mapping of GRIB keys with the corresponding values.
    """
    attrs = {}
    for key in attributes:
        try:
            value = ecc.codes_get(msgid, key)
            attrs[f"GRIB_{key}"] = value
        except KeyValueNotFoundError:  # Skip missing attributes
            pass

    return attrs


def _read_MARS_attributes(
    msgid: int, attributes: T.List[str]
) -> T.Dict[str, T.Any]:
    """
    Read the listed MARS attributes from the ecCodes handle msgid.

    Arguments:
    ----------
    msgid : int
        ecCodes message handle.
    attributes : list[str]
        List of GRIB keys to read from message.

    Returns:
    --------
    dict[str, Any]
        Mapping of GRIB keys with the corresponding values.
    """
    attrs = {}
    for key in attributes:
        try:
            value = ecc.codes_get(msgid, key, ktype=str)
            attrs[key] = value
        except KeyValueNotFoundError:  # Skip missing attributes
            pass

    return attrs


def read_attributes(msgid: int, grid: Grid) -> T.Dict[str, T.Any]:
    """
    Read the whole set of attribute for a given DataArray.

    Arguments:
    ----------
    msgid : int
        ecCodes message handle.
    grid : gsv.grids.Grid
        Grid object representing the source grid.

    Returns:
    --------
    dict[str, Any]
        Mapping of GRIB keys with the corresponding values.
    """
    # Read xarray minimal CF attributes
    attrs = _read_xarray_cf_attributes(msgid, xarray_cf_attributes)
    mars_attrs = _read_MARS_attributes(msgid, MARS_attributes)
    attrs = dict(attrs, **mars_attrs)

    # Read all GRIB attributes
    new_grib_attributes = GRIB_attributes.copy()
    new_grib_attributes.extend(grid.ATTRIBUTES)
    grib_attrs = _read_GRIB_attributes(msgid, new_grib_attributes)
    attrs = dict(attrs, **grib_attrs)

    # Add custom attributes for GSV
    attrs["gridtype"] = grid.grid_type

    return attrs
