from dataclasses import dataclass

import eccodes as ecc

from .level_reader import LevelReader


@dataclass
class UnknownLevelReader(LevelReader):

    def read_level(self, msgid):
        """
        Read the level value of the GRIB message from the ecCodes handle msgid.

        For general (unknown) types of level, the value of the level key
        is read from the ecCodes handle msgid.

        Arguments:
        ----------
        msgid : int
            ecCodes message handle.

        Returns:
        --------
        int
            Numerical value of level key.
        """
        return ecc.codes_get(msgid, "level")

    @property
    def units(self):
        """
        Units of the numerical value of vertical level.

        For general (unkown) types of level, 'unknown' is reported.s
        """
        return "unknown"
