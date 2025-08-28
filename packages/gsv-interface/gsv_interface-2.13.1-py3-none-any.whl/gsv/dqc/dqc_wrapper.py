from copy import deepcopy
import collections.abc
import inspect
import os
from pathlib import Path
import typing as T

import eccodes as ecc
import yaml

from gsv import GSVRetriever
from gsv import __version__ as gsv_version
from gsv.iterator import MessageIterator, StreamMessageIterator
from gsv.requests.checker import check_requested_dates
from gsv.requests.parser import parse_request
from gsv.requests.utils import (
    convert_to_step_format,
    convert_date_to_monthly,
    count_combinations,
    pick_random_requests,
    subsample_request
)
from gsv.exceptions import (
    DQCDataAvailableError,
    DQCStandardComplianceError,
    DQCSpatialConsistencyError,
    DQCSpatialCompletenessError,
    DQCPhysicalPlausibilityError,
    DQCInvalidHaltModeError,
    DQCFailedError,
    DQCMissingProfilesError,
    DQCInvalidProfilesSpecificationError,
    DQCMissingStartDateError,
    DQCInconsistentDateUpdateRequestedError,
    DateNotConvertableToMonthlyError,
)
from gsv.logger import get_logger

from .data_available_checker import DataAvailableChecker
from .standard_compliance_checker import StandardComplianceChecker
from .spatial_consistency_checker import SpatialConsistencyChecker
from .spatial_completeness_checker import SpatialCompletenessChecker
from .physical_plausibility_checker import PhysicalPlausibilityChecker


