import os
from dataclasses import dataclass
import typing as T
from pathlib import Path

import eccodes as ecc
import xarray as xr

from .level_reader import LevelReader


@dataclass
class OceanLevelReader(LevelReader):

    level_meters = None
    GRID_DEFINITION_PATH: T.ClassVar[Path] = Path(
        os.environ["GRID_DEFINITION_PATH"]
    ) if "GRID_DEFINITION_PATH" in os.environ else None
    DEFINITION_FILE = "NEMO_levels_m.nc"

    def __post_init__(self):
        if self.GRID_DEFINITION_PATH is None:
            return

        level_file = self.GRID_DEFINITION_PATH / self.DEFINITION_FILE

        try:
            ds = xr.open_dataset(level_file)
            list_of_levels = ds["nav_lev"].values
            self.level_meters = dict(enumerate(list_of_levels, 1))


        except FileNotFoundError:
            self.level_meters = None

    def read_level(self, msgid):
        """
        Read the level value of the GRIB message from the ecCodes handle msgid.

        For NEMO 3D levels, model level number is read from the GRIB message
        and depth values are read from a file located at self.GRID_DEFINITON.
        Decoded value for depth is returned.

        Arguments:
        ----------
        msgid : int
            ecCodes message handle.

        Returns:
        --------
        float
            Numerical value of the vertical level (meters deep from ocean sfc)
        """
        level_number = ecc.codes_get(msgid, "level")
        if self.level_meters is None:
            return level_number

        return self.level_meters[level_number]

    @property
    def units(self) -> str:
        """
        Units of the numerical value of vertical level.

        For NEMO 3D levels, units are reported in meters, after
        the NEMO model level number has been decoded.
        """
        if self.level_meters is None:
            return "NEMO model layers"

        return "m"
