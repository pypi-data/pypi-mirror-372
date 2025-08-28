import eccodes as ecc

from gsv.exceptions import UnknownLevtypeError


class SpatialCompletenessChecker:

    CHECKER_CODE = 8

    def __init__(self, msgid, logger):
        self.status = 0
        self.msgid = msgid
        self.logger = logger
        self.err_msg = None

    def check_atmos_variable(self):
        """Docstrings"""
        bit_map_indicator = ecc.codes_get(self.msgid, 'bitMapIndicator')

        if bit_map_indicator != 255:
            self.status = 1
            self.err_msg = (
                f"Spatial Completeness: Unexpected value for bitMapIndicator "
                f"{bit_map_indicator} for atmospheric variable. Atmospheric "
                f"variables should have bitMapIndicator=255 (no bitMap" 
                "present)."
            )

    def check_ocean_variable(self):
        """Docstrings"""
        bit_map_indicator = ecc.codes_get(self.msgid, 'bitMapIndicator')

        if bit_map_indicator != 0:
            self.status = 1
            self.err_msg = (
                f"Spatial Completeness: Unexpected value for bitMapIndicator "
                f"{bit_map_indicator} for oceanic variable. Oceanic "
                f"variables should have bitMapIndicator=0 (bitMap present "
                f"and specified in Section 6."
            )

    def get_checking_fn(self, levtype):
        """Docstrings"""
        if levtype in {"sfc", "pl", "hl", "sol"}:
            return self.check_atmos_variable

        elif levtype in {"o2d", "o3d"}:
            return self.check_ocean_variable

        else:
            raise UnknownLevtypeError(levtype)

    def run(self):
        levtype = ecc.codes_get(self.msgid, 'levtype')
        check = self.get_checking_fn(levtype)
        check()
