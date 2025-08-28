from typing import Dict, Any, Optional, Union, BinaryIO

import xarray as xr

from gsv.logger import get_logger
from gsv.engines import FDBEngine, PolytopeEngine, Engine
from gsv.grids import Grid
from gsv.derived.derived import get_derived_variables_components, compute_derived_variables
from gsv.requests.parser import parse_request
from gsv.requests.utils import filter_request, count_combinations
from gsv.decoder import GSVDecoder

from gsv.area import RectangularAreaSelector
from gsv.fixer import Fixer
from gsv.exceptions import (
    MissingGSVMessageError,
    MissingKeyError,
    NoMessageDecodedError,
    InvalidEngineError,
    InvalidOutputTypeError,
)


class GSVRetriever:
    """
    Class to manage retrieval of GSV data.

    This class collects the basic functionalities of
    GSV interface for reading, decoding, and interpolating
    GRIB data stored in FDB.

    Attributes
    ----------
    logger : logging.Logger
        Logger object to manage messages.
    engine : gsv.engines.Engine
        Engine object with the specific methods
        for retrieving data with different backends (FDB, Polytope).
    request : dict[str, Any]
        Dictionary with all the keys for requesting data.
    decoder : gsv.decoder.GSVDecoder
        Object that manages the decoding of GRIB messages into
        xarray objects.
    datareader : BinaryIO
        File object containing a continuous stream of retrieved
        raw GRIB messages.
    area: List[float]
        Specification of requested rectangular area in the following
        format: [N, W, S, E]
    ds : xr.Dataset
        Resulting dataset returned by the decoder.

    Legacy:
    input_grid : gsv.grids.Grid
        Grid object representing input grid
        (source grid of data in GSV).
    output_grid : gsv.grids.Grid
        Grid object representing output grid
        (target grid if interpolation is requested).
        If no interpolation is requested, it defaults to input_grid.
    interpolation_method : str
        Descriptor of interpolation method used if interpolation
        is requested. Options are 'nn' (nearest neighbor) and
        'con' (first order conservative).
        If no interpolation is requested, it defaults to None.
    weights : dict[str, xr.Dataset]
        Dictionary to store weights datasets used during interpolation
        process.
    data_variables : dict[str, dict[str, xr.DataArray]]
        Nested dictionary to store all the decoded 2D DataArrays.
        Top level keys are variable names. Second level keys
        are vertical levels. Ex. {"sst": {"1000": array_1,
        "500": array_2}}.
    """

    MARS_KEYS = [
        "date",
        "time",
        "levtype",
        "levelist",
        "step",
        "param",
        "class",
        "stream",
        "domain",
        "type",
        "expver",
        "anoffset",
        "dataset",
        "activity",
        "experiment",
        "generation",
        "model",
        "realization",
        "resolution",
        "frequency",
        "direction",
        "year",
        "month",
    ]

    def __init__(self, logging_level="INFO", engine="fdb", source=None):
        """
        Constructor for GSVRetriever class.

        Arguments
        ---------
        logging_level : str
            Set level for log messages. Options are: DEBUG, INFO,
            WARNING, ERROR and CRITICAL. Default is INFO.
        engine: str
            Set engine for data retrieval. Supported options are
            'fdb' and 'polytope'. Default is 'fdb'.
        """
        self.logger = get_logger(
            logger_name=__name__, logging_level=logging_level
        )
        self.engine = self.get_engine(engine, source)
        self.request = None
        self.decoder = None
        self.datareader = None
        self.area = None
        self.ds = None

    def __repr__(self):
        _repr = (
            f"GSVRetriever:\n"
            f"  logger: {self.logger}\n"
            f"  engine: {self.engine}"
        )
        return _repr

    def _get_output_area(self, request: Dict[str, Any]):
        """
        Get the output area region from the request.

        Arguments
        ---------
        request : dict
            Data request in Python dict format.
        """
        if "area" in request:
            self.area = RectangularAreaSelector(request["area"])
            self.logger.debug(f"Output data will be cropped to {self.area}")

    @staticmethod
    def get_engine(engine_name: str, source: Optional[str]=None) -> Engine:
        """
        WARNING: should this method be moved to engine?
        Get engine object from user specification.

        Arguments
        ---------
        engine_name : str
            User specification of selected retrieval engine.
            Valid options are 'fdb' and 'polytope'.
        source : Optional[str]
            Optional. Only for the Polytope engine.
            Sets wether the data must be retrieved from the
            Lumi databridge or from the MN5 databridge.
            If None, the default source (Lumi) is used.
            If provided with fdb engine, it will raise an error.

        Returns
        -------
        gsv.engines.Engine
            Engine object with the specific methods
            or retrieving data with different backends (FDB, Polytope).

        Raises
        ------
        InvalidEngineError
            If engine_name is neither 'fdb' nor 'polytope'.
        """
        if engine_name.lower() not in {"fdb", "polytope"}:
            raise InvalidEngineError(engine_name)

        if engine_name.lower() == "fdb":
            if source is not None:
                raise InvalidEngineError(
                    "FDB engine does not support source argument. "
                    "Please use Polytope engine instead."
                )
            return FDBEngine()

        if engine_name.lower() == "polytope":
            machine = source or "lumi"
            return PolytopeEngine(machine.lower())

    def _list(self, request: Dict[str, Any]):
        """
        WARNING: This function should be deprecated, since it is only
        supported in FDB engine.

        Call fdb-list to get a list of FDB messages matching request.

        Arguments
        ---------
        request: dict
            Dictionary with MARS keys to request.

        Returns
        -------
        pyfdb.ListIterator
            Iterator that runs over all the messages that match the
            given request, without reading the message content.
        """
        mars_request = filter_request(request, self.MARS_KEYS)
        return self.engine.list_(mars_request)

    def _retrieve(self, request: Dict[str, Any]) -> BinaryIO:
        """
        Retrieve the requested data with the selected engine.

        Arguments
        ---------
        request : dict
            Dictionary with MARS keys to requests. Extra keys
            not included in MARS_KEYS are ignored.

        Returns
        -------
        BinaryIO
            File object containing a continuous stream of retrieved
            raw GRIB messages.
        """
        mars_request = filter_request(request, self.MARS_KEYS)
        return self.engine.retrieve(mars_request)

    def _decode_messages(
        self,
        grid: Optional[Grid] = None,
        method: Optional[str] = None,
        use_stream_iterator=False,
    ) -> xr.Dataset:
        """
        Decode the retrieved GRIB messages into a xarray Dataset.

        Interpolation to a regular LatLon grid can be requested
        in the decoding process.

        Arguments
        ---------
        grid : Optional[Grid]
            Target regular LatLon grid if interpolation is requsted.
            If no interpolation is requested it is set to None.
            Default is None.
        method : Optional[str]
            Interpolation method to be used ifinterpolation is
            requested. If no interpolation is requested it is set to
            None. Default is None.
        use_stream_iterator : bool
            If True, gsv.iterator.StreamMessageIterator object is used
            to read the GRIB messages. If False,
            gsv.iterator.MessageIterator object is used instead.
            Reading from the databridge requires this flag being
            True. Default is False.

        Returns
        -------
        xr.Dataset
            Requested data in xarray Dataset format.
        """
        self.decoder = GSVDecoder(
            use_stream_iterator=use_stream_iterator,
            logging_level=self.logger.level,
            grid=grid,
            method=method,
        )
        try:
            return self.decoder.decode_messages(self.datareader)
        except NoMessageDecodedError:
            raise MissingGSVMessageError(self.request)
        finally:
            self.engine.close()

    def check_messages_in_fdb(
            self,
            request,
            process_request=True,
            process_derived_variables=False,
            derived_variables_definitions=None,

            ):
        """
        WARNING: should this method be oved to the FDB engine?
        Keep in mind that this is part of the Public API, and is
        used by the Data Notifier in the Workflow.

        Check that all requested messages are available in FDB.

        For performance improvement, only the number of expected
        and available messages messages is checked. If these two
        numbers do not match, an error is raised.

        Arguments
        ---------
        request : dict
            Request to check
        process_request : bool
            If True, request checker and processer are runned before
            checking messages in FDB. Default is True.

        Raises
        ------
        NotImplementedError
            When this method is called with a selected engine other
            thatn FDB.
        MissingGSVMessageError
            When at least one of the requested messages is not found
            in the FDB.
        MissingKeyError
            When some needed MARS keys are missing in the request.
        """
        # Block engines other than FDBEngine
        if not isinstance(self.engine, FDBEngine):
            raise NotImplementedError(
                f"Cannot check messages in FDB with engine: {self.engine}. "
                f"Checking of messages is only supported with engine: 'fdb'."
            )

        request = parse_request(request, process_request)
        request = filter_request(request, self.MARS_KEYS)

        # Process derived variables if requsted
        if process_derived_variables:
            request = get_derived_variables_components(
                request, derived_variables_definitions=derived_variables_definitions
            )

        # Catch missing messages in FDB
        n_expected_messages = count_combinations(request, self.MARS_KEYS)
        matching_messages = list(self._list(request))
        n_gsv_messages = len(matching_messages)

        if n_expected_messages != n_gsv_messages:
            raise MissingGSVMessageError(
                request,
                f"Some messages are not available in FDB and "
                "request cannot be fulfilled. "
                f"{n_expected_messages} were requested in request {request} "
                f"but only {n_gsv_messages} were found on FDB.",
            )

        # Catch requests being too unespecific
        mars_keys_fdb = set(matching_messages[0]["keys"])

        # Ad hoc fix for ICON o2d and sfc data reporting levelist as MARS key
        if (
            matching_messages[0]["keys"]["levtype"] == "o2d"
            and "levelist" in mars_keys_fdb
        ):
            mars_keys_fdb.remove("levelist")

        if (
            matching_messages[0]["keys"]["levtype"] == "sfc"
            and "levelist" in mars_keys_fdb
        ):
            mars_keys_fdb.remove("levelist")

        # Ad hoc fix for month and year in the clte data
        if matching_messages[0]["keys"]["stream"] == "clte":
            if "month" in mars_keys_fdb:
                mars_keys_fdb.remove("month")
            if "year" in mars_keys_fdb:
                mars_keys_fdb.remove("year")

        # Ad hoc additional fix for date and time in the clmn date
        if matching_messages[0]["keys"]["stream"] == "clmn":
            if "date" in mars_keys_fdb:
                mars_keys_fdb.remove("date")
            if "time" in mars_keys_fdb:
                mars_keys_fdb.remove("time")

        missing_mars_keys = mars_keys_fdb - set(request)

        for key in missing_mars_keys:
            if matching_messages[0]["keys"][key]:
                raise MissingKeyError(
                    key=key,
                    message=f"The following MARS keys are missing in the request: "
                    f"{missing_mars_keys}"
                )

        self.logger.debug(
            f"All requested {n_expected_messages} messages are available "
            f"in FDB."
        )

    def request_data(
        self,
        request: Union[Dict, str],
        check_messages_in_fdb=False,
        definitions=None,
        use_stream_iterator=False,
        output_type="xarray",
        output_filename="gsv_data.grb",
        process_derived_variables=True,
        derived_variables_definitions=None,
        report_valid_time=False,
        apply_fixer=False,
    ) -> Optional[xr.Dataset]:
        """
        Request GSV data.

        Data is retrieved using the selected gsv Engine at
        initialization.

        Data can be outputed as it is in GRIB format, or it can be
        decoded into xarray using the GSVDecoder.

        Data can be interpolated to a regular LatLon grid using the
        gsv interpolator. Supported interpolation methods are
        nearest neighbor and conservative.

        Arguments
        ---------
        request : dict or str
            Request for data to retrieve.
            Request can be passed in two ways: as a Python dict
            or as a path to a YAML file.
            If request is a str, a path to a YAML file is interpreted
            and the file will be read as a dict.
        check_messages_in_fdb : bool
            If True, messages are checked in FDB before trying
            data retrieval. Default is False.
            This can only be used with FDB engine.
        definitions : Optional[str]
            Optional. Path to YAML file with defintions of extra
            short names and its GRIB paramIds. Short names not in
            default list will be appended. Short names that are already
            in the default list will be overwritten by the user defined
            ones (be careful with this). If None, only short names on
            default list can be used. Only recommended for developres.
        use_stream_iterator : bool
            If True, gsv.iterator.StreamMessageIterator object is used
            to read the GRIB messages. If False,
            gsv.iterator.MessageIterator object is used instead.
            Reading from the databridge with FDB requires this flag
            being True. Default is False.
        output_type : str
            Output format of the retrieved data. Valid options are:
            'grib' and 'xarray'.
            If 'xarray' is selected, the retrieved data will be passed
            through the GSVDecoder to convert it into a xarray Dataset.
            If 'grib' is selected, the retrieved data will be directly
            dumped into a GRIB file. Postprocessing keys in request as
            'grid' or 'area' will be ignored in this case.
            Default is 'xarray'.
        output_filename : str
            Only used if output_type is 'grib'. Path of the resulting
            GRIB file. If not provided a default name of 'gsv_data.grb'
            will be used.
        process_derived_variables : bool
            If true, derived variables are substituted by their
            components before retrieving data and the requested
            variable is computed and returned. Default is True.
        derived_variables_definitions : Optional[str]
            Optional. Path to YAML file with definitions of derived
            variables. If None, only derived variables in default
            list are used. Default is None.
        report_valid_time : bool (deprecated)
            Optional. If True, resulting dataset will contain
            both `time` and `valid_time` as coordinates. If False,
            it will only contai `time` coordinate. Default is False.
            WARNING: `valid_time` coordinate can contain incorrect
            values if both instantaneous and accumulated/averaged
            variables are mixed in the same reuqest.
        apply_fixer : bool (deprecated)
            Optional. If True, data will be passed through a data fixer
            defined in module `fixer`. This ifxer is a temporary
            workaround to some encoding problems on the original GRIB
            fields that could not be fixed on time for production runs.
            Default is False.

        Returns
        -------
        Optional[xr.dataset]
            If output_type is 'xarray' a xarray Dataset will be
            returned containing the requested data. The dataset
            can be also accessed from self.ds.
            If output_type is 'grib' nothing will be returned.

        Raises
        ------
        InvalidOutputTypeError
            When an output_type other than 'xarray' or 'grib' is
            requested. Case is not taken into account.
        """
        if output_type.lower() not in {"xarray", "grib"}:
            raise InvalidOutputTypeError(output_type)

        # Clean previous requests
        if self.ds is not None:
            self.clear_data()

        # Report parsed definitions file
        if definitions is None:
            self.logger.debug(
                "No short_name definitions file specified. Default "
                "definitions will be used for interpreting short names."
            )
        else:
            self.logger.debug(
                f"File {definitions} specified for short name definitons. "
                "Default definitions will be updated with the content of "
                "this file."
            )

        # Check and process request
        self.request = parse_request(
            request, check_and_process=True, definitions=definitions
        )
        self.logger.debug(f"Checked and processed request: {self.request}")

        # Check if messages are in FDB
        if check_messages_in_fdb:
            self.check_messages_in_fdb(
                self.request,
                process_request=False,
                process_derived_variables=process_derived_variables,
                derived_variables_definitions=derived_variables_definitions,
            )

        # Retrieve data from FDB
        request = get_derived_variables_components(
            self.request, logger=self.logger, derived_variables_definitions=derived_variables_definitions
        ) if process_derived_variables else self.request

        self.datareader = self._retrieve(request)

        if output_type.lower() == "grib":
            self.engine.grib_dump(output_filename)
            return 0

        # Set up area selection if needed
        self._get_output_area(self.request)

        # Read and decode messages as xarray dataset
        self.ds = self._decode_messages(
            grid=self.request.get("grid"),
            method=self.request.get("method"),
            use_stream_iterator=use_stream_iterator,
        )

        # Compute variables if needed
        if process_derived_variables:
            self.ds = compute_derived_variables(
                self.request, self.ds, definitions=definitions, logger=self.logger,
                derived_variables_definitions=derived_variables_definitions
            )

        # Drop valid_time
        if not report_valid_time:
            if "valid_time" in self.ds.coords:
                self.ds = self.ds.drop("valid_time")

        else:
            self.logger.warning(
                "Valid_time coordinate can report incorrect values "
                "if instantaneous and accumulated/averaged variables "
                "are mixed in the same request."
            )

        # Crop if needed
        if self.area is not None:
            self.ds = self.area.select_area(self.ds)

        # Apply post-reading fixer if requested
        if apply_fixer:
            if "model" in self.request:  # For backwards comp. with old DGOV
                fixer = Fixer(self.request["model"])
                self.ds = fixer.apply(self.ds)

        return self.ds

    def clear_data(self):
        """
        Clear data of last request
        """
        self.request = None
        self.decoder = None
        self.datareader = None
        self.area = None
        self.ds = None
