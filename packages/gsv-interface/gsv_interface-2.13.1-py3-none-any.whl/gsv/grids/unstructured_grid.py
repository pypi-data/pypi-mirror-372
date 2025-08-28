from dataclasses import dataclass
import typing as T
import os
from pathlib import Path

import numpy as np
import xarray as xr
import eccodes as ecc

from gsv.exceptions import (
    InvalidShapeError, UnsupportedUnstructuredGridError,
    MissingGridDefinitionPathError
)
from gsv.grids.grid import Grid, requires_coordinates


@dataclass
class UnstructuredGrid(Grid):
    """
    A class to represent an unstructured grid.

    Coordinates of unstructured grid are read from precomputed
    netCDF files. Supported grids are: tco79, tco399, tco1279,
    tco2559 and eORCA1.

    Attributes
    ----------
    grid_name : str
        Name of grid.
    grid_type : str
        Type of grid.
    longitudes : np.ndarray
        1-D array representing the x-coordinate values.
    latitudes : np.ndarray
        1-D array representing the y-coordinate values.
    lon_corners: np.ndarray
        2-D array representing longitudes for cell corners.
    lat_corners: np.ndarray
        2-D arrat representing latitudes for cell corners.
    dims : List[str]
        Set of dimensions that a xarray.DataArray with
        this grid should have.
    ATTRIBUTES : List[str]
        List of GRIB keys specific to this grid
    GRID_DEFINITION_ROOT : Path
        Path to directory where grid definition fiels are stored.
    GRID_DEFINITIONS : Dict[str, str]
        Mapping from grid_name to name of file describing that grid.
    """

    grid_name: str
    grid_type: str
    longitudes = None
    latitudes = None
    lon_corners = None
    lat_corners = None
    dims: T.ClassVar[T.List[str]] = ["time", "level", "ncells"]
    ATTRIBUTES = {}
    GRID_DEFINITION_ROOT: T.ClassVar[Path] = Path(
        os.environ["GRID_DEFINITION_PATH"]
    ) if "GRID_DEFINITION_PATH" in os.environ else None

    GRID_DEFINITIONS: T.ClassVar[T.Dict[str, str]] = {
        "O80": "std_tco79_grid.nc",
        "O400": "std_tco399_grid.nc",
        "O1280": "std_tco1279_grid.nc",
        "O2560": "std_tco2559_grid.nc",
        "eORCA1_T": "eORCA1_mesh_sfc_grid_T.nc",
        "eORCA1_U": "eORCA1_mesh_sfc_grid_U.nc",
        "eORCA1_V": "eORCA1_mesh_sfc_grid_V.nc",
        "eORCA12_T": "eORCA12_mesh_sfc_grid_T.nc",
        "eORCA12_U": "eORCA12_mesh_sfc_grid_U.nc",
        "eORCA12_V": "eORCA12_mesh_sfc_grid_V.nc",
        "eORCA025_T": "eORCA025_mesh_sfc_grid_T.nc",
        "eORCA025_U": "eORCA025_mesh_sfc_grid_U.nc",
        "eORCA025_V": "eORCA025_mesh_sfc_grid_V.nc"
    }

    @property
    def grid_id(self) -> str:
        """
        CDO grid identifier.
        """
        return self.grid_name

    @property
    @requires_coordinates
    def npix(self) -> int:
        """
        Number of pixels.
        """
        return len(self.longitudes)

    @property
    @requires_coordinates
    def coords(self):
        """
        Dictionary mapping coordinate names and DataArrays.
        For unstructured: lon, lat.
        """
        lon = xr.DataArray(
            data=self.longitudes, dims={"ncells":self.npix},
            attrs={
                "standard_name": "longitude",
                "units": self.lon_units,
                "bounds": "lon_bounds"
            },
            name="lon"
        )

        lat = xr.DataArray(
            data=self.latitudes, dims={"ncells":self.npix},
            attrs={
                "standard_name": "latitudes",
                "units": self.lat_units,
                "bounds": "lat_bounds"
            },
            name="lat"
        )

        return {
            "lon": lon,
            "lat": lat
        }


    @property
    @requires_coordinates
    def coord_bounds(self):
        """
        Dictionary mapping boundary coordinate names and DataArrays.
        For unstructured: lon_boudns, lat_bounds.
        """
        lon_bounds = xr.DataArray(
            data=self.lon_corners,
            dims={"ncells": self.npix, "cell_corners": 4},
            attrs={"units": self.lon_units}, name="lon_bounds"
        )

        lat_bounds = xr.DataArray(
            data=self.lat_corners,
            dims={"ncells": self.npix, "cell_corners": 4},
            attrs={"units": self.lat_units}, name="lat_bounds"
        )

        return {
            "lon_bounds": lon_bounds,
            "lat_bounds": lat_bounds,
        }

    @property
    @requires_coordinates
    def full_coords(self) -> T.Dict[str, xr.DataArray]:
        """
        Dictionary mapping cell coordinate and cell corner coordinate
        names to their corresponding DataArrays.
        """
        return dict(self.coords, **self.coord_bounds)
    
    def compute_coordinates(self) -> None:
        """
        Read coordinates and bounds from predefined netCDF files.
        """
        if self.GRID_DEFINITION_ROOT is None:
            raise MissingGridDefinitionPathError

        if self.grid_name not in self.GRID_DEFINITIONS:
            raise UnsupportedUnstructuredGridError(
                self.grid_id, self.GRID_DEFINITIONS.keys
            )

        grid_filename = self.GRID_DEFINITIONS[self.grid_name]

        # Include exception for file not found
        ds_grid = xr.open_dataset(
            self.GRID_DEFINITION_ROOT / grid_filename
        )

        # Read coord and bounds values
        self.longitudes = ds_grid.lon.values
        self.latitudes = ds_grid.lat.values
        self.lon_corners = ds_grid.lon_bnds.values
        self.lat_corners = ds_grid.lat_bnds.values

        # Read coord units
        self.lon_units = ds_grid.lon.units
        self.lat_units = ds_grid.lat.units


    @requires_coordinates
    def create_dummy_variable(self) -> xr.Dataset:
        """
        Create a dataset with a random valued data variable
        that fits into the grid.

        This is needed in order to generate the interpolation weights.
        """
        ds = self.create_empty_dataset()
        ds["dummy"] = ("ncells", np.random.rand(self.npix))
        return ds

    def read_values(self, msgid: int) -> np.ndarray:
        """
        Read the data values from the ecCodes handle msgid
        and reshape to match the Unstructured grid shape.

        Values are read from ecCodes as a flat array (1D).

        The result is turned with the same shape and order.
        """
        if self.longitudes is None:
            self.compute_coordinates()

        values = ecc.codes_get_array(msgid, "values")
        if len(values) != self.npix:
            raise InvalidShapeError(self.grid_id, self.npix, len(values))

        return values

    def reshape_for_xarray(self, values: np.ndarray) -> np.ndarray:
        """
        Reshape the default values matrix to fit into the
        xarray DataArray shape.
        
        Input values matrix is expected to have shape (npix)
        while output matrix is expected to have shape (1, 1, npix)
        """
        return values.reshape(1, 1, self.npix)
