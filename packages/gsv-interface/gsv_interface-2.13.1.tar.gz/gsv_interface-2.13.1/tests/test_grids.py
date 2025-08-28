import pytest
import numpy as np

from gsv.grids import LonLatGrid, UnstructuredGrid
from gsv.exceptions import (
    InvalidShapeError, UnsupportedUnstructuredGridError,
    MissingGridDefinitionPathError
)


def test_grid_id_lonlat(lonlat_grid_r10x10):
    assert lonlat_grid_r10x10.grid_id == "r10x10"


def test_grid_id_healpix(healpix_grid_hp4r):
    assert healpix_grid_hp4r.grid_id == "hp4"


def test_grid_id_unst(tco_grid_79):
    assert tco_grid_79.grid_id == "O80"


def test_npix_lonlat(lonlat_grid_r10x10):
    assert lonlat_grid_r10x10.npix == 10 * 10


def test_npix_healpix(healpix_grid_hp4r):
    assert healpix_grid_hp4r.npix == 12 * 4 ** 2


def test_npix_unst(tco_grid_79):
    assert tco_grid_79.npix == 4 * 80 * (80+9)


def test_coords_lonlat(lonlat_grid_r10x10):
    coords = lonlat_grid_r10x10.coords
    assert coords.keys() == {"lon", "lat"}
    assert np.array_equal(
        coords["lon"].data, np.linspace(0.0, 360.0, 10, endpoint=False)
        )
    assert np.array_equal(coords["lat"].data, np.linspace(90.0, -90, 10))
    

def test_coords_healpix(healpix_grid_hp4r):
    coords = healpix_grid_hp4r.coords
    full_coords = healpix_grid_hp4r.full_coords
    assert coords.keys() == {"lon", "lat"}
    assert full_coords.keys() == {"lon", "lat", "lon_bounds", "lat_bounds"}
    assert len(coords["lon"]) == 12 * 4 ** 2
    assert len(coords["lat"]) == 12 * 4 ** 2
    assert full_coords["lon_bounds"].shape == (12*4**2, 4)
    assert full_coords["lat_bounds"].shape == (12*4**2, 4)


def test_coords_unst(tco_grid_79):
    coords = tco_grid_79.coords
    full_coords = tco_grid_79.full_coords
    assert coords.keys() == {"lon", "lat"}
    assert full_coords.keys() == {"lon", "lat", "lon_bounds", "lat_bounds"}
    assert len(coords["lon"]) == 4 * 80 * (80+9)
    assert len(coords["lat"]) == 4 * 80 * (80+9)
    assert full_coords["lon_bounds"].shape == (4*80*(80+9), 4)
    assert full_coords["lat_bounds"].shape == (4*80*(80+9), 4)


def test_coords_unst_unsupported():
    grid = UnstructuredGrid("dummy", "unstructured_grid")
    with pytest.raises(UnsupportedUnstructuredGridError):
        grid.compute_coordinates()


def test_reshape_lonloat(lonlat_grid_r10x10):
    values = np.arange(100).reshape(10, 10)
    reshaped_values = lonlat_grid_r10x10.reshape_for_xarray(values)
    assert reshaped_values.shape == (1, 1, 10, 10)
    assert np.array_equal(reshaped_values[0, 0, :, 0], np.arange(10))


def test_reshape_healpix(healpix_grid_hp4r):
    values = np.arange(12*4**2)
    reshaped_values = healpix_grid_hp4r.reshape_for_xarray(values)
    assert reshaped_values.shape == (1, 1, 12*4**2)
    assert np.array_equal(reshaped_values[0, 0 ,:], np.arange(12*4**2))


def test_reshape_unst(tco_grid_79):
    values = np.arange(4*80*(80+9))
    reshaped_values = tco_grid_79.reshape_for_xarray(values)
    assert reshaped_values.shape == (1, 1, 4*80*(80+9))
    assert np.array_equal(reshaped_values[0, 0, :], np.arange(4*80*(80+9)))


def test_create_empty_dataset_lonlat(lonlat_grid_r10x10):
    ds = lonlat_grid_r10x10.create_empty_dataset()
    assert set(ds.coords) == {"lon", "lat"}


def test_create_empty_dataset_healpix(healpix_grid_hp4r):
    ds = healpix_grid_hp4r.create_empty_dataset()
    assert set(ds.coords) == {"lon", "lat", "lon_bounds", "lat_bounds"}


def test_create_empty_dataset(tco_grid_79):
    ds = tco_grid_79.create_empty_dataset()
    assert set(ds.coords) == {"lon", "lat", "lon_bounds", "lat_bounds"}


def test_dummy_variable_lonlat(lonlat_grid_r10x10):
    ds = lonlat_grid_r10x10.create_dummy_variable()
    assert 'dummy' in ds
    assert set(ds.coords) == {"lon", "lat"}
    assert set(ds["dummy"].coords) == {"lon", "lat"}


def test_dummy_variable_healpix(healpix_grid_hp4r):
    ds = healpix_grid_hp4r.create_dummy_variable()
    assert 'dummy' in ds
    assert set(ds.coords) == {"lon", "lat", "lon_bounds", "lat_bounds"}
    assert set(ds["dummy"].coords) == {"lon", "lat"}


def test_dummy_variable_unst(tco_grid_79):
    ds = tco_grid_79.create_dummy_variable()
    assert 'dummy' in ds
    assert set(ds.coords) == {"lon", "lat", "lon_bounds", "lat_bounds"}
    assert set(ds["dummy"].coords) == {"lon", "lat"}


def test_read_values_lonlat(eccodes_msgid):
    lonlat_grid = LonLatGrid(180, 91)
    values = lonlat_grid.read_values(eccodes_msgid)
    assert values.shape == (180, 91)


def test_read_values_lonlat_wrong_size(lonlat_grid_r10x10, eccodes_msgid):
    with pytest.raises(InvalidShapeError):
        lonlat_grid_r10x10.read_values(eccodes_msgid)


def test_read_values_unst(eccodes_msgid_tco399):
    unstructured_grid = UnstructuredGrid("O400", "reduced_gg")
    values = unstructured_grid.read_values(eccodes_msgid_tco399)
    assert len(values) == 4 * 400 * (400+9)


def test_read_values_unst_wrong_size(eccodes_msgid):
    unstructured_grid = UnstructuredGrid("O400", "reduced_gg")
    with pytest.raises(InvalidShapeError):
        unstructured_grid.read_values(eccodes_msgid)


def test_coords_unst_missing_grid_def(tco_grid_79):
    tco_grid_79.GRID_DEFINITION_ROOT=None
    with pytest.raises(MissingGridDefinitionPathError):
        tco_grid_79.compute_coordinates()