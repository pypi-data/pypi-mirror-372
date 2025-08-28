from dataclasses import dataclass
import typing as T

import numpy as np
import eccodes as ecc
import xarray as xr

from gsv.exceptions import InvalidShapeError
from gsv.grids.grid import Grid, requires_coordinates


@dataclass
class LonLatGrid(Grid):
    """
    A class to represent a regular LonLat Grid

    Attributes
    ----------
    ni : int
        Number of grid points along x-direction
    nj : int
        Number of grid points along y-direction
    longitudes : np.ndarray
        1-D array representing the x-coordinate values
    latitudes : np.ndarray
        1-D array representing the y-coordinate values
    dims : List[str]
        Set of dimensions that a xarray.Dataset with
        this gridshould have
    gridtype : str
        Indicator for type of grid
    ATTRIBUTES : List[str]
        List of GRIB keys specific to this grid
    grid_id : str
        CDO grid identifier
    npix : int
        Number of pixels of grid
    """

    ni: int
    nj: int
    longitudes = None
    latitudes = None
    dims: T.ClassVar[T.List[str]] = ["time", "level", "lat", "lon"]
    grid_type: T.ClassVar[str] = "regular_ll"
    ATTRIBUTES: T.ClassVar[T.List[str]] = [
        "Nx",
        "iDirectionIncrementInDegrees",
        "iScansNegatively",
        "longitudeOfFirstGridPointInDegrees",
        "longitudeOfLastGridPointInDegrees",
        "Ny",
        "jDirectionIncrementInDegrees",
        "jPointsAreConsecutive",
        "jScansPositively",
        "latitudeOfFirstGridPointInDegrees",
        "latitudeOfLastGridPointInDegrees",
    ]

    @property
    def grid_id(self) -> str:
        """
        CDO grid identifier: r<Ni>x<Nj>
        """
        return f"r{self.ni}x{self.nj}"

    @property
    def npix(self) -> int:
        """
        Number of pixels
        """
        return self.ni * self.nj

    @property
    @requires_coordinates
    def coords(self) -> T.Dict[str, xr.DataArray]:
        """
        Dictionary mapping coordinate names and DataArrays.
        For LonLat: lon, lat.
        """
        lon =  xr.DataArray(
            data=self.longitudes, dims={'lon': self.ni},
            attrs={
                "standard_name": "longitude",
                "units": "degrees",
            },
            name="lon"
        )

        lat =  xr.DataArray(
            data=self.latitudes, dims={'lat': self.nj},
            attrs={
                "standard_name": "latitude",
                "units": "degrees"
            },
            name="lat"
        )

        return {
            "lon": lon,
            "lat": lat
        }

    @property
    @requires_coordinates
    def full_coords(self):
        """
        Dictionary mapping cell coordinate and cell corner coordinate
        names to their corresponding DataArrays.
        """
        return self.coords

    def compute_coordinates(self) -> None:
        """
        Compute the coordinates of the grid using the
        grid-defining instance variables.
        For LonLat: lon, lat
        """
        self.longitudes = np.linspace(0.0, 360.0, self.ni, endpoint=False)
        self.latitudes = np.linspace(90.0, -90.0, self.nj)

    @requires_coordinates
    def create_dummy_variable(self) -> xr.Dataset:
        """
        Create a dataset with a random valued data variable
        that fits into the grid.

        This is needed in order to generate the interpolation weights.
        """
        ds = self.create_empty_dataset()
        ds["dummy"] = (("lon", "lat"), np.random.rand(self.ni, self.nj))
        return ds

    def read_values(self, msgid: int) -> np.ndarray:
        """
        Read the data values from the ecCodes handle msgid
        and reshape to match the LonLat grid shape.

        Values are read from ecCodes as a flat array (1D), where
        indices go on Fortran order (first index varies fastest).

        The result is returned as 2D array of shape (ni, nj)
        """
        # Read array
        values = ecc.codes_get_array(msgid, "values")

        # Reshape array
        try:
            values = values.reshape(self.ni, self.nj, order='F')
        except ValueError:
            raise InvalidShapeError(
                self.grid_id, self.ni * self.nj, len(values)
                )

        # Force latitudes from north to south
        if ecc.codes_get(msgid, "latitudeOfFirstGridPoint") < 0.0:
            values = np.flip(values, axis=1)

        return values

    def reshape_for_xarray(self, values: np.ndarray) -> np.ndarray:
        """
        Reshape the default values matrix to fit into the
        xarray DataArray shape.
        
        Input values matrix is expected to have shape (ni, nj)
        while output matrix is expected to have shape (1, 1, Nj, Ni)
        """
        values = values.transpose()
        return values.reshape(1, 1, self.nj, self.ni)
