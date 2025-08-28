from abc import ABC, abstractmethod
from dataclasses import dataclass
import typing as T

import xarray as xr


@dataclass
class LevelReader(ABC):

    @abstractmethod
    def read_level(self, msgid: int) -> T.Any:
        """
        Read the level value of the GRIB message from the ecCodes handle msgid.

        Arguments:
        ----------
        msgid : int
            ecCodes message handle.

        Returns:
        --------
        Any
            Numerical value of the vertical level of GRIB message.
        """

    @property
    @abstractmethod
    def units(self) -> str:
        """
        Units of the numerical value of vertical level.
        """

    def read_vertical_coordinate(self, msgid):
        """
        Read vertical coordinate DataArray from the ecCodes handle msgid.

        DataArray must contain both the numerical value of the level and
        its units.

        Arguments:
        ----------
        msgid : int
            ecCodes message handle.

        Returns:
        --------
        xr.DataArray
            DataArray of dimensions {'level': 1} with the correct value
            and units attribute for the vertical coordinate.
        """
        level = self.read_level(msgid)
        units = self.units

        return xr.DataArray(
        data=[level], dims={'level': 1},
        attrs={
            "standard_name": "level",
            "units": units
        },
        name="level"
    )
