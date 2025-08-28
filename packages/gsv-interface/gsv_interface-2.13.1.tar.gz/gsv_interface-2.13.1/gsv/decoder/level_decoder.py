import eccodes as ecc

from gsv.levels import (
    LevelReader, PressureLevelReader, SurfaceLevelReader, OceanLevelReader,
    UnknownLevelReader
)


def get_level_reader(msgid: int) -> LevelReader:
    """
    Get the specific implementation of the level reader class.

    Implementation depends on the `typeOfLevel` which one of `isobaricInhPa`
    (IFS pressure levels), `surface` (IFS 2D), `oceanSurface` (NEMO 2D) or
    `oceanModelLayer` (NEMO 3D).

    Arguments:
    ----------
    msgid : int
        ecCodes message handle.

    Returns:
    --------
    LevelReader
        Class with specific reading implementation for each type of level.
    """
    levtype = ecc.codes_get(msgid, "levtype")
    if levtype == "pl":
        return PressureLevelReader()
    elif any([
        levtype == "sfc",
        levtype == "o2d"
    ]):
        return SurfaceLevelReader()
    elif levtype == "o3d":
        return OceanLevelReader()
    else:
        return UnknownLevelReader()


def decode_level_reader(message: bytes) -> LevelReader:
    """
    Decode the GRIB message to get a suitable level reader class.

    Arguments:
    ----------
    message : bytes
        Full GRIB message to decode.

    Returns:
    --------
    LevelReader
        Class with specific reading implementation for each type of level.
    """
    msgid = ecc.codes_new_from_message(message)
    level_reader = get_level_reader(msgid)
    ecc.codes_release(msgid)
    return level_reader
