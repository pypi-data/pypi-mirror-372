from pathlib import Path
import re

import eccodes as ecc


def is_data_local_destine(msgid):
    production_status_of_processed_data = ecc.codes_get(msgid, "productionStatusOfProcessedData")
    generation = ecc.codes_get(msgid, "generation")
    return production_status_of_processed_data in {12, 13} and generation != 1


class StandardComplianceChecker:

    CHECKER_CODE = 2

    STD_KEYS = {
        "editionNumber": 2,
        "centre": "ecmf",
#         "tablesVersion": 31,
        "productionStatusOfProcessedData": 12,
        "destineLocalVersion": 1
    }

    def __init__(self, msgid, logger):
        self.status = 0
        self.msgid = msgid
        self.logger = logger
        self.err_msg = ""

    @staticmethod
    def read_definition_file(filename):
        """
        Not used anymore, but kept for reference
        """
        PARAM_PATTERN = "'(\d+)'"
        DEF_PATTERN = "([a-zA-Z]+)\s\=\s(-?\d+)\s\;"

        with open(filename, 'r') as f:
            params = {}

            for line in f:
                # Identify paramId definition
                match = re.match(PARAM_PATTERN, line)
                if match:
                    current_param = match.group(1)

                    if current_param in params:  # pragma: no cover
                        raise Exception(  # TODO: Exception not checked. Can this even happen?
                            f"Duplicated paramId: {current_param} "
                            f"in definitions file {filename}"
                        )
                    params[current_param] = {}

                # Identify attribute
                match = re.search(DEF_PATTERN, line)
                if match:
                    key, value = match.group(1), match.group(2)
                    params[current_param][key] = value

        return params

    def run(self):

        # Check standard common keys
        for key, ref_value in self.STD_KEYS.items():
            grib_value = ecc.codes_get(self.msgid, key)

            if grib_value != ref_value:
                self.err_msg += (
                    f"Standard Compliance: Missmatch between obtained "
                    f"and expected {key} value: {grib_value} was obtanied, "
                    f"but {ref_value} was expected."
                )
                self.status = 1


