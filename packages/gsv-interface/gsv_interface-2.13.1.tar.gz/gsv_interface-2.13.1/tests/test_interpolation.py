import numpy as np
import xarray as xr
import packaging
import pytest
import smmregrid

from gsv.decoder.gsv_decoder import GSVDecoder
from gsv.interpolate import weights
from gsv.interpolate.gsv_interpolator import GSVInterpolator
from gsv.grids import LonLatGrid
from gsv.exceptions import InvalidInterpolationMethodError, MissingSourceGridError


def test_weight_name_nn_atmos(da_sfc_atmos, da_pl_atmos):
    input_grid = LonLatGrid(10, 10)
    output_grid = LonLatGrid(5, 5)
    method = 'nn'
    for da in (da_sfc_atmos, da_pl_atmos):
        weights_name = weights.get_weights_name(da, input_grid, output_grid, method)
        assert weights_name == 'weights_nn_r10x10_r5x5_atmos'

def test_weight_name_con_atmos(da_sfc_atmos, da_pl_atmos):
    input_grid = LonLatGrid(10, 10)
    output_grid = LonLatGrid(5, 5)
    method = 'con'
    for da in (da_sfc_atmos, da_pl_atmos):
        weights_name = weights.get_weights_name(da, input_grid, output_grid, method)
        assert weights_name == 'weights_con_r10x10_r5x5_atmos'

def test_weight_name_nn_ocean(da_sfc_ocean, da_pl_ocean):
    input_grid = LonLatGrid(10, 10)
    output_grid = LonLatGrid(5, 5)
    method = 'nn'

    weights_name = weights.get_weights_name(da_sfc_ocean, input_grid, output_grid, method)
    assert weights_name == 'weights_nn_r10x10_r5x5_ocean_sfc'

    weights_name = weights.get_weights_name(da_pl_ocean, input_grid, output_grid, method)
    assert weights_name == 'weights_nn_r10x10_r5x5_ocean_0'

def test_weight_name_con_ocean(da_sfc_ocean, da_pl_ocean):
    input_grid = LonLatGrid(10, 10)
    output_grid = LonLatGrid(5, 5)
    method = 'con'

    weights_name = weights.get_weights_name(da_sfc_ocean, input_grid, output_grid, method)
    assert weights_name == 'weights_con_r10x10_r5x5_ocean_sfc'

    weights_name = weights.get_weights_name(da_pl_ocean, input_grid, output_grid, method)
    assert weights_name == 'weights_con_r10x10_r5x5_ocean_0'

def test_weight_name_unknown_variable_atmos(da_sfc_atmos, da_pl_atmos):
    input_grid = LonLatGrid(10, 10)
    output_grid = LonLatGrid(5, 5)
    method = 'nn'
    for da in (da_sfc_atmos, da_pl_atmos):
        da.name = "dummy"
        weights_name = weights.get_weights_name(da, input_grid, output_grid, method)
        assert weights_name == 'weights_nn_r10x10_r5x5_atmos'

def test_weight_name_unknown_variable_ocean(da_sfc_ocean, da_pl_ocean):
    input_grid = LonLatGrid(10, 10)
    output_grid = LonLatGrid(5, 5)
    method = 'nn'
    
    da = da_sfc_ocean
    da.name = "dummy"
    weights_name = weights.get_weights_name(da, input_grid, output_grid, method)
    assert weights_name == 'weights_nn_r10x10_r5x5_ocean_sfc'

    da = da_pl_ocean
    da.name = "dummy"
    weights_name = weights.get_weights_name(da, input_grid, output_grid, method)
    assert weights_name == 'weights_nn_r10x10_r5x5_ocean_0'

def test_weight_invalid_method(da_sfc_atmos, da_pl_atmos, debug_logger):
    input_grid = LonLatGrid(10, 10)
    output_grid = LonLatGrid(5, 5)
    method = 'dummy'
    logger = debug_logger
    for da in (da_sfc_atmos, da_pl_atmos):
        with pytest.raises(InvalidInterpolationMethodError):
            weights.get_weights(da, input_grid, output_grid, method, logger)

