import pytest
import numpy as np

from gsv.decoder import GSVDecoder

from gsv.decoder.message_decoder import (
    decode_message
)
from gsv.decoder.grid_decoder import (
    _read_lonlat_grid, _read_healpix_grid, _read_unstructured_grid, _get_grid_reader,
    read_grid
)
from gsv.decoder.level_decoder import (
    get_level_reader, decode_level_reader
)
from gsv.decoder.attribute_decoder import (
    _read_xarray_cf_attributes, xarray_cf_attributes,
    MARS_attributes, _read_MARS_attributes
)
from gsv.grids import LonLatGrid, HealpixGrid, UnstructuredGrid
from gsv.levels import (
    PressureLevelReader, SurfaceLevelReader, OceanLevelReader
)
from gsv.exceptions import InvalidShapeError, MissingDatasetError


def test_read_xarray_attributes(eccodes_msgid):
    attrs = _read_xarray_cf_attributes(eccodes_msgid, xarray_cf_attributes)
    assert "standard_name" in attrs
    assert "long_name" in attrs
    assert "units" in attrs
    assert attrs["units"] == "K"
    assert attrs["long_name"] == "Sea surface temperature"
    assert attrs["standard_name"] == "unknown"  # Why?

def test_read_mars_attributes(eccodes_msgid_inst):
    attrs = _read_MARS_attributes(eccodes_msgid_inst, MARS_attributes)
    assert attrs["class"] == "d1"
    assert attrs["dataset"] == "climate-dt"
    assert attrs["experiment"] == "hist"
    assert attrs["activity"].lower() == "cmip6"
    assert attrs["model"].lower() == "ifs-nemo"
    assert attrs["realization"] == "1"
    assert attrs["generation"] == "1"
    assert attrs["stream"] == "clte"
    assert attrs["resolution"] == "standard"
    assert attrs["expver"] == "a0fe"
    assert attrs["type"] == "fc"
    assert attrs["levtype"] == "sfc"

def test_mars_attributes_full_decoder(grib_file_inst):
    decoder = GSVDecoder(logging_level="DEBUG")
    ds = decoder.decode_messages(grib_file_inst)
    attrs = ds["2t"].attrs
    assert attrs["class"] == "d1"
    assert attrs["dataset"] == "climate-dt"
    assert attrs["experiment"] == "hist"
    assert attrs["activity"].lower() == "cmip6"
    assert attrs["model"].lower() == "ifs-nemo"
    assert attrs["realization"] == "1"
    assert attrs["generation"] == "1"
    assert attrs["stream"] == "clte"
    assert attrs["resolution"] == "standard"
    assert attrs["expver"] == "a0fe"
    assert attrs["type"] == "fc"
    assert attrs["levtype"] == "sfc"

def test_decode_message_without_grid(grib_message):
    da = decode_message(grib_message)
    assert da.name == "sst"
    assert set(da.coords) == {"lon", "lat", "time"}
    assert da.values.shape == (1, 91, 180)
    assert "standard_name" in da.attrs
    assert "long_name" in da.attrs
    assert "units" in da.attrs


def test_decode_message_lonlat_grid(grib_message):
    input_grid = LonLatGrid(180, 91)
    da = decode_message(grib_message, input_grid)
    assert da.name == "sst"
    assert set(da.coords) == {"lon", "lat", "time"}
    assert da.values.shape == (1, 91, 180)
    assert "standard_name" in da.attrs
    assert "long_name" in da.attrs
    assert "units" in da.attrs

def test_decode_message_tco_grid(grib_message_tco399):
    input_grid = UnstructuredGrid("O400", "reduced_gg")
    da = decode_message(grib_message_tco399, input_grid)
    assert da.name == "ssrdc"
    assert set(da.coords) == {"lon", "lat", "time"}
    assert da.values.shape == (1, 4*400*(400+9))
    assert "standard_name" in da.attrs
    assert "long_name" in da.attrs
    assert "units" in da.attrs

def test_decode_message_healpix_grid(grib_message_h32):
    input_grid = HealpixGrid(32, False)
    da = decode_message(grib_message_h32, input_grid)
    assert da.name == "t"
    assert set(da.coords) == {"lon", "lat", "level", "time"}
    assert da.values.shape == (1, 1, 12*32*32)
    assert "standard_name" in da.attrs
    assert "long_name" in da.attrs
    assert "units" in da.attrs

def test_decode_message_incorrect_grid(grib_message):
    input_grid = LonLatGrid(5,5)
    with pytest.raises(InvalidShapeError):
        decode_message(grib_message, input_grid)


def test_decode_grid_lonlat(grib_message):
    da = decode_message(grib_message)
    assert da.name == "sst"
    assert set(da.coords) == {"lon", "lat", "time"}
    assert da.values.shape == (1, 91, 180)


def test_decode_grid_tco(grib_message_tco399):
    da = decode_message(grib_message_tco399)
    assert da.name == "ssrdc"
    assert set(da.coords) == {"lon", "lat", "time"}
    assert da.values.shape == (1, 4*400*(400+9))


def test_decode__grid_h32(grib_message_h32):
    da = decode_message(grib_message_h32)
    assert da.name == "t"
    assert set(da.coords) == {"lon", "lat", "level", "time"}
    assert da.values.shape == (1, 1, 12*32*32)


