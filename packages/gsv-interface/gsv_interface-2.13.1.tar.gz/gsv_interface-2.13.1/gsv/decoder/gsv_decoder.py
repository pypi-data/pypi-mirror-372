from typing import BinaryIO, Dict, List, Optional, Union

import numpy as np
import xarray as xr

from gsv.decoder.grid_decoder import decode_grid
from gsv.decoder.level_decoder import decode_level_reader
from gsv.decoder.message_decoder import decode_message
from gsv.exceptions import MissingDatasetError, NoMessageDecodedError
from gsv.grids import Grid, LonLatGrid
from gsv.interpolate.gsv_interpolator import GSVInterpolator
from gsv.iterator import MessageIterator, StreamMessageIterator
from gsv.logger import get_logger
from gsv.requests.checker import check_requested_interpolation
from gsv.requests.processor import _render_grid


class GSVDecoder:
    """
    Class to manage the decoding of GRIB messages into Xarray datasets.

    Data is read from file containing a continuous stream of raw
    GRIB data.

    A gsv iterator object is used to iterate over GRIB messages.

    Messages are decoded one by one into xarray DataArrays and added
    to the data_variables dictionary.

    At the end, all the DataArrays in data_variables are merged into
    a single dataset.

    Additinally, interpolation to a regular LatLon grid can be
    requested to the decoder. Interpolation logic is delegated to
    GSVInterpolator.

    Attributes
    ----------
    logger : logging.Logger
        Logger object to manage messages.
    iterator_class : gsv.iterator.Iterator
        WARNING ABC Iterator does not exist. Create it for type hint purposes.
    input_grid: gsv.grids.Grid
        Original grid in which the data is written.
        This attribute is initialize to None, and is updated when the
        first GRIB message is being decoded.
    level_reader : WARNING what kind of object is this?
    data_variables: Dict[]
        WARNING Describe the strucuture of the dictionary
    interpolator : gsv.interpolate.GSVInterpolator
        Object to manage interpolation to LatLonGrid
    """

    def __init__(
        self,
        logging_level="INFO",
        use_stream_iterator=False,
        grid: Optional[Union[str, List[float]]]=None,
        method: Optional[str]=None
    ):
        """
        Constructor for GSVDecoder class.

        Arguments
        ---------
        logging_level : str
            Set level for log messages. Options are: DEBUG, INFO,
            WARNING, ERROR and CRITICAL. Default is INFO.
        use_stream_iterator : bool
            If True, gsv.iterator.StreamMessageIterator object is used
            to read the GRIB messages. If False,
            gsv.iterator.MessageIterator object is used instead.
            Reading from the databridge requires this flag being
            True. Default is False.
        grid : Optional[List[float] or str]
            Specification of target grid in [degrees_lon, degrees_lat].
            Can be also implicitly specified as a string representing
            'degrees_lon/degrees_lat'.
            If set to None, no interpolation is requestd.
        method : Optional[str]
            Interpolation method to use if interpoaltion is requested.
            Valid options are 'nn' and 'con'.
            If set to None, but interpolation is requested
            (by asking a valid grid), the  GSV Interpolator will
            default it no 'nn'.
        """
        self.logger = get_logger(
            logger_name=__name__, logging_level=logging_level
        )
        self.iterator_class = self.get_iterator_class(use_stream_iterator)
        self.input_grid = None
        self.level_reader = None
        self.data_variables = {}

        # Validate grid and method
        self.validate_grid_and_method(grid, method)
        self.set_interpolator(grid, method)

    @staticmethod
    def get_iterator_class(use_stream_iterator: bool):
        """
        WARNING: Missing ABC GSV Iterator for type hints

        Get the selected GSV iterator class.

        If use_stream_iterator is True, StreamMessageIterator is used
        to read the binary stream of GRIB messages. Otherwise,
        MessageIterator is used.
        
        For reading from the databridge with FDB, StreamMessageIterator
        is needed.

        Arguments
        ---------
        use_stream_iterator : bool
            If True, StreamMessageIterator is used.
            If False, MessageIterator is used.

        Returns
        -------
        gsv.iterator.Iterator
            gsv Iterator object to manage the reading of the continuous
            stream of GRIB messages.
        """
        if use_stream_iterator:
            return StreamMessageIterator
        else:
            return MessageIterator

    @staticmethod
    def validate_grid_and_method(
        grid: Optional[Union[List[str], str]], method: Optional[str]
    ):
        """
        Check compatibility of requested grid and method keys.

        GSV requests checker is used to check validity of these
        two keys.

        Arguments
        ---------
        grid : Optional[ List[float] or str]
            Specification of target grid in [degrees_lon, degrees_lat].
            Can be also implicitly specified as a string representing
            'degrees_lon/degrees_lat'.
            If set to None, no interpolation is requestd.
        method : Optional[str]
            Interpolation method to use if interpoaltion is requested.
            Valid options are 'nn' and 'con'.
            If set to None, but interpoaltion is requested, no error
            is raised, since the interpolator will assume 'nn' by
            default.
        
        Raises
        ------
        InvalidTargetGridError
            When grid is not a valid specification of target grid.
            Validation of grid key is made in gsv.requests.checker.
        InvalidInterpolationMethodError
            When method is not a valid interpolation method.
            Validation of method key is made in gsv.requests.checker.
        UnexpectedKeyError
            When grid is None but method is a valid key.
        """
        # Convert to standard request format to use requests module
        request = {}
        if grid is not None:
            request["grid"] = grid
        if method is not None:
            request["method"] = method

        if request:  # Skip check if request is empty (no interpolation)
            check_requested_interpolation(request)

    @staticmethod
    def get_output_grid(grid: List[float]) -> LonLatGrid:
        """
        Get a LonLatGrid object from the grid key.

        Key must be already rendered to a list of two float
        numbers, describing the angular separation in degrees along
        the longitude and latitude lines respectively.

        Arguments
        ---------
        grid : List[float]
            Specification of target regular LonLat grid as a list of
            two float numbers, representing angular separation in
            degrees along the longitude and latitude lines respectively.
        
        Returns
        -------
        LonLatGrid
            LonLatGrid object describing the target grid.
        """
        deg_lon, deg_lat = grid
        ni = int(360.0 / deg_lon)
        nj = int(180.0 / deg_lat)
        grid = LonLatGrid(ni, nj)

        return LonLatGrid(ni, nj)

    def set_interpolator(
        self, grid: Optional[Union[List[str], str]], method: Optional[str]
    ):
        """
        Set GSV Interpolator object if interolation is requested.

        If grid is None, interpolator attribute is set to None.

        If grid is not None,  interpolator is set to a GSVInterpolator
        object that takes care of the interpolation features.

        Arguments
        ---------
        grid : Optional[ List[float] or str] 
            Specification of target grid in [degrees_lon, degrees_lat].
            Can be also implicitly specified as a string representing
            'degrees_lon/degrees_lat'.
            If set to None, no interpolation is requestd.
        method : Optional[str]
            Interpolation method to use if interpoaltion is requested.
            Valid options are 'nn' and 'con'.
            If set to None, but interpolation is requested, it will be
            set to 'nn'.

        Returns
        -------
        gsv.interpolator.GSVInterpolator
            Object to manage interpolation, if requested.
        """
        if grid is not None:
            output_grid = self.get_output_grid(_render_grid(grid))
            self.logger.debug(f"Output grid set to {output_grid.grid_id}")
            interpolation_method = method or "nn"
            self.logger.debug(
                f"Interpolation method set to {interpolation_method}"
            )
            self.interpolator = GSVInterpolator(
                output_grid=output_grid,
                method=interpolation_method,
                logger=self.logger,
                )

        else:
            self.interpolator = None

    @property
    def output_grid(self) -> Grid:
        """
        Accessor for real output_grid of resulting dataset.

        If interpoaltion is requested, output_grid will be equal to the
        output_grid defined in the interpolator.

        If interpolation is not requestedm output_grid will be equal to
        input_grid.

        Returns
        -------
        Grid
            Object representing the grid of the resulting dataset.
        """
        if self.interpolator is not None:
            return self.interpolator.output_grid
        else:
            return self.input_grid

    @property
    def interpolation_method(self) -> Optional[str]:
        """
        Accessor for the interpoalation method.

        If interpolation is requested, it will return the
        interpolation_method defined in the interpolator.

        If interpolation is not requested, it will return None.

        Returns
        -------
        str or None
            Interpolation method if requested.
        """
        if self.interpolator is not None:
            return self.interpolator.interpolation_method
        else:
            return None

    def _add_array(self, da: xr.DataArray):
        """
        Add a xarray DataArray to data_variables dictionary.

        Arguments
        ---------
        da : xr.DataArray
            xarray DataArray to be included in data_variables.
        """
        name = da.name
        level = da.level.values[0] if "level" in da.dims else "sfc"

        if name not in self.data_variables:
            self.data_variables[name] = {}

        level_dict = self.data_variables[name]

        if level not in level_dict:
            level_dict[level] = []

        level_dict[level].append(da)

    def _construct_dataset(
        self,
        input_grid: Grid,
        data_variables: Dict,
        interpolation_method: Optional[str]=None,
        ) -> xr.Dataset:
        """
        Merge all the DataArrays in data_variables in a single Dataset.

        WARNING: check if first four lines can be simplified in a single line

        Arguments
        ---------
        input_grid : Grid
            Object representing the original grid of the data.
        data_variables : Dict
            WARNING
        interpolation_method : str or None
            Interpolation method to use if interpoaltion is requested.

        Returns
        -------
        xr.Dataset
            Resulting xarray Dataset with all the decoded data.
        """
        # Set Dataset with output_grid coordinates
        if interpolation_method is None:
            ds = input_grid.create_empty_dataset()
        else:
            ds = xr.Dataset()

        for name, level_dict in data_variables.items():

            for level, timesteps in level_dict.items():
                level_dict[level] = xr.concat(timesteps, dim="time")

            if "sfc" in level_dict:
                da = level_dict["sfc"]
            else:
                da = xr.concat(list(level_dict.values()), dim="level")

            ds[name] = da

        return ds

    def decode_messages(self, datareader: BinaryIO) -> xr.Dataset:
        """
        Decode file with GRIB message into a xarray Dataset.

        GSV Iterator is used to read the GRIB messages one by one.

        If requested, GSVInterpolator can be used to interpoalte
        the data into a regular LonLat file.

        Arguments
        ---------
        datareader : BinaryIO
            A file object containing a stream of GRIB messages.

        Returns
        -------
        xr.Dataset
            Resulting xarray Dataset with all the decoded data.

        Raises
        ------
        MissingDatasetError
            When datareader is None.
        NoMessageDecodedError
            When the datareader object does not contain any
            GRIB message. This is detected because, as the iterator
            loop does not do any iteration, the input_grid attribute
            is not updated and therefore keeps its initial None
            value.
        """
        if datareader is None:
            raise MissingDatasetError(datareader)

        # Add exception if datareader is not readable
        iterator = self.iterator_class(datareader)
        self.logger.debug(f"Reading GRIB data with {self.iterator_class}")

        for message in iterator:
            # Decode grid and levels if needed
            if self.input_grid is None:
                self.input_grid = decode_grid(message)
                self.logger.debug(
                    f"Correctly decoded source grid: {self.input_grid}"
                )

            if self.level_reader is None:
                self.level_reader = decode_level_reader(message)

            da = decode_message(message, self.input_grid, self.level_reader)

            if self.interpolator is not None:
                self.interpolator.set_input_grid(self.input_grid)
                da = self.interpolator.interpolate(da)

            self._add_array(da)

            # Report result
            level = da.level.values[0] if "level" in da.dims else "sfc"
            timestamp = np.datetime_as_string(da.time.values[0], unit='s')
            self.logger.debug(
                f"Correctly decoded {da.name: <6} on level "
                f"{level: <6} at {timestamp}"
            )

        if self.input_grid is None:
            raise NoMessageDecodedError()

        return self._construct_dataset(
            self.input_grid, self.data_variables, self.interpolation_method
        )
