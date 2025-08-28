import eccodes as ecc
import numpy as np


class PhysicalPlausibilityChecker:

    CHECKER_CODE = 16

    def __init__(self, msgid, logger, variable_db):
        self.status = 0
        self.msgid = msgid
        self.logger = logger
        self.variable_db = variable_db
        self.err_msg = ""

    def run(self):
        param_id = ecc.codes_get(self.msgid, 'paramId')
        short_name = ecc.codes_get(self.msgid, 'shortName')

        # Read values
        values = ecc.codes_get_array(self.msgid, 'values')
        bitmap_indicator = ecc.codes_get(self.msgid, 'bitMapIndicator')

        if bitmap_indicator == 0:
            missing_value = ecc.codes_get(self.msgid, 'missingValue')
            values = np.ma.masked_equal(values, missing_value)


        max_value = np.nanmax(values)
        min_value = np.nanmin(values)

        try:
            variable = self.variable_db[param_id]
        except KeyError:
            self.status = 1
            self.err_msg += (
                f"Variable {param_id} ({short_name}) is not defined in "
                "dqc/profiles/conf/variables. "
                "Physical Plausibility cannot be checked."
            )
            return None

        check_enabled = variable.get("check_enabled", True)
        if not check_enabled:
            self.logger.debug(
                f"Skipping physical plausability check on variable "
                f"{param_id} [{short_name}] (check_enabled: False)"
            )
            return None

        # Check maximum value if needed
        if 'max' in variable:
            max_ref = variable["max"]

            if max_value > max_ref:
                self.status = 1
                self.err_msg += (
                    f"Unprobable value for variable {short_name}: {max_value} "
                    f"greater than theoretical max {max_ref}. "
                )

        # Check minimum if needed
        if 'min' in variable:
            min_ref = variable["min"]

            if min_value < min_ref:
                self.status = 1
                self.err_msg += (
                    f"Unprobable value for variable {short_name}: {min_value} "
                    f"less than theoretical min {min_ref}."
                )

        # Check at least one value passes the lower treshold if needed
        if 'lower_treshold' in variable:
            lower_treshold = variable["lower_treshold"]

            if max_value < lower_treshold:
                self.status = 1
                self.err_msg += (
                    f"Unprobable maximum value for variable {short_name}: "
                    f"{min_value} less than lower treshold: {lower_treshold}. "
                    f"Data units may be incorrect."
                )