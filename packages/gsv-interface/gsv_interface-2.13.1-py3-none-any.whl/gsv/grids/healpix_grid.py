from dataclasses import dataclass
import typing as T

import numpy as np
import eccodes as ecc
import healpy as hp
import xarray as xr

from gsv.grids.grid import Grid, requires_coordinates


@dataclass
class HealpixGrid(Grid):

    nside: int
    nest: bool
    longitudes = None
    latitudes = None
    lon_corners = None
    lat_corners = None
    dims: T.ClassVar[T.List[str]] = ["time", "level", "ncells"]
    grid_type: T.ClassVar[str] = "healpix"
    ATTRIBUTES = {}

    @property
    def grid_id(self) -> str:
        """
        CDO grid identifier: hp<Nside>
        """
        return f"hp{self.nside}"

    @property
    def npix(self) -> int:
        """
        Number of pixels
        """
        return 12 * self.nside**2

    @property
    @requires_coordinates
    def coords(self) -> T.Dict[str, xr.DataArray]:
        """
        Dictionary mapping coordinate names and DataArrays.
        For healpix: lon, lat.
        """
        lon =  xr.DataArray(
            data=self.longitudes, dims={"ncells":self.npix},
            attrs={
                "standard_name": "longitude",
                "units": "degrees",
                "bounds":"lon_bounds"
            },
            name="lon"
        )

        lat =  xr.DataArray(
            data=self.latitudes, dims={"ncells":self.npix},
            attrs={
                "standard_name": "latitude",
                "units": "degrees",
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
            attrs={"units": "degrees"}, name="lon_bounds"
        )

        lat_bounds = xr.DataArray(
            data=self.lat_corners,
            dims={"ncells": self.npix, "cell_corners": 4},
            attrs={"units": "degrees"}, name="lat_bounds"
        )

        return {
            "lon_bounds": lon_bounds,
            "lat_bounds": lat_bounds
        }

    @property
    @requires_coordinates
    def full_coords(self):
        """
        Dictionary mapping cell coordinate and cell corner coordinate
        names to their corresponding DataArrays.
        """
        return dict(self.coords, **self.coord_bounds)


    def compute_coordinates(self) -> None:
        """
        Compute the coordinates of the grid using the
        grid-defining instance variables.
        For healpix: lon, lat, lon_bounds, lat_bounds
        """
        # Cell centers
        self.longitudes, self.latitudes = hp.pixelfunc.pix2ang(
            self.nside, np.arange(self.npix), self.nest, lonlat=True
        )

        # Cell corner position vector in unit sphere. Shape(npix, 3, 4)
        bounds_vec = hp.boundaries(
            self.nside, np.arange(self.npix), step=1, nest=self.nest
            )

        # Flatten cell number and cell corner dims. Shape(npix*4, 3)
        bounds_2d = bounds_vec.transpose(0, 2, 1).reshape(self.npix * 4, 3)

        # Convert position vectors into lon/lat angles in degrees
        lon_flat, lat_flat = hp.vec2ang(bounds_2d, lonlat=True)

        # Reshape bounds to shape (npix, 4) (4 corners per pixel)
        self.lon_corners = lon_flat.reshape(self.npix, 4)
        self.lat_corners = lat_flat.reshape(self.npix, 4)

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
        and reshape to match the HealPix grid shape.

        Values are read from ecCodes as a flat array (1D), where
        indiceds go on <RING/NESTED> order.

        The result is turned with the same shape and order.
        """
        values = ecc.codes_get_array(msgid, "values")
        return values

    def reshape_for_xarray(self, values: np.ndarray) -> np.ndarray:
        """
        Reshape the default values matrix to fit into the
        xarray DataArray shape.
        
        Input values matrix is expected to have shape (npix)
        while output matrix is expected to have shape (1, 1, npix)
        """
        return values.reshape(1, 1, self.npix)