class DQCWrapper:
    """
    Class to handle the Data Quality Checker run and its outputs.

    The Data Quality Checker takes some profile files as arguments
    and performs various check on the Data defined on those profile
    files.

    Profile files must contain the MARS requests for the messages
    being checked. Additional information is also defined in the
    profiles.

    Current profile files for ClimateDT production runs can be found
    at gsv/dqc/profiles/production.

    Available Checkers are:

    Data Available Checker: Checks that all messages expected to be
    written by the model can be accessed through FDB.

    Spatial Consistency Checker: Checks that the grid encoded in the
    GRIB message corresponds to the expected grid.

    Spatial Completeness Checker: Checks that the atmospheric values
    have no masked regions, and that ocean values have masked regions.
    The point to point check to validate that masked regions correspond
    to land regions is not implemented yet.

    Physical Plausibility Checker: Checks that for every variable. All
    values are inside physically reasonable ranges. The allowed max
    and min values for each variables are defined in:
    gsv/dqc/profiles/conf/variables.yaml NOTE: Currently, failures on
    this checker do not raise ERRORs, but just WARNINGs.
    """

    def __init__(
            self,
            profile_path: str,
            profiles: T.Optional[T.List[str]]=None,
            exclude_profiles: T.Optional[T.List[str]]=None,
            allow_submonthly_chunks: bool=False,
            expver: T.Optional[str]=None,
            date: T.Optional[str]=None,
            time: T.Optional[str]=None,
            year: T.Optional[str]=None,
            month: T.Optional[str]=None,
            start_date: T.Optional[str]=None,
            start_time: str="0000", # This should be reseted to None
            model: str="IFS-NEMO",
            experiment: str='hist',
            activity: str='CMIP6',
            realization: int=1,
            generation: T.Optional[int]=None,
            additional_keys:  T.Optional[T.Dict[str, T.Any]]=None,
            logging_level: str="DEBUG",
            fdb5_config_file: T.Optional[str]=None,
            sample_length: T.Optional[int]=None,
            halt_mode: T.Optional[str]=None,
            check_standard_compliance: bool=True,
            check_spatial_consistency: bool=True,
            check_spatial_completeness: bool=True,
            check_physical_plausibility: bool=True,
            use_stream_iterator: bool=False,
            variables_config=None,
            n_proc=1,
            proc_id=0
        ):
        """
        Constructor for DQCWrapper class. (TODO: update docstrings)

        Arguments
        ---------
        profile_path: str
            Path where profile files are located

        profiles: List[str] (optional)
            List of paths for profile files (relative to profile_path)
            to use when checking. This allows checking only specific
            profiles. If not provided, all .yaml files in profile_path
            are used.

        expver: str (optional)
            Key `expver` of the experiment being checked. This
            overwrites the `expver` defined in the profile. If not
            provided, the `expver` key defined in the profile is used.

        date: str (optional).
            Implicit dates for the period of data being checked. This
            overwrites the `date` key defined in the profile. If not
            provided the `date` key defined in the profile is used.

        time: str (optional).
            Implicit times for the period of data being checked. This
            overwrites the `time` key defined in the profile. If not
            provided the `time` key defined in the profile is used.

        TODO update docstrigns

        start_date: str (optional)
            Start date of the experiment for the data being checked.
            This must be provided if data is in 'step format'.

        start_time: str (optional)
            Start date of the experiment for the data being checked.
            This is only used if data is in 'step format'. If not
            provided and needed, '0000' is asumed.

        model: str (optional)
            Name of the model that generate the data being checked.
            This overwrites the `model` key defined in the profiles.
            Valid options are 'IFS', 'IFS-NEMO', 'IFS-FESOM' and 'ICON'.
            If not provided 'IFS-NEMO' is assumed.

        experiment: str (optional)
            Name of the experiment configuration that generated
            the data being checked. This overwrites the `experiment`
            key defined in the profiles. If not provided
            'hist' is assumed.

        activity: str (optional)
            Name of the multIO activity of the experiment that
            generated the data being checked. This overwrites
            the `activity` key defined in the profiles. If not provided
            'CMIP6' is assumed.

        realization: int (optional)
            Number of the ensemble member to be checked. This
            overwrittes the `realization` key defined in the profiles.
            If not provided 1 is asumed.

        generation: int (optional)
            Number of the destine generation of the data being checked.
            All ClimateDT Phase 1 data is generation 1. Current Phase 2
            data is generation 2. This overwrites the `generation` key
            in the profiles. If not provided, the `generation` key in
            the profile is used.

        additional_keys: dict (optional)
            Additional MARS keys to overwrites the ones defined in
            profile files. If not provided no additional keys are
            overwriten.

        logging_level: str (optional)
            Logging level for the gsv interface. If not provided
            level is set to DEBUG (maximum verbosity).

        fdb5_config_file: str (optional)
            Path to the FDB5_CONFIG_FILE. If not provided, the one
            defined in the environment variable FDB5_CONFIG_FILE or
            FDB_HOME is used.

        sample_length: int (optional)
            Number of messages to apply the check for each profile.
            If provided, only N messages (randomly picked from request)
            will be checked. If not provided, all found messages
            will be checked (DataAvailableChecker always applies to
            all messages defined in the profiles, regardless of the
            `sample_length` value).

        halt_mode: str (optional)
            Set when the DQC is supossed to stop and raise an error.
            Accepted valeus are:
                - "always": checker stops at the first error.
                - "end": checker stops only after checking all messages.
                - "off": checker never raises any error, only logs.
            Default is "end".

        check_standard_compliance: bool (optional)
            If True, Standard Compliance Checker will be run.
            If False, it will not. Default is True.

        check_spatial_consistency: bool (optional)
            If True, Spatial Consistency Checker will be run.
            If False, it will not. Default is True.

        check_spatial_completeness: bool (optional):
            If True, Spatial Completeness Checker will be run.
            If False, it will be not. Default is True.

        check_physical_plausibility: bool (optional):
            If True, Physical Plausibility Checker will be run.
            If False, it will not. Default is True.

        use_stream_iterator: bool (optional):
            If True, StreamMessageIterator will be used for reading
            the GRIB messages.
            If False, normal MessageIterator will be used.
         """
        self.logging_level = logging_level
        self.logger = get_logger(logger_name=f"DQC-{proc_id+1}/{n_proc}", logging_level=self.logging_level)
        self.profile_path = profile_path
        self.profiles = self.get_data_profiles(profile_path, profiles, exclude_profiles)
        self.allow_submonthly_chunks = allow_submonthly_chunks
        self.expver = expver
        self.date = date
        self.time = time
        self.year = year
        self.month = month
        self.start_date = start_date
        self.start_time = start_time
        self.model = model
        self.experiment = experiment
        self.activity = activity
        self.realization = realization
        self.generation = generation
        self.additional_keys  = additional_keys
        self.fdb5_config_file = fdb5_config_file
        self.sample_length = sample_length
        self.halt_mode = halt_mode if halt_mode is not None else "end"
        self._check_standard_compliance = check_standard_compliance
        self._check_spatial_consistency = check_spatial_consistency
        self._check_spatial_completeness = check_spatial_completeness
        self._check_physical_plausibility = check_physical_plausibility
        self.use_stream_iterator = use_stream_iterator
        self.any_failed = False
        self.variables_config=variables_config
        self.n_proc=n_proc
        self.proc_id=proc_id

        self.validate_halt_mode()
        self.param_definitions = None
        self.variable_db = self.read_variable_database(user_db_path=self.variables_config)


    def validate_halt_mode(self):
        if self.halt_mode not in {"always", "end", "off"}:
            raise DQCInvalidHaltModeError(
                self.halt_mode
            )

    def get_data_profiles(
            self,
            profile_path: str,
            profiles: T.Optional[T.List[str]],
            exclude_profiles: T.Optional[T.List[str]],
            ) -> T.List[T.Dict]:
        """
        Get a list of data profiles in dictionary form.

        All profile files need to be in the same parent profile_path.
        If profiles is not, all .yaml files of profile_path are taken
        into account.

        All yaml files are read and returned as a list of dictionaries.

        Arguments
        ---------
        profile_path: str
            Parent directory where all profile files are stored.
        profiles: str or None
            List or None
            List of file names with the data profile to be checked.
            If None, all files in profile_path are taken.

        Returns
        -------
        List[Dict]
            List of loaded profile paths in Dictionary form.
        """
        # Complain if both profiles and exclude_profiles are defined
        if profiles is not None and exclude_profiles is not None:
            raise DQCInvalidProfilesSpecificationError(profile_path, profiles, exclude_profiles)  # TOFIX: Exception not checked

        if profiles is None:
            profile_files = list(Path(profile_path).glob('*.yaml'))
        else:
            profile_files = [
                Path(profile_path) / profile for profile in profiles
                ]

        # Filter out profiles in exclude profiles
        # TODO: some logs to tell which profiles have been removed
        if exclude_profiles:
            filtered_profiles = []
            for p in profile_files:
                if p.name in exclude_profiles:
                    self.logger.warning(
                        f"Excluding profile {p}"
                    )
                else:
                    filtered_profiles.append(p)
            profile_files = filtered_profiles

        # Open and read files
        profiles = []
        for profile in profile_files:
            try:
                with open(profile, 'r') as f:
                    new_profile = yaml.safe_load(f)
                    new_profile["file"] = profile
                    profiles.append(new_profile)
            except FileNotFoundError:
                self.logger.warning(
                    f"Could not find file {profile}. File will be skipped."
                )

            # TODO: Add exception for wrong formatted YAML

        if not profiles:
            raise DQCMissingProfilesError(profile_path, profiles, exclude_profiles=None)

        return profiles

    @staticmethod
    def load_yaml_file(yaml_file: str) -> T.List[T.Dict[str, T.Any]]:
        """
        Load a YAML file into a dictionary.

        Arguments
        ---------
        yaml_file: str
            Path to a YAML file.

        Returns
        -------
            Content of the YAML in dictionary form.
        """
        with open(yaml_file, 'r') as f:
            db = yaml.safe_load(f)
        return db

    @classmethod
    def update_variables_database(cls, default_db, user_db):
        default_db = deepcopy(default_db)
        for key, value in user_db.items():
            if isinstance(value, collections.abc.Mapping):
                default_db[key] = cls.update_variables_database(default_db.get(key, {}), value)
            else:
                default_db[key] = value
        return default_db

    def update_expver(self, request: T.Dict[str, T.Any]) -> T.Dict[str, T.Any]:
        """
        Update the `expver` key of the request.

        Arguments
        ---------
        request: Dict
            Request to be updated.

        Returns
        -------
        Dict
            Request with the updated key.
        """
        if self.expver is not None:
            request["expver"] = self.expver
        return request

    def update_date(self, request: T.Dict[str, T.Any]) -> T.Dict[str, T.Any]:
        """
        Update the `date` key of the request.

        Arguments
        ---------
        request: Dict
            Request to be updated.

        Returns
        -------
        Dict
            Request with the updated key.
        """
        valid_keys = {"date", "time", "year", "month"}
        new_date_request = {key: getattr(self, key) for key in valid_keys if getattr(self, key) is not None}

        if "date" in new_date_request or "time" in new_date_request:
            if "month" in new_date_request or "year" in new_date_request:
                raise DQCInconsistentDateUpdateRequestedError(new_date_request)

            if "date" in new_date_request:
                request["date"] = new_date_request["date"]

            if "time" in new_date_request:
                request["time"] = new_date_request["time"]
            else:
                if "time" not in request:  # Add default time for clmn profiles updated with date and time
                    request["time"] = "0000"

            if "month" in request:
                del request["month"]

            if "year" in request:
                del request["year"]

        # Rethink if this is a good approach
        if "month" in new_date_request or "year" in new_date_request:

            if "date" in request or "time" in request:
                raise DQCInconsistentDateUpdateRequestedError(
                    new_date_request,
                    f"Cannot overwrite keys {new_date_request} for a "
                    f"request that contains 'date' and 'time' keys. "
                    f"Original request: {request}."
                )

            if "month" in new_date_request:
                request["month"] = new_date_request["month"]

            if "year" in new_date_request:
                request["year"] = new_date_request["year"]

            if "date" in request:
                del request["date"]

            if "time" in request:
                del request["time"]

        return request

    def convert_to_steps(
            self, request: T.Dict[str, T.Any]
            ) -> T.Dict[str, T.Any]:
        """
        Convert request in 'date format' to 'step format'.

        If start date is not provided an error is rasied.

        Arguments
        ---------
        request: Dict
            Request in date format to be converted to step format.
        
        Returns
        -------
        Dict
            Request converted to step format.
        """
        if self.start_date is None:
            raise DQCMissingStartDateError(
                "Missing start date. Request cannot be converted to "
                "step format."
                )
        request = convert_to_step_format(
            request, start_date=self.start_date, start_time=self.start_time
            )
        return request

    def get_message_string(
            self, msgid: int, request: T.Dict[str, T.Any]
            ) -> str:
        """
        Get string representation MARS request.

        String representation contains all the MARS keys of a given
        GRIB message.

        Arguments
        ---------
        msgid: int
            ecCodes handle for the ginve GRIB message.
        request: Dict
            MAR request used to retrieve the GRIB message.
        """
        return str({key: ecc.codes_get(msgid, key) for key in request})

    @staticmethod
    def get_spatial_consistency_keys(
            profile: T.Dict[str, T.Any]
            ) -> T.Dict[str, T.Any]:
        """
        Get the set of key, value pairs to check Spatial Consistency.

        The set of key, value pairs will depend on the variable,
        run resolution, output resolution, output grid...

        Different set of keys for different grids are defined in
        gsv/dqc/profiles/grids.

        Arguments
        ---------
        profile: Dict
            Data profile defining data to check.

        Returns
        -------
        Dict
            Dictionary with ecCodes keys to check and its reference
            values.
        """
        grid = profile["grid"]
        model = profile["mars-keys"]["model"]
        levtype = profile["mars-keys"]["levtype"]

        grid_root_path = (
            Path(inspect.getfile(DQCWrapper)).parent / "profiles" / "grids"
        )
        grid_mapping_path = (
            Path(inspect.getfile(DQCWrapper)).parent / "profiles"/ "config" /
            "grid_mapping.yaml"
        )
        with open(grid_mapping_path, 'r') as f:
            grid_mapping = yaml.safe_load(f)

        if grid == "native-high" or grid == "native-standard":
            if levtype in {"sfc", "pl", "sol", "hl"}:
                native_grid = f"{model.lower()}-atmos"
            elif levtype in {"o2d", "o3d"}:
                native_grid = f"{model.lower()}-ocean"
            else:
                raise Exception(f"Levtype {levtype} not recognized")  # TOFIX: Exception not checked

            grid_profile = (
                grid_root_path / grid_mapping[grid][native_grid]
                ).with_suffix(".yaml")

        else:
            grid_profile = (
                grid_root_path / grid_mapping[grid]
                ).with_suffix(".yaml")

        with open(grid_profile, 'r') as f:
            spatial_consistency_keys = yaml.safe_load(f)

        return spatial_consistency_keys

    @classmethod
    def read_variable_database(cls, user_db_path=None) -> T.Dict[str, T.Any]:
        """
        Read variable database with physical plausibility data.

        Data variable database can be found at
        gsv/dqc/profiles/conf/variables.

        Returns
        -------
        Dict
            Variable database loaded into a dictionary.
        """
        default_variable_database_path = Path(__file__).parent / "profiles/config/variables.yaml"
        default_db = cls.load_yaml_file(default_variable_database_path)

        if user_db_path is not None:
            user_db = cls.load_yaml_file(user_db_path)
        else:
            user_db = {}

        return cls.update_variables_database(default_db, user_db)

    def get_updated_request(self, profile):
        """
        Docstrings
        """
        # Get and update Request
        request = deepcopy(profile["mars-keys"])
        request = self.update_expver(request)
        request = self.update_date(request)  # Updates date, time, month and year
        request["model"] = self.model
        request["experiment"] = self.experiment
        request["activity"] = self.activity
        request["realization"] = self.realization

        if self.generation is not None:  # Only update generation if requested.
            request["generation"] = self.generation

        # Process request
        request = parse_request(request)

        # Transform request if needed
        if profile["date-format"] == "step":
            request = self.convert_to_steps(request)

        if profile["date-format"] == "month" and "date" in request:
            request = convert_date_to_monthly(request, strict=True)

        return request

    def run_message_checker(
            self,
            request,
            iterator,
            current_sample_length=None,
            message_start_index=1
            ):
        """Improve docstrings"""
        # Track number of checked messages
        self.n_checked_messages = 0
        total_messages = self.expected_n_checked_messages

        # Iterate over messages and run checkers
        # Start index from 1 to match number of checked messages
        for i, msg in enumerate(iterator, message_start_index):

            if current_sample_length is not None:
                if i > current_sample_length:
                    break

            self.logger.debug(
                f"Checking message {i}/{total_messages}")
            msgid = ecc.codes_new_from_message(msg)
            msg_str = self.get_message_string(msgid, request)

            # Run Standard Compliance Checker
            if self._check_standard_compliance:
                checker = StandardComplianceChecker(
                    msgid, self.logger)
                checker.run()

                if checker.status == 0:
                    self.logger.debug(
                        f"Message {i}/{total_messages}: "
                        "Standard Compliance Checker passed"
                    )

                else:
                    self.profile_status += checker.status * checker.CHECKER_CODE
                    self.any_failed = True
                    self.logger.error(
                        f"FAILED Standard Compliance checker "
                        f"for profile {self.profile_name}. {checker.err_msg}"
                    )

                    if self.halt_mode == "always":
                        raise DQCStandardComplianceError(checker.err_msg)

            # Run Spatial Consistency Checker
            if self._check_spatial_consistency:
                spatial_consistency_keys = self.get_spatial_consistency_keys(self.profile)  # TODO: exception for grid missing in profile
                checker = SpatialConsistencyChecker(
                    msgid, spatial_consistency_keys, self.logger
                )
                checker.run()

                if checker.status == 0:
                    self.logger.debug(
                        f"Message {i}/{total_messages}: "
                        "Spatial Consistency Checker passed")

                else:
                    self.profile_status += checker.status * checker.CHECKER_CODE
                    self.any_failed = True
                    self.logger.error(
                        f"FAILED Spatial Consistency Checker "
                        f"for profile {self.profile_name}. {checker.err_msg}"
                    )

                    if self.halt_mode == "always":
                        raise DQCSpatialConsistencyError(checker.err_msg)

            # Run Spatial Completeness Checker
            if self._check_spatial_completeness:
                checker = SpatialCompletenessChecker(msgid, self.logger)
                checker.run()

                if checker.status == 0:
                    self.logger.debug(
                        f"Message {i}/{total_messages}: "
                        "Spatial Completeness Checker passed"
                    )

                else:
                    self.profile_status += checker.status * checker.CHECKER_CODE
                    self.any_failed = True
                    self.logger.error(
                        f"FAILED Spatial Completeness Checker "
                        f"for profile {self.profile_name}. {checker.err_msg}"
                    )

                    if self.halt_mode == "always":
                        raise DQCSpatialCompletenessError(checker.err_msg)

            # Run Physical Plausibility Checker
            if self._check_physical_plausibility:
                checker = PhysicalPlausibilityChecker(
                    msgid, self.logger, self.variable_db
                )
                checker.run()

                if checker.status == 0:
                    self.logger.debug(
                        f"Message {i}/{total_messages}: "
                        "Physical Plausibility Checker passed"
                    )

                else:
                    self.profile_status += checker.status * checker.CHECKER_CODE
                    self.any_failed = True
                    self.logger.error(
                        f"FAILED Physical Plausibility Checker "
                        f"for profile {self.profile_name}. {checker.err_msg}"
                    )

                    if self.halt_mode == "always":
                        raise DQCPhysicalPlausibilityError(checker.err_msg)

            # Release message from memory
            ecc.codes_release(msgid)

            # Update number of checked messages
            self.n_checked_messages = i

    def run_checks_one_by_one(self, request):
        request_list = pick_random_requests(request, self.current_sample_length)

        n_checked_messages = 0
        for request in request_list:
            self.run_checks_multiple_field_request(
                request=request, message_start_index=n_checked_messages+1
            )
            n_checked_messages += 1

        # Overwritte message counter
        self.n_checked_messages = n_checked_messages

    def run_checks_multiple_field_request(self, request, message_start_index=1):
        # Retrieve data with GSV Interface
        gsv = GSVRetriever(logging_level=self.logging_level)
        datareader = gsv._retrieve(request)

        if self.use_stream_iterator:
            iterator = StreamMessageIterator(datareader)
        else:
            iterator = MessageIterator(datareader)

        self.run_message_checker(
            request=request,
            iterator=iterator,
            current_sample_length=self.current_sample_length,
            message_start_index=message_start_index
        )


    def run_dqc(self):
        """
        Run the dqc wrapper with the parameters defined at __init__.
        """
        # File header
        self.logger.info(f"Running DQC with GSV version {gsv_version}")
        self.logger.info(f"Using profiles in {self.profile_path}")

        for profile in self.profiles:
            # Set profile status to zero (no errors)
            self.profile = profile
            self.profile_name = profile['file'].name
            self.profile_status = 0

            # Log start of checking
            self.logger.info(f"Checking profile {profile['file']}")

            # Parse FDB5_CONFIG_FILE from model
            if self.fdb5_config_file is not None:
                os.environ["FDB5_CONFIG_FILE"] = self.fdb5_config_file

            # Get and update Request
            try:
                request = self.get_updated_request(profile)
            except DateNotConvertableToMonthlyError as e:
                if not self.allow_submonthly_chunks:  # If submonthly chunks not allowed, raise error
                    raise(e)

                # If submonthly chunks allowed, skip this profile
                self.profile_status = -1
                self.logger.warning(
                    f"WARNING: {e}."
                )
                self.logger.warning(
                    f"Checker skipped with profile: {profile['file']}. Cannot check monthly profiles with submonthly chunks."
                )
                continue

            # Split request for processor
            key_length = {k: count_combinations(request, [k]) for k in request}
            parallel_key = max(key_length, key=key_length.get)
            request = subsample_request(request, parallel_key, self.n_proc, self.proc_id)
            if not request[parallel_key]:  # Check if this is even possible
                continue

            # Update other extra keys  # TODO: remove this and force updating through API
            if self.additional_keys  is not None:
                request.update(self.additional_keys)

            # Get expected number of messages
            self.n_messages = count_combinations(request, GSVRetriever.MARS_KEYS)

            # Check sample length is not bigger than expected n _messages
            self.current_sample_length = self.sample_length
            if self.current_sample_length is not None and self.current_sample_length > self.n_messages:
                self.logger.warning(
                    f"WARNING: A sample length of {self.current_sample_length} "
                    f"was requested but only {self.n_messages} are expected "
                    f"for request {request}. All messages will be "
                    "checked."
                )
                self.current_sample_length = None

            # Check data available
            data_available_checker = DataAvailableChecker(
                request, self.logging_level
            )
            data_available_checker.run()

            if data_available_checker.status != 0:
                self.profile_status = 1
                self.any_failed = True
                self.logger.error(
                    f"FAILED Data Availability Checker "
                    f"for profile {self.profile_name}. {data_available_checker.err_msg}"
                )

                if self.halt_mode == "always":
                    raise DQCDataAvailableError(data_available_checker.err_msg)  # TOFIX: Exception not checked

            else:  # Report data available checker passed
                self.logger.info(
                    f"Found all requested {self.n_messages} messages in FDB."
                    )

            skip_other_checks = not any([
                self._check_standard_compliance,
                self._check_spatial_completeness,
                self._check_spatial_consistency,
                self._check_physical_plausibility
            ])

            if skip_other_checks:
                self.logger.debug("Skipping all the checks without reading")

            else:

                # Check if subsample is needed
                if self.current_sample_length is not None:
                    self.logger.info(
                        f"Checking a sample of {self.current_sample_length} "
                        f"messages out of total {self.n_messages}."
                    )
                    self.expected_n_checked_messages = self.current_sample_length
                    self.run_checks_one_by_one(request)

                else:
                    self.expected_n_checked_messages = self.n_messages
                    self.run_checks_multiple_field_request(request)

                # Ensure all listed messages were read and checked
                if data_available_checker.status == 0:
                    if self.n_checked_messages != self.expected_n_checked_messages:
                        if self.current_sample_length is None:
                            err_msg = (
                                f"{self.n_messages} "
                                f"were detected by fdb-list but only "
                                f"{self.n_checked_messages} were retrieved "
                                f"by fdb-read."
                            )
                        else:
                            err_msg = (
                                f"A sample length of "
                                f"{self.current_sample_length} messages was "
                                f"requested for checking but only "
                                f"{self.n_checked_messages} were read with "
                                f"fdb-read. Some messages detected by "
                                f"fdb-list could not be retrieved by fdb-read."
                            )

                        self.logger.error(
                            f"FAILED Data Availability Checker "
                            f"for profile {self.profile_name}. {err_msg}"
                        )
                        self.profile_status = 1
                        self.any_failed = True

                        if self.halt_mode == "always":
                            raise DQCDataAvailableError(err_msg)  # TOFIX: Exception not checked

            if self.profile_status == 0:
                self.logger.info(
                    f"Checker passed with profile: {profile['file']} (split key: {parallel_key}). Request: {request}"
                )
            else:
                self.logger.error(
                    f"Checker failed with profile: {profile['file']} (split key: {parallel_key}). Request: {request}"
                )

        self.report_general_result()

    def report_general_result(self):
        """
        Report general result of the DQC run.
        """
        if self.any_failed:
            if self.halt_mode == "end":
                err_msg = (
                    "Checker stopped after checking all GRIB messages. "
                    "Check ERROR messages in logs for more detailed info."
                )
                self.logger.error(err_msg)
                raise DQCFailedError(err_msg)