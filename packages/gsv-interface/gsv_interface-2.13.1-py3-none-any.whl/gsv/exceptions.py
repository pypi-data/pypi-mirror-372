

class MissingKeyError(Exception):

    def __init__(self, key, message=None):
        self.key = key
        self.message = message if message else (
            f"Missing key '{self.key}' in request."
        )
        super().__init__(self.message)


class InvalidKeyError(Exception):

    def __init__(self, key, message=None):
        self.key = key
        self.message = message if message else (
            f"Invalid key '{key}' in request."
        )
        super().__init__(self.message)


class UnexpectedKeyError(Exception):

    def __init__(self, key, message=None):
        self.key = key
        self.message = message if message else (
            f"Unexpected key '{key}' in request."
        )
        super().__init__(self.message)


class InvalidValueError(Exception):

    def __init__(self, key, value, message=None):
        self.key = key
        self.value = value
        self.message = message if message else (
            f"Invalid type '{key}'. Requested values must "
            f"be either 'str' or 'List[str]'."
        )
        super().__init__(self.message)


class InvalidDateError(InvalidValueError):

    def __init__(self, value, message=None):
        self.value = value
        self.message = message if message else (
            f"Invalid valie '{value}' for key 'date'. "
            f"'date' must be a eight-digit number with format 'YYYYMMDD'."
        )
        super().__init__('date', self.value, self.message)


class InvalidTimeError(InvalidValueError):

    def __init__(self, value, message=None):
        self.value = value
        self.message = message if message else (
            f"Invalid value {value} for key 'time'. "
            f"'time' must be a four-digit string with format 'hhmm'."
        )
        super().__init__('time', self.value, self.message)


class InvalidMonthError(InvalidValueError):

    def __init__(self, value, message=None):
        self.value = value
        self.message = message if message else (
            f"Invalid value {value} for key 'month'. "
            f"'Month' must be an integer between 1 and 12."
        )
        super().__init__('month', self.value, self.message)


class InvalidYearError(InvalidValueError):

    def __init__(self, value, message=None):
        self.value = value
        self.message = message if message else (
            f"Invalid value {value} for key 'year'. "
            f"'year' must be an integer between 1 and 9999."
        )
        super().__init__('month', self.value, self.message)


class InvalidStepError(InvalidValueError):

    def __init__(self, value, message=None):
        self.value = value
        self.message = message if message else (
            f"Invalid value {value} for key 'step'. "
            f"'step' must be a positive integer."
        )
        super().__init__('step', self.value, self.message)


class InvalidLevelError(InvalidValueError):

    def __init__(self, value, message=None):
        self.value = value
        self.message = message if message else (
            f"Invalid value {value} for key 'levelist'."
        )
        super().__init__('levelist', self.value, self.message)


class InvalidShapeError(Exception):

    def __init__(self, grid_id, grid_points, value_points, message=None):
        self.grid_id = grid_id
        self.grid_shape = grid_points
        self.value_shape = value_points
        self.message = message if message else (
            f"Cannot reshape values for xarray.\n"
            f"Expected  input grid: {grid_id}\n."
            f"Number of grid points: {grid_points}.\n"
            f"Number of values to reshape: {value_points}.\n"
            f"Number of grid points and values must be equal."
        )
        super().__init__(self.message)


class UnknownVariableError(Exception):

    def __init__(self, variable, message=None):
        self.variable = variable
        self.message = message if message else (
            f"Variable {variable} is not recognised "
            f"and cannot be interpolated."
        )
        super().__init__(self.message)


class InvalidInterpolationMethodError(Exception):

    def __init__(self, method, message=None):
        self.method = method
        self.message = message if message else (
            f"Invalid interpolation method '{method}'. "
            f"Method must be either 'nn' (nearest neighbor) or "
            f"'con' (first-order conservative)."
        )
        super().__init__(self.message)


class MissingDatareaderError(Exception):  # Not called

    def __init__(self, gsv, message=None):
        self.gsv = gsv
        self.message = message if message else (
            "No data has been requested to FDB. "
            "Cannot get source grid."
        )
        super().__init__(self.message)


