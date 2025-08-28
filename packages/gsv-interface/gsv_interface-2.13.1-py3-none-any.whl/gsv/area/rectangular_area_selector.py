import typing as T

import xarray as xr

from gsv.area.area_selector import AreaSelector
from gsv.area.utils import longitude_to_360, longitude_to_180, lon_hemisphere
from gsv.exceptions import InvalidAreaError


class RectangularAreaSelector(AreaSelector):

    def __init__(self, area: T.List[float]):
        self.area = area
        self.standardize_area()

    def __eq__(self, other):
        if isinstance(other, RectangularAreaSelector):
            return self.area == other.area

        return False

    @property
    def north(self) -> float:
        """
        Northernmost boudnary of rectangular area.
        """
        return self.area[0]

    @property
    def south(self) -> float:
        """
        Southernmost boundary of rectangular area.
        """
        return self.area[2]

    @property
    def west(self) -> float:
        """
        Westernmost boundary of rectangular area.
        """
        return self.area[1]

    @property
    def east(self) -> float:
        """
        Easternmost boundary of rectangular area.
        """
        return self.area[3]

    def standardize_area(self):
        """
        Convert the parsed boundaries to a common format:

        Longitudes are converted to either [0, 360) or [-180, 180) format
        in order to ensure `E` is greater or equal than `W`.

        Since areas crossing both the 0.0 and 180.0 longitude point are not
        allowed, `W<E` can only be possible if W and E fall on different
        hemispheres. Tihs condition can only happen in two cases:
        - Case 1: W is in (180, 360)  and `E` is in (0, 180). In this case,
        `W` is converted to [-180, 0) (by changing to [-180, 180) format).

        - Case 2: `W` is in [0,180] and `E` is in [-180, 0). In this case,
        `E` is converted to [180, 360) (by changing to [0, 360) format).
        """
        north, west, south, east = self.north, self.west, self.south, self.east

        # Remove overlapping areas (A3)
        if east - west > 360.0:
            west, east = 0.0, 360.0

        # Avoid big areas (pass to checker)
        if all(
            [
                (east - west) % 360.0 > 180.0,
                lon_hemisphere(west) == lon_hemisphere(east),
            ]
        ):
            raise InvalidAreaError(
                area=[north, west, south, east],
                message="Areas crossing both the 0 and 180 longitude points "
                "cannot be selected with `gsv`. Try asking global area."
            )

        # Ensure wrapping areas follow west < east
        if west > east:

            if east >= 0.0:  # Case 1
                west = longitude_to_180(west)

            else:  # Case 2
                east = longitude_to_360(east)

        self.area = north, west, south, east

    def select_area(self, ds: xr.Dataset):
        north, west, south, east = self.north, self.west, self.south, self.east

        # Crop latitudes
        ds = ds.sel(lat=(ds.lat <= north) & (ds.lat >= south))

        # Crop longitudes
        if west >= 0.0:
            ds = ds.sel(lon=(ds.lon >= west) & (ds.lon <= east))

        else:
            # Roll dataset to [-180, 180) format
            ds.coords["lon"] = (ds.coords["lon"] + 180.0) % 360 - 180.0
            ds = ds.sortby(ds.lon)

            # Crop area
            ds = ds.sel(lon=(ds.lon >= west) & (ds.lon <= east))

        return ds
