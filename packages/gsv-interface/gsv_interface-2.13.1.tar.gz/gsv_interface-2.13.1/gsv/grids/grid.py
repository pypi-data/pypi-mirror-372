from abc import ABC, abstractmethod
from dataclasses import dataclass
import typing as T

import numpy as np
import xarray as xr


def requires_coordinates(method: T.Callable) -> T.Callable:
    """
    Decorator for methods that require grid coordinates
    to be already computed
    """
    def wrapper(grid, *args, **kwargs):
        if grid.longitudes is None:
            grid.compute_coordinates(*args, **kwargs)
        return method(grid, *args, **kwargs)
    return wrapper


@dataclass
class Grid(ABC):

    @property
    @abstractmethod
    def grid_id(self) -> str:
        """
        CDO grid identifier
        """

    @property
    @abstractmethod
    def npix(self) -> int:
        """
        Number of pixels
        """

    @property
    @abstractmethod
    def coords(self) -> T.Dict[str, xr.DataArray]:
        """
        Dictionary mapping coordinate names and DataArrays
        """

    @property
    @abstractmethod
    def full_coords(self) -> T.Dict[str, xr.DataArray]:
        """
        Dictionary mapping coordinate names and DataArrays
        """

    @abstractmethod
    def compute_coordinates(self) -> None:
        """
        Compute the coordinates of the grid using the
        grid-defining instance variables
        """

    @abstractmethod
    def create_dummy_variable(self) -> xr.Dataset:
        """
        Create a dataset with a random valued data variable
        that fits into the grid.

        This is needed in order to generate the interpolation weights.
        """

    @abstractmethod
    def read_values(self, msgid: int) -> np.ndarray:
        """
        Read the data values from the ecCodes handle msgid
        and reshape to match the grid shape.
        """

    @abstractmethod
    def reshape_for_xarray(self, values: np.ndarray) -> np.ndarray:
        """
        Reshape the given values to match the shape
        expected by xarray
        """

    @requires_coordinates
    def create_empty_dataset(self):
        """
        Create a xarray dataset with no data variables and
        the coordinates for the horizontal dimensions
        """
        return xr.Dataset(data_vars=None, coords=self.full_coords, attrs={})
