import typing as T

import eccodes as ecc

from gsv.exceptions import InvalidSourceGridError
from gsv.grids import Grid, LonLatGrid, HealpixGrid, UnstructuredGrid


def _read_lonlat_grid(msgid: int) -> LonLatGrid:
    """
    Read the grid information of a global Regular LonLat grid.

    Global regular LonLat grid is defined by the number of points
    along lon (Ni) and along lat (Nj).

    Arguments:
    ----------
    msgid : int
        ecCodes message handle.

    Returns:
    --------
    LonLatGrid
        Object representation of the source LonLat grid.
    """
    ni = ecc.codes_get(msgid, "Ni")
    nj = ecc.codes_get(msgid, "Nj")
    return LonLatGrid(ni, nj)


def _read_healpix_grid(msgid: int) -> HealpixGrid:
    """
    Read the grid information of a HEALPix grid.

    HEALPix grid is defined by the Nside parameter (number of pixels
    in a side of one of the 12 primitive pixels), and ordering
    (ordering scheme for the pixels).

    Arguments:
    ----------
    msgid : int
        ecCodes message handle.

    Returns:
    --------
    HealpixGrid
        Object representation of the source HERALPix grid.
    """
    nside = ecc.codes_get(msgid, "Nside")
    nest = ecc.codes_get(msgid, "ordering")
    return HealpixGrid(nside, nest)


def _read_unstructured_grid(msgid: int) -> UnstructuredGrid:
    """
    Read the grid information of a unstructured grid.

    Cell coordinates and bounds for supported unstructured grids
    must be precalculated and stored in netCDF files,

    Arguments:
    ----------
    msgid : int
        ecCodes message handle.

    Returns:
    --------
    UnstructuredGrid
        Object representation of the source unstructured grid.
    """
    grid_name = ecc.codes_get(msgid, "gridName")
    grid_type = ecc.codes_get(msgid, "gridType")
    return UnstructuredGrid(grid_name, grid_type)


def _get_grid_reader(msgid: int) -> T.Callable:
    """
    Get the specific implementation of the grid reader function.

    Implementation depends on the grid type which can be either
    regular_ll (Regualr LonLat grid) or healpix (HEALPix grid).

    Arguments:
    ----------
    msgid : int
        ecCodes message handle.

    Returns:
    --------
    Callable
        Function with specific implementation for grid reader.
    """
    grid_type = ecc.codes_get(msgid, "gridType")
    if grid_type == "regular_ll":
        return _read_lonlat_grid
    elif grid_type == "healpix":
        return _read_healpix_grid
    elif grid_type in {"reduced_gg", "unstructured_grid"}:
        return _read_unstructured_grid
    else:
        raise InvalidSourceGridError(grid_type)


def read_grid(msgid: int) -> Grid:
    """
    Read the Grid definition from the ecCodes handle.

    A specific implementation of grid_reader is used, depending on
    the type of grid (regular lonlat, HEALPix or unstructured).

    Arguments:
    ----------
    msgid : int
        ecCodes message handle.

    Returns:
    --------
    gsv.grids.Grid
        Grid object representing the source grid.
    """
    grid_reader = _get_grid_reader(msgid)
    return grid_reader(msgid)


def decode_grid(message: bytes):
    """
    Decode the Grid definition from the GRIB message.

    Arguments:
    ----------
    message : bytes
        Full GRIB message to decode.

    Returns:
    --------
    gsv.grids.Grid
        Grid object representing the source grid.
    """
    msgid = ecc.codes_new_from_message(message)
    grid = read_grid(msgid)
    ecc.codes_release(msgid)
    return grid