class MissingDatasetError(Exception):

    def __init__(self, datareader, message=None):
        self.datareader = datareader
        self.message = message if message else (
            "None object was passed to GSVDecoder. "
            "A valid datareader needs to be passed."
        )
        super().__init__(self.message)


class InvalidRequestError(Exception):

    def __init__(self, request, message=None):
        self.request = request
        self.message = message if message else (
            f"Could not extract request from {request}. "
            f"Request must be parsed as Python dict or from YAML file."
        )
        super().__init__(self.message)


class InvalidSourceGridError(Exception):

    def __init__(self, grid_type, message=None):
        self.grid_type = grid_type
        self.message = message if message else (
            f"Cannot decode message with gridType {grid_type}."
            f"Suported grid types are r'regular_ll', 'healpix', "
            "'reduced_gg' and 'unstructured_grid'."
        )
        super().__init__(self.message)

class MissingSourceGridError(Exception):

    def __init__(self, message=None):
        self.message = message if message else (
            "Input grid is not set. Call 'set_input_grid' before "
            "interpolating."
        )
        super().__init__(self.message)

class UnsupportedUnstructuredGridError(Exception):

    def __init__(self, grid_name, supported_grids, message=None):
        self.grid_name = grid_name
        self.message = message if message else (
            f"Cannot decode GRIB message with grid {grid_name}. "
            f"Supported unstructured grids are: {supported_grids}."
        )
        super().__init__(message)


class InvalidTargetGridError(Exception):

    def __init__(self, grid, message=None):
        self.grid = grid
        self.message = message if message else (
            f"Could not interpret target grid {grid}. "
            f"'Grid' field in request must be a list of two integers "
            f"representing number of points along x and y direction."
        )
        super().__init__(self.message)


class MissingGSVMessageError(Exception):

    def __init__(self, request, message=None):
        self.request = request
        self.message = message if message else (
            f"Could not find any GRIB message matching request {request}."
        )
        super().__init__(self.message)


class MissingGridDefinitionPathError(Exception):

    def __init__(self, message=None):
        self.message = message if message else (
            "Environment variable `GRID_DEFINITION_PATH` is not "
            "set. This variable must point to the location of "
            "grid-defining netCDF files. Without this path "
            "Unstructured Grids cannot be decoded."
        )
        super().__init__(self.message)


class UnsupportedTypeOfLevelError(Exception):  # Not used at all

    def __init__(self, type_of_level, message=None):
        self.message = message if message else (
            f"GRIB TypeOfLevel '{type_of_level}' is not supported. "
            f"Supported values are 'isobaricInhPa' and 'surface'."
        )
        super().__init__(self.message)


class InvalidAreaError(Exception):

    def __init__(self, area, message=None):
        self.message = message if message else (
            f"Invalid area {area}. Please introduce a vaid region "
            f"in N/W/S/E format."
        )
        super().__init__(self.message)

class InvalidLoggingLevelError(Exception):

    def __init__(self, log_level, message=None):
        self.message = message if message else (
            f"Invalid logging level {log_level}. Valid options are "
            f"'DEBUG', 'INFO', 'WARNING', 'ERROR' and 'CRITICAL'."
        )
        super().__init__(self.message)

class DQCFailedError(Exception):

    def __init__(self, message=None):
        self.message = message if message else(
            "Checker stopped after checking all GRIB messages. "
            "Check ERROR messages in logs for more detailed info."
        )
        super().__init__(self.message)

class DQCDataAvailableError(Exception):

    def __init__(self, message=None):
        self.message = message if message else(
            "DQC: DataAvailableChecker FAILED."
        )
        super().__init__(self.message)

class DQCStandardComplianceError(Exception):

    def __init__(self, message=None):
        self.message = message if message else(
            "DQC: StandardComplianceChecker FAILED"
        )
        super().__init__(self.message)

class DQCSpatialConsistencyError(Exception):

    def __init__(self, message=None):
        self.message = message if message else(
            "DQC: SpatialConsistencyChecker FAILED"
        )
        super().__init__(self.message)

class DQCSpatialCompletenessError(Exception):

    def __init__(self, message=None):
        self.message = message if message else(
            "DQC: SpatialCompletenessChecker FAILED"
        )
        super().__init__(self.message)

