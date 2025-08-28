from dataclasses import dataclass

import eccodes as ecc

from .level_reader import LevelReader


@dataclass
class PressureLevelReader(LevelReader):

    def read_level(self, msgid):
        """
        Read the level value of the GRIB message from the ecCodes handle msgid.

        For IFS pressure levels, value of pressure level is read from the
        GRIB message, using the ecCodes handle msgid.

        Arguments:
        ----------
        msgid : int
            ecCodes message handle.

        Returns:
        --------
        int
            Numerical value of the pressure level (in hPa)
        """
        return ecc.codes_get(msgid, "level")

    @property
    def units(self):
        """
        Units of the numerical value of vertical level.

        For IFS pressure levels, units are reported in 'hPa'.
        """
        return "hPa"
