from dataclasses import dataclass

from .level_reader import LevelReader


@dataclass
class SurfaceLevelReader(LevelReader):

    def read_level(self, msgid):
        """
        Read the level value of the GRIB message from the ecCodes handle msgid.

        For surface variables, level value is set to zero.

        Arguments:
        ----------
        msgid : int
            ecCodes message handle. Even if not used, it is required
            for consistent interface between LevelReader objects.

        Returns:
        --------
        int
            Numerical value of the pressure level (in hPa)
        """
        return 0

    @property
    def units(self):
        """
        Units of the numerical value of vertical level.

        For surface variables, units are set to "m".
        """
        return "m"