def test_weights_filename(da_sfc_atmos):  # Cannot test this as expected answer depends on machine
    pass
    # FIXME
    # input_grid = LonLatGrid(10, 10)
    # output_grid = LonLatGrid(5, 5)
    # method = 'nn'
    # weights_filename = weights.get_weights_filename(da_sfc_atmos, input_grid, output_grid, method)
    # assert weights_filename == "/gpfs/scratch/dese28/dese28006/gsv_weights/weights_nn_r10x10_r5x5_atmos.nc"

def test_weights_from_file(debug_logger):
    da = xr.DataArray(
        name='2t', dims={'level': 1}, coords={'level': [0]},
        data=[1.0]
        )
    input_grid = LonLatGrid(8, 8)
    output_grid = LonLatGrid(4, 4)
    method = 'con'

    # If file is not found, this step will fail as da is not correctly formatted
    weights.get_weights(da, input_grid, output_grid, method, debug_logger)

def test_weights_no_weights_env_variable(da_sfc_atmos, debug_logger):
    input_grid = LonLatGrid(10, 10)
    output_grid = LonLatGrid(5, 5)
    method = 'nn'

    with pytest.MonkeyPatch.context() as mp:
        mp.delenv('GSV_WEIGHTS_PATH', raising=False)
        weights.get_weights(da_sfc_atmos, input_grid, output_grid, method, debug_logger)

def test_interp_atmos(da_sfc_atmos, da_pl_atmos, debug_logger):
    input_grid = LonLatGrid(10, 10)
    output_grid = LonLatGrid(5, 5)
    for da in (da_sfc_atmos, da_pl_atmos):
        weights_ds = weights.get_weights(
            da, input_grid, output_grid, 'nn', debug_logger)
        da_out = smmregrid.regrid(da, weights=weights_ds)
    assert not np.isnan(da_out.values).any()


def test_interp_ocean(da_sfc_ocean, da_pl_ocean, debug_logger):
    input_grid = LonLatGrid(10, 10)
    output_grid = LonLatGrid(5, 5)
    for da in (da_sfc_ocean, da_pl_ocean):
        weights_ds = weights.get_weights(
            da, input_grid, output_grid, 'nn', debug_logger)
        da_out = smmregrid.regrid(da, weights=weights_ds)
    assert np.isnan(da_out.values).any()


def test_interp_atmos_no_logger(da_sfc_atmos, da_pl_atmos):
    input_grid = LonLatGrid(10, 10)
    output_grid = LonLatGrid(5, 5)
    for da in (da_sfc_atmos, da_pl_atmos):
        weights_ds = weights.get_weights(
            da, input_grid, output_grid, 'nn')
        da_out = smmregrid.regrid(da, weights=weights_ds)
    assert not np.isnan(da_out.values).any()

def test_interpolator_init():
    output_grid = LonLatGrid(5, 5)
    interpolator = GSVInterpolator(output_grid)

    assert interpolator.output_grid.grid_id == "r5x5"
    assert interpolator.interpolation_method == "nn"
    assert interpolator.input_grid is None
    assert interpolator.weights == {}

def test_interpolator_init_con():
    output_grid = LonLatGrid(5, 5)
    interpolator = GSVInterpolator(output_grid, "con")

    assert interpolator.output_grid.grid_id == "r5x5"
    assert interpolator.interpolation_method == "con"
    assert interpolator.input_grid is None
    assert interpolator.weights == {}

def test_inteprolator_set_input_grid(debug_logger):
    grid = LonLatGrid(5, 5)
    interpolator = GSVInterpolator(output_grid=grid, logger=debug_logger)
    interpolator.set_input_grid(grid)

    assert interpolator.output_grid.grid_id == "r5x5"
    assert interpolator.interpolation_method == "nn"
    assert interpolator.input_grid.grid_id == "r5x5"
    assert interpolator.weights == {}

