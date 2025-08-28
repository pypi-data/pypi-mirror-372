import typing as T

import numpy as np
import xarray as xr
import eccodes as ecc

from gsv.decoder.grid_decoder import read_grid
from gsv.decoder.level_decoder import get_level_reader
from gsv.decoder.time_decoder import read_time_coords
from gsv.decoder.attribute_decoder import read_attributes

from gsv.grids import Grid
from gsv.levels import LevelReader, SurfaceLevelReader


def decode_message(
        message: bytes,
        grid: T.Optional[Grid]=None,
        level_reader: T.Optional[LevelReader]=None
        ) -> xr.DataArray:
    """
    Decode GRIB message into xarray.DataArray.

    The GRIB message is decoded using ecCodes.

    The resulting xarray contains dimensions:
    ["time", "level", **spatial_coords] where
    the spatial_coords depend on the specific
    grid. For 2D variables the "level" dimension
    is flattened.

    Arguments:
    ----------
    message : bytes
        Full GRIB message to decode.
    grid : gsv.grids.Grid
        Grid object representing the source grid. If not provided
        it will be decoded from the GRIB message.
    level_reader: gsv.

    Returns:
    --------
    xr.DataArray:
        Decoded data from GRIB turned into a xarray format DataArray.
    """
    # Create ecCodes msgid
    msgid = ecc.codes_new_from_message(message)

    # Get variable name
    short_name = ecc.codes_get(msgid, "shortName")

    # Get grid and levels if not provided
    if grid is None:
        grid = read_grid(msgid)

    if level_reader is None:
        level_reader = get_level_reader(msgid)

    # Get values
    values = grid.read_values(msgid)

    # Mask values
    missing_value = ecc.codes_get(msgid, "missingValue")
    values = np.ma.masked_where(values==float(missing_value), values)

    # Get spatial coordinates and dims
    spatial_coords = grid.coords

    # Get vertical level
    level = level_reader.read_vertical_coordinate(msgid)

    # Get time coordinate
    time_coords = read_time_coords(msgid)

    # Get attributes
    attrs = read_attributes(msgid, grid)

    # Create Xarray Metadata
    coords = dict(time_coords, **{
        "level": level,
        **spatial_coords
    })
    dims = grid.dims

    # Reshape values for xarray
    values = grid.reshape_for_xarray(values)
    da = xr.DataArray(
        data=values, dims=dims, coords=coords, name=short_name ,attrs=attrs
        )

    # Flatten if variable is 2D
    if isinstance(level_reader, SurfaceLevelReader):
        da = da.isel(level=0).drop_vars("level")

    # Release handle
    ecc.codes_release(msgid)

    # Return DataArray
    return da