def test_decode_invertlat(grib_message, grib_message_invertlat):
    da_right = decode_message(grib_message).values
    da_inverted = decode_message(grib_message_invertlat).values
    assert np.all(
        da_right[~np.isnan(da_right)] == da_inverted[~np.isnan(da_inverted)]
        )

def test_read_lonlat_grid(eccodes_msgid):
    grid = _read_lonlat_grid(eccodes_msgid)
    assert grid == LonLatGrid(180, 91)

def test_read_tco_grid(eccodes_msgid_tco399):
    grid = _read_unstructured_grid(eccodes_msgid_tco399)
    assert grid == UnstructuredGrid("O400", "reduced_gg")

def test_read_healpix_grid(eccodes_msgid_h32):
    grid = _read_healpix_grid(eccodes_msgid_h32)
    assert grid == HealpixGrid(32, False)

def test_get_grid_reader_lonlat(eccodes_msgid):
    reader = _get_grid_reader(eccodes_msgid)
    assert reader == _read_lonlat_grid

def test_get_grid_reader_tco399(eccodes_msgid_tco399):
    reader = _get_grid_reader(eccodes_msgid_tco399)
    assert reader == _read_unstructured_grid

def test_read_grid(eccodes_msgid, eccodes_msgid_tco399):
    msgids = [eccodes_msgid, eccodes_msgid_tco399]
    expected_grids = [LonLatGrid(180, 91), UnstructuredGrid("O400", "reduced_gg")]
    for msgid, expected_grid in zip(msgids, expected_grids):
        grid = read_grid(msgid)
        assert grid == expected_grid

def test_get_level_reader_pl(eccodes_msgid_pl):
    level_reader = get_level_reader(eccodes_msgid_pl)
    assert isinstance(level_reader, PressureLevelReader)

def test_get_level_reader_sfc(eccodes_msgid):
    level_reader = get_level_reader(eccodes_msgid)
    assert isinstance(level_reader, SurfaceLevelReader)

def test_get_level_reader_o3d(eccodes_msgid_o3d):
    level_reader = get_level_reader(eccodes_msgid_o3d)
    assert isinstance(level_reader, OceanLevelReader)

def test_decode_level_reader_sfc(grib_message):
    levels = decode_level_reader(grib_message)
    assert isinstance(levels, SurfaceLevelReader)

def test_decode_level_reader_pl(grib_message_pl):
    levels = decode_level_reader(grib_message_pl)
    assert isinstance(levels, PressureLevelReader)

def test_decode_level_reader_o3d(grib_message_o3d):
    levels = decode_level_reader(grib_message_o3d)
    assert isinstance(levels, OceanLevelReader)

def test_time_decoding_inst(grib_message_inst):
    da = decode_message(grib_message_inst)
    time = da.time.values[0]
    valid_time = da.valid_time.values[0]
    assert time == np.datetime64('1990-01-02T00:00:00.000000000')
    assert valid_time == np.datetime64('1990-01-02T00:00:00.000000000')

def test_time_decoding_acc_1h(grib_message_acc_1h):
    da = decode_message(grib_message_acc_1h)
    time = da.time.values[0]
    valid_time = da.valid_time.values[0]
    assert time == np.datetime64('1990-01-02T00:00:00.000000000')
    assert valid_time == np.datetime64('1990-01-02T01:00:00.000000000')

def test_time_decoding_avg_1d(grib_message_avg_1d):
    da = decode_message(grib_message_avg_1d)
    time = da.time.values[0]
    valid_time = da.valid_time.values[0]
    assert time == np.datetime64('1990-01-02T00:00:00.000000000')
    assert valid_time == np.datetime64('1990-01-03T00:00:00.000000000')

def test_time_decoding_step_inst(grib_message_step_inst):
    da = decode_message(grib_message_step_inst)
    time = da.time.values[0]
    assert time == np.datetime64('1990-01-02T16:00:00.000000000')

def test_time_decoding_step_acc(grib_message_step_acc):
    da = decode_message(grib_message_step_acc)
    time = da.time.values[0]
    assert time == np.datetime64('1990-01-02T16:00:00.000000000')

def test_time_decoding_grib1(grib_message_grib1):
    da = decode_message(grib_message_grib1)
    time = da.time.values[0]
    assert time == np.datetime64('2014-10-01T15:00:00.000000000')

def test_gsv_get_output_grid():
    grid = GSVDecoder.get_output_grid([1.0, 1.0])
    assert grid == LonLatGrid(360, 180)

def test_gsv_decoder(debug_logger, grib_file_small):
    decoder = GSVDecoder(logging_level="DEBUG")
    decoder.decode_messages(grib_file_small)

    assert decoder.input_grid.grid_id == 'r180x91'
    assert decoder.output_grid.grid_id == 'r180x91'
    assert decoder.interpolation_method is None
    assert decoder.interpolator is None

# TODO: rethink if this test makes any sense
def test_gsv_decoder_no_datareader(debug_logger):
    decoder = GSVDecoder(logging_level="DEBUG")
    with pytest.raises(MissingDatasetError):
        decoder.decode_messages(datareader=None)