def test_interpolator_no_input_grid():
    interpolator = GSVInterpolator(output_grid=LonLatGrid(5, 5))
    da = xr.DataArray(np.random.rand(3, 3), dims=['lat', 'lon'])
    with pytest.raises(MissingSourceGridError):
        interpolator.interpolate(da)

def test_decoder_healpix_atmos_interpolation_nn(grib_file_inst, reference_values_2t_r360x180_nn):
    decoder = GSVDecoder(grid=[1.0, 1.0], method="nn")
    ds = decoder.decode_messages(grib_file_inst)
    assert ds.dims == {"time": 1, "lat": 180, "lon": 360}
    assert not np.any(np.isnan(ds["2t"].values))
    assert np.all(np.isclose(ds["2t"].isel(time=0).values, reference_values_2t_r360x180_nn, rtol=1.0e-3, equal_nan=True))

def test_decoder_healpix_atmos_interpolation_con(grib_file_inst, reference_values_2t_r360x180_con):
    decoder = GSVDecoder(grid=[1.0, 1.0], method="con")
    ds = decoder.decode_messages(grib_file_inst)
    assert ds.dims == {"time": 1, "lat": 180, "lon": 360}
    assert not np.any(np.isnan(ds["2t"].values))
    assert np.all(np.isclose(ds["2t"].isel(time=0).values, reference_values_2t_r360x180_con, rtol=1.0e-3, equal_nan=True))

def test_decoder_healpix_ocean_native_interpolation_nn(grib_file_avg_1d, reference_values_avg_sithick_r360x180_nn):
    decoder = GSVDecoder(grid=[1.0, 1.0], method="nn")
    ds = decoder.decode_messages(grib_file_avg_1d)
    assert ds.dims == {"time": 1,  "lat": 180, "lon": 360}
    assert np.any(np.isnan(ds["avg_sithick"].values))
    assert np.all(np.isclose(ds["avg_sithick"].isel(time=0).values, reference_values_avg_sithick_r360x180_nn, rtol=1.0e-3, equal_nan=True))

@pytest.mark.skipif(packaging.version.parse(smmregrid.__version__) >= packaging.version.parse("0.1.1"),
                    reason="Test only intended for smmregrid < 0.1.1. Remap area 0.0 is only used in smmregrid < 0.1.1")
def test_decoder_healpix_ocean_native_interpolation_con_remap_area_0(grib_file_avg_1d, reference_values_avg_sithick_r360x180_con):
    decoder = GSVDecoder(grid=[1.0, 1.0], method="con")
    ds = decoder.decode_messages(grib_file_avg_1d)
    assert ds.dims == {"time": 1, "lat": 180, "lon": 360}
    assert np.any(np.isnan(ds["avg_sithick"].values))
    assert np.all(np.isclose(ds["avg_sithick"].isel(time=0).values, reference_values_avg_sithick_r360x180_con, rtol=1.0e-3, equal_nan=True))

@pytest.mark.skipif(packaging.version.parse(smmregrid.__version__) < packaging.version.parse("0.1.1"),
                    reason="Test only intended for smmregrid version >= 0.1.1, remap area 0.5 is not available in earlier versions")
def test_decoder_healpix_ocean_native_interpolation_con_remap_area_05(grib_file_avg_1d, reference_values_avg_sithick_r360x180_con_remap_area_05):
    decoder = GSVDecoder(grid=[1.0, 1.0], method="con")
    ds = decoder.decode_messages(grib_file_avg_1d)
    assert ds.dims == {"time": 1, "lat": 180, "lon": 360}
    assert np.any(np.isnan(ds["avg_sithick"].values))
    assert np.all(np.isclose(ds["avg_sithick"].isel(time=0).values, reference_values_avg_sithick_r360x180_con_remap_area_05, rtol=1.0e-3, equal_nan=True))