class DQCPhysicalPlausibilityError(Exception):

    def __init__(self, message=None):
        self.message = message if message else(
            "DQC: PhysicalPlausibility FAILED"
        )
        super().__init__(self.message)

class InvalidShortNameDefinitionPath(Exception):

    def __init__(self, def_file, message=None):
        self.def_file = def_file
        self.message = message if message else (
            f"Cannot find any file in {def_file}. Please specify a "
            f"valid definitions file or use the default short name "
            f"table, by not specifying any definitions."
        )
        super().__init__(self.message)

class DQCInvalidHaltModeError(Exception):

    def __init__(self, halt_mode, message=None):
        self.halt_mode = halt_mode
        self.message = message if message else (
            f"Invalid value for 'halt_mode': {halt_mode}. "
            f"Valid options are: 'always, 'end' and 'off'."
        )
        super().__init__(self.message)

class NoMessageDecodedError(Exception):

    def __init__(self, message=None):
        self.message = message if message else (
            "No message was found in datareader."
        )
        super().__init__(self.message)

class InvalidEngineError(Exception):

    def __init__(self, engine, message=None):
        self.engine = engine
        self.message = message if message else (
            f"Invalid option for engine: {engine}"
            f"Valid options are: 'fdb' and 'polytope'."

        )
        super().__init__(self.message)

class InvalidOutputTypeError(Exception):

    def __init__(self, output_type, message=None):
        self.engine = output_type
        self.message = message if message else (
            f"Invalid option for output_type: {output_type}"
            f"Valid options are: 'xarray' and 'grib'"
        )
        super().__init__(self.message)

class UnknownLevtypeError(Exception):

    def __init__(self, levtype, message=None):
        self.levtype = levtype
        self.message = message if message else (
            f"Unknown levtype: {levtype}. "
            f"Valid options are: 'sfc', 'pl', 'o2d', 'o3d', 'hl', and 'sol'."
        )
        super().__init__(self.message)

class DQCMissingProfilesError(Exception):

    def __init__(self, profile_path, profiles, exclude_profiles, message=None):
        self.profile_path = profile_path
        self.profiles = profiles
        self.exclude_profiles = exclude_profiles
        self.message = message if message else (
            f"Could not find any profile YAML file in profile_path: "
            f"{profile_path}."
            f"(profiles: {profiles})"
            f"(exlice_profiles: {exclude_profiles})"
        )
        super().__init__(self.message)

class DQCInvalidProfilesSpecificationError(Exception):

    def __init__(self, profile_path, profiles, exclude_profiles, message=None):
        self.profile_path = profile_path
        self.profiles = profiles
        self.exclude_profiles = exclude_profiles
        self.message = message if message else (
            f"Arguments 'profiles' and 'exclude_profiles' cannot be "
            f"simultaneously speficied. At least one of then must be "
            f"None:\n"
            f"profile_path: {profile_path}\n"
            f"profiles: {profiles}\n"
            f"exclude_profiles: {exclude_profiles}\n"
        )
        super().__init__(self.message)

class DQCMissingStartDateError(Exception):

    def __init__(self, message=None):
        self.message = message if message else (
            "Start date is missing."
        )
        super().__init__(self.message)

class DateNotConvertableToMonthlyError(Exception):

    def __init__(self, date, message=None):
        self.date = date
        self.message = message if message else (
            f"Date list: {date} cannot be converted to monthly format."
            f"Check that the following conditions are met:\n"
            f"  1. No dates missing for any present month.\n"
            f"  2. All years have the same set of months.\n"
        )
        super().__init__(self.message)

class DQCInconsistentDateUpdateRequestedError(Exception):

    def __init__(self, keys_to_update, message=None):
        self.keys_to_update = keys_to_update
        self.message = message if message else (
            f"Inconsistent date keys requested: {keys_to_update} "
            f"for updating DQC profile time coordinates. "
            f"Keys 'date' and 'time' cannot be mixed with "
            f"keys 'year', and 'month'. Please use only one set of keys."
        )
        super().__init__(self.message)

class UnknownDatabridgeError(Exception):

    def __init__(self, databridge, message=None):
        self.databridge = databridge
        self.message = message if message else (
            f"Unknown databridge: {databridge}. "
            f"Valid options are: 'lumi' and 'mn5'."
        )
        super().__init__(self.message)
