import eccodes as ecc


class SpatialConsistencyChecker:

    CHECKER_CODE = 4

    def __init__(self, msgid, keys, logger):
        self.status = 0
        self.msgid = msgid
        self.keys = keys
        self.logger = logger
        self.err_msg = None
    
    def run(self):
        for key, ref_value in self.keys.items():
            grib_value = ecc.codes_get(self.msgid, key)  # TODO: factor out this line to better test gridName

            # Workaround to remove _T/W/V/F suffix in eORCA grids
            if key == "gridName" and "eORCA" in grib_value:
                grib_value = grib_value.split('_')[0]

            if grib_value != ref_value:
                self.err_msg = (
                    f"Spatial Consistency: Missmatch between obtained "
                    f"and expected {key} value: {grib_value} was obtanied, "
                    f"but {ref_value} was expected."
                )
                # self.logger.error(self.err_msg)  # This err_msg does not whow. Why??
                self.status = 1
