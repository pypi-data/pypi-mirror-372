import os
from pathlib import Path
import pytest

import numpy as np
import xarray as xr
import eccodes as ecc
import yaml

import gsv
from gsv import GSVRetriever
from gsv.dqc import dqc_wrapper
from gsv.logger import get_logger
from gsv.grids import LonLatGrid, HealpixGrid, UnstructuredGrid
from gsv.requests import utils


TEST_FILES = Path(os.environ["GSV_TEST_FILES"])


@pytest.fixture
def lonlat_grid_r10x10():
    return LonLatGrid(10, 10)


@pytest.fixture
def healpix_grid_hp4r():
    return HealpixGrid(4, False)

@pytest.fixture
def tco_grid_79():
    return UnstructuredGrid("O80", "regular_gg")

@pytest.fixture
def basic_request():
    return {
        "levtype": "sfc",
        "date": ["20050401"],
        "time": ["0000", "0600", "1200", "1800"],
        "step": ["0"],
        "param": ["165", "166", "167"]
    }


@pytest.fixture
def fdb_request():
    return {
        "domain": "g",
        "class": "rd",
        "expver": "hz9n",
        "stream": "lwda",
        "type": "fc",
        "anoffset": 9,
        "date": "20200120",
        "time": "0000",
        "param": ["165", "166", "167"],
        "step": ["0", "6", "12", "18"],
        "levtype": "sfc",
    }

@pytest.fixture
def fdb_new_hourly_request():
    return {
        "class": "d1",
        "dataset": "climate-dt",
        "activity": "ScenarioMIP",
        "experiment": "SSP3-7.0",
        "generation": "1",
        "model": "IFS-NEMO",
        "realization": "1",
        "expver": "0001",
        "stream": "clte",
        "date": "20200201",
        "resolution": "standard",
        "type": "fc",
        "levtype": "sfc",
        "time": ["0000", "0600", "1200", "1800"],
        "param": "167"
    }

@pytest.fixture
def fdb_new_monthly_request():
    return {
        "class": "d1",
        "dataset": "climate-dt",
        "activity": "dummy",
        "experiment": "dummy",
        "generation": "dummy",
        "model": "dummy",
        "realization": "dummy",
        "expver": "0001",
        "stream": "clmn",
        "year": "2020",
        "month": "02",
        "resolution": "standard",
        "type": "fc",
        "levtype": "sfc",
        "param": "167"
    }

@pytest.fixture
def fdb_new_wave_request():
    return {
        "class": "d1",
        "dataset": "climate-dt",
        "activity": "dummy",
        "experiment": "dummy",
        "generation": "dummy",
        "model": "dummy",
        "realization": "dummy",
        "expver": "0001",
        "stream": "wave",
        "date": "20200120",
        "resolution": "standard",
        "type": "fc",
        "levtype": "sfc",
        "time": "1200",
        "param": "167",
        "frequency": "dummy",
        "direction": "dummy"
    }

@pytest.fixture
def complete_request_sfc():
    return {
    "levtype": "sfc",
    "step": "0",
    "date": [f"{20050401 + i:8d}" for i in range(5)],
    "time": [f"{100 * i:04d}" for i in range(24)],
    "param":  [
        "sf", "sshf", "slhf", "msl", "tcc", "10u", "10v", "2t",
        "2d", "ssrd", "strd", "ssr", "str", "tsr", "ttr", "10si", "tp",
        "skt", "nsf", "100u", "100v", "100si", "10wdir"
        ]
    }


@pytest.fixture
def complete_request_pl():
    return {
        "levtype": "pl",
        "levelist": ["300", "500", "1000"],
        "step": "0",
        "date": [f"{20050401 + i:8d}" for i in range(5)],
        "time": [f"{100 * i:04d}" for i in range(24)],
        "param": ["z", "r"]
    }

@pytest.fixture
def minimal_reques_sfc():
    return {
        "levtype": "sfc",
        "date": ["20050401"],
        "time": ["0000"],
        "step": "0",
        "param": ["167"]
    }


@pytest.fixture
def minimal_request_pl():
    return {
        "levtype": "pl",
        "levelist": "1000",
        "date": "20050401",
        "time": "0000",
        "step": "0",
        "param": "z"
    }


@pytest.fixture
def request_interp_nn():
    return {
        "levtype": "sfc",
        "date": ["20050401"],
        "time": ["0000", "0600", "1200", "1800"],
        "step": ["0"],
        "param": ["165", "166", "167"],
        "grid": (72.0, 36.0),
        "method": "nn"
    }


@pytest.fixture
def request_interp_con():
    return {
        "levtype": "sfc",
        "date": ["20050401"],
        "time": ["0000", "0600", "1200", "1800"],
        "step": ["0"],
        "param": ["165", "166", "167"],
        "grid": (72.0, 36.0),
        "method": "con"
    }

@pytest.fixture
def fdb_request_area():
    return {
        "class": "rd",
        "stream": "lwda",
        "expver": "hz9n",
        "domain": "g",
        "type": "fc",
        "anoffset": "9",
        "date": "20200120",
        "time": "0000",
        "param": "2t",
        "step": "0",
        "levtype": "sfc",
        "grid": "1.0/1.0",
        "method": "nn",
        "area": "90.0/0.0/-90.0/180.0"
    }

@pytest.fixture
def shortname_request():
    request = {
        "levtype": "sfc",
        "date": ["20050401"],
        "time": ["0000", "0600", "1200", "1800"],
        "step": ["0"],
        "param": ["10u", "10v", "2t"]
    }
    return request


# TODO: rethink this, get_input_gird is not part of retriever
@pytest.fixture
def gsv_with_datareader(grib_file_small):
    gsv = GSVRetriever(logging_level="DEBUG")
    gsv.datareader = grib_file_small
    return gsv

@pytest.fixture
def gsv_input_grid():
    gsv = GSVRetriever(logging_level="DEBUG")
    # gsv.input_grid = LonLatGrid(5000, 2500)
    return gsv


@pytest.fixture
def gsv_with_data():
    gsv = GSVRetriever(logging_level="DEBUG")
    gsv.ds = xr.Dataset()
    gsv.request = basic_request
    gsv.data_variables = {"dummy": xr.Dataset()}
    gsv.weights = {"dummy": xr.Dataset()}
    return gsv

@pytest.fixture
def ds_r180x91():
    return LonLatGrid(180, 91).create_dummy_variable()

@pytest.fixture
def mars_keys():
    return ["date", "time", "levtype", "levelist", "step", "param"]


@pytest.fixture
def lat_coord():
    return xr.DataArray(
        data=np.linspace(90.0, -90.0, 10),
        dims={'lat': 10},
        attrs={
            "standard_name": "latitudes",
            "units": "degrees"
        },
        name="lat"
    )


@pytest.fixture
def lon_coord():
    return xr.DataArray(
        data=np.linspace(0.0, 360.0, 10, endpoint=False),
        dims={'lon': 10},
        attrs={
            "standard_name": "longitude",
            "units": "degrees"
        },
        name="lon"
    )


@pytest.fixture
def da_sfc_atmos(lat_coord, lon_coord):
    return xr.DataArray(
        name='2t', dims={'time': 1, 'lat':10, 'lon':10},
        coords={
            'time': [0],
            'lat': lat_coord,
            'lon': lon_coord
            },
        data=np.random.rand(1, 10 ,10)
    )


@pytest.fixture
def da_pl_atmos(lat_coord, lon_coord):
    return xr.DataArray(
        name='2t', dims={'time': 1, 'level': 1, 'lat':10, 'lon':10},
        coords={
            'time': [0],
            'level': [0],
            'lat': lat_coord,
            'lon': lon_coord
            },
        data=np.random.rand(1, 1, 10 ,10)
    )


@pytest.fixture
def da_sfc_ocean(lat_coord, lon_coord):
    array =  xr.DataArray(
        name='sst', dims={'time': 1, 'lat':10, 'lon':10},
        coords={
            'time': [0],
            'lat': lat_coord,
            'lon': lon_coord
            },
        data=np.random.rand(1, 10 ,10)
    )
    array.values[:, :, 0] = np.nan
    return array


@pytest.fixture
def da_pl_ocean(lat_coord, lon_coord):
    array = xr.DataArray(
        name='sst', dims={'time': 1, 'level': 1, 'lat':10, 'lon':10},
        coords={
            'time': [0],
            'level': [0],
            'lat': lat_coord,
            'lon': lon_coord
            },
        data=np.random.rand(1, 1, 10 ,10)
    )
    array.values[:, :, :, 0] = np.nan
    return array


@pytest.fixture
def grib_file_small():
    filename = TEST_FILES / "sst_small.grb"
    with open(filename, 'rb') as f:
        yield f


@pytest.fixture
def grib_file_trailling():
    filename = TEST_FILES / "sst_small_trailling.grb"
    with open(filename, 'rb') as f:
        yield f


@pytest.fixture
def grib_file_invertlat():
    filename = TEST_FILES / "sst_small_invertlat.grb"
    with open(filename, 'rb') as f:
        yield f


@pytest.fixture
def grib2_file():
    filename = TEST_FILES / "sst_small_grb2.grb"
    with open(filename, 'rb') as f:
        yield f


@pytest.fixture
def grib_file_tco399():
    filename = TEST_FILES / "ssrdc_tco399.grb"
    with open(filename, 'rb') as f:
        yield f

@pytest.fixture
def grib_file_pl():
    filename = TEST_FILES / "small_t_pl.grb"
    with open(filename, 'rb') as f:
        yield f

@pytest.fixture
def grib_file_o3d():
    filename = TEST_FILES / "ocean_3d.grb"
    with open(filename, 'rb') as f:
        yield f

@pytest.fixture
def grib_file_h32():
    filename = TEST_FILES / "h32_t.grb"
    with open(filename, 'rb') as f:
        yield f

@pytest.fixture
def grib_file_inst():
    filename = TEST_FILES / "2t_inst.grb"
    with open(filename, 'rb') as f:
        yield f

@pytest.fixture
def grib_file_acc_1h():
    filename = TEST_FILES / "ssr_acc_1h.grb"
    with open(filename, 'rb') as f:
        yield f

@pytest.fixture
def grib_file_avg_1d():
    filename = TEST_FILES / "avg_sithick_1d.grb"
    with open(filename, 'rb') as f:
        yield f

@pytest.fixture
def grib_file_step_inst():
    filename = TEST_FILES / "inst_step.grb"
    with open(filename, 'rb') as f:
        yield f

@pytest.fixture
def grib_file_step_acc():
    filename = TEST_FILES / "acc_step.grb"
    with open(filename, 'rb') as f:
        yield f

@pytest.fixture
def grib_file_grib1():
    filename = TEST_FILES / "sst_step_grib1.grb"
    with open(filename, 'rb') as f:
        yield f

@pytest.fixture
def grib_file_h32_ring():
    filename = TEST_FILES / "h32_ring.grb"
    with open(filename, 'rb') as f:
        yield f

@pytest.fixture
def eccodes_msgid(grib_file_small):
        msgid = ecc.codes_new_from_file(grib_file_small, 0)
        yield msgid
        ecc.codes_release(msgid)


@pytest.fixture
def eccodes_msgid_invertlat(grib_file_invertlat):
        msgid = ecc.codes_new_from_file(grib_file_invertlat, 0)
        yield msgid
        ecc.codes_release(msgid)


@pytest.fixture
def eccodes_msgid_tco399(grib_file_tco399):
    msgid = ecc.codes_new_from_file(grib_file_tco399, 0)
    yield msgid
    ecc.codes_release(msgid)

@pytest.fixture
def eccodes_msgid_pl(grib_file_pl):
    msgid = ecc.codes_new_from_file(grib_file_pl, 0)
    yield msgid
    ecc.codes_release(msgid)

@pytest.fixture
def eccodes_msgid_o3d(grib_file_o3d):
    msgid = ecc.codes_new_from_file(grib_file_o3d, 0)
    yield msgid
    ecc.codes_release(msgid)

@pytest.fixture
def eccodes_msgid_h32(grib_file_h32):
    msgid = ecc.codes_new_from_file(grib_file_h32, 0)
    yield msgid
    ecc.codes_release(msgid)

@pytest.fixture
def eccodes_msgid_inst(grib_file_inst):
    msgid = ecc.codes_new_from_file(grib_file_inst, 0)
    yield msgid
    ecc.codes_release(msgid)

@pytest.fixture
def eccodes_msgid_acc_1h(grib_file_acc_1h):
    msgid = ecc.codes_new_from_file(grib_file_acc_1h, 0)
    yield msgid
    ecc.codes_release(msgid)

@pytest.fixture
def eccodes_msgid_avg_1d(grib_file_avg_1d):
    msgid = ecc.codes_new_from_file(grib_file_avg_1d, 0)
    yield msgid
    ecc.codes_release(msgid)

@pytest.fixture
def eccodes_msgid_step_inst(grib_file_step_inst):
    msgid = ecc.codes_new_from_file(grib_file_step_inst, 0)
    yield msgid
    ecc.codes_release(msgid)

@pytest.fixture
def eccodes_msgid_step_acc(grib_file_step_acc):
    msgid = ecc.codes_new_from_file(grib_file_step_acc, 0)
    yield msgid
    ecc.codes_release(msgid)

@pytest.fixture
def eccodes_msgid_grib1(grib_file_grib1):
    msgid = ecc.codes_new_from_file(grib_file_grib1, 0)
    yield msgid
    ecc.codes_release(msgid)

@pytest.fixture
def eccodes_msgid_tcc(eccodes_msgid_h128_nest):
    msgid = eccodes_msgid_h128_nest

    # Set parameter to tcc (288164)
    ecc.codes_set(msgid, "parameterCategory", 6)
    ecc.codes_set(msgid, "parameterNumber", 1)
    ecc.codes_set(msgid, "typeOfFirstFixedSurface", 1)
    ecc.codes_set(msgid, "typeOfSecondFixedSurface", 8)

    # Set random values between 0-100 to match boundaries
    values = ecc.codes_get_array(msgid, "values")
    tcc_values = 100*np.random.rand(len(values))
    ecc.codes_set_array(msgid, "values", tcc_values)

    yield msgid
    # No release since original msgid is released after yield

@pytest.fixture
def grib_message(eccodes_msgid):
        return ecc.codes_get_message(eccodes_msgid)

@pytest.fixture
def grib_message_invertlat(eccodes_msgid_invertlat):
        return ecc.codes_get_message(eccodes_msgid_invertlat)

@pytest.fixture
def grib_message_tco399(eccodes_msgid_tco399):
    return ecc.codes_get_message(eccodes_msgid_tco399)

@pytest.fixture
def grib_message_pl(eccodes_msgid_pl):
    return ecc.codes_get_message(eccodes_msgid_pl)

@pytest.fixture
def grib_message_o3d(eccodes_msgid_o3d):
    return ecc.codes_get_message(eccodes_msgid_o3d)

@pytest.fixture
def grib_message_h32(eccodes_msgid_h32):
    return ecc.codes_get_message(eccodes_msgid_h32)

@pytest.fixture
def grib_message_inst(eccodes_msgid_inst):
    return ecc.codes_get_message(eccodes_msgid_inst)

@pytest.fixture
def grib_message_acc_1h(eccodes_msgid_acc_1h):
    return ecc.codes_get_message(eccodes_msgid_acc_1h)

@pytest.fixture
def grib_message_avg_1d(eccodes_msgid_avg_1d):
    return ecc.codes_get_message(eccodes_msgid_avg_1d)

@pytest.fixture
def grib_message_step_inst(eccodes_msgid_step_inst):
    return ecc.codes_get_message(eccodes_msgid_step_inst)

@pytest.fixture
def grib_message_step_acc(eccodes_msgid_step_acc):
    return ecc.codes_get_message(eccodes_msgid_step_acc)

@pytest.fixture
def grib_message_grib1(eccodes_msgid_grib1):
    return ecc.codes_get_message(eccodes_msgid_grib1)

@pytest.fixture
def info_logger():
    return get_logger(logger_name="GSVTest", logging_level='INFO')

@pytest.fixture
def debug_logger():
    return get_logger(logger_name="GSVTest", logging_level='DEBUG')

@pytest.fixture
def default_shortname_filepath():
    return Path(utils.__file__).parent / "shortname_to_paramid.yaml"


@pytest.fixture
def user_definitions(tmp_path):
    temp_def_file = tmp_path / "def.yaml"
    with open(temp_def_file, 'w') as f:
        print('dummy: "1"', file=f)
        print('2t: "2"', file=f)
    yield temp_def_file

@pytest.fixture
def request_dqc_base():
    return {
        "class": "d1",
        "dataset": "climate-dt",
        "experiment": "ssp3-7.0",
        "activity": "scenariomip",
        "model": "ifs-nemo",
        "realization": 1,
        "generation": 1,
        "expver": "0001",
        "type": "fc",
        "stream": "clte",
        "resolution": "standard",
        "levtype": "sfc",
        "param": "167",
        "date": "20200201",
        "time": "0000"
    }

@pytest.fixture
def dqc_base():
    return dqc_wrapper.DQCWrapper(
        profile_path=Path(dqc_wrapper.__file__).parent / "profiles/production/ifs-nemo",
        profiles=["sfc_hourly_healpix_standard.yaml"],
        expver="0001",
        date="20200101",
        model="ifs-nemo",
        experiment="ssp3-7.0",
        activity="scenariomip",
        logging_level="DEBUG",
        sample_length=None,
        halt_mode="end",
        use_stream_iterator=True,
        check_standard_compliance=True,
        check_spatial_completeness=True,
        check_spatial_consistency=True,
        check_physical_plausibility=True
    )

@pytest.fixture
def dqc_hl_full():
    return dqc_wrapper.DQCWrapper(
        profile_path=Path(dqc_wrapper.__file__).parent / "profiles/production/ifs-nemo",
        profiles=["hl_hourly_healpix_standard.yaml"],
        expver="0001",
        date="20200101",
        model="ifs-nemo",
        experiment="ssp3-7.0",
        activity="scenariomip",
        logging_level="DEBUG",
        sample_length=None,
        halt_mode="always",
        use_stream_iterator=True,
        check_standard_compliance=True,
        check_spatial_completeness=True,
        check_spatial_consistency=True,
        check_physical_plausibility=True
    )

@pytest.fixture
def dqc_hl_subsampled():
    return dqc_wrapper.DQCWrapper(
        profile_path=Path(dqc_wrapper.__file__).parent / "profiles/production/ifs-nemo",
        profiles=["hl_hourly_healpix_standard.yaml"],
        expver="0001",
        date="20200101",
        model="ifs-nemo",
        experiment="ssp3-7.0",
        activity="scenariomip",
        logging_level="DEBUG",
        sample_length=10,
        halt_mode="always",
        use_stream_iterator=True,
        check_standard_compliance=True,
        check_spatial_completeness=True,
        check_spatial_consistency=True,
        check_physical_plausibility=True
    )

@pytest.fixture
def dqc_hl_oversampled():
    return dqc_wrapper.DQCWrapper(
        profile_path=Path(dqc_wrapper.__file__).parent / "profiles/production/ifs-nemo",
        profiles=["hl_hourly_healpix_standard.yaml"],
        expver="0001",
        date="20200101",
        model="ifs-nemo",
        experiment="ssp3-7.0",
        activity="scenariomip",
        logging_level="DEBUG",
        sample_length=50,
        halt_mode="always",
        use_stream_iterator=True,
        check_standard_compliance=True,
        check_spatial_completeness=True,
        check_spatial_consistency=True,
        check_physical_plausibility=True
    )

@pytest.fixture
def dqc_dac_passed(dqc_base, request_dqc_base):
    dqc = dqc_base
    dqc.profile = dqc.profiles[0]
    dqc.profile_name = dqc.profile["file"]
    dqc.profile_status = 0
    dqc.variable_db = dqc.read_variable_database()
    dqc.expected_n_checked_messages = 1
    dqc.request = request_dqc_base
    return dqc

@pytest.fixture
def grib_file_h128_nest():
    filename = TEST_FILES / "h128_nest.grb"
    with open(filename, 'rb') as f:
        yield f

@pytest.fixture
def grib_file_h128_nest_4msg():
    filename = TEST_FILES / "h128_nest_4msg.grb"
    with open(filename, 'rb') as f:
        yield f

@pytest.fixture
def eccodes_msgid_h128_nest(grib_file_h128_nest):
    msgid = ecc.codes_new_from_file(grib_file_h128_nest, 0)
    yield msgid
    ecc.codes_release(msgid)

@pytest.fixture
def grib_tempfile_h128_ring(grib_file_h128_nest):
    msgid = ecc.codes_new_from_file(grib_file_h128_nest, 0)
    ecc.codes_set(msgid, "ordering", 0)
    output_filepath = TEST_FILES / "tempfile.grb"
    with open(output_filepath, 'wb') as f:
        ecc.codes_write(msgid, f)

    with open(output_filepath, 'rb') as f:
        yield f

    os.remove(output_filepath)

@pytest.fixture
def grib_tempfile_wrong_bitmap(grib_file_h128_nest):
    msgid = ecc.codes_new_from_file(grib_file_h128_nest, 0)
    ecc.codes_set(msgid, "bitMapIndicator", 0)
    output_filepath = TEST_FILES / "tempfile.grb"
    with open(output_filepath, 'wb') as f:
        ecc.codes_write(msgid, f)

    with open(output_filepath, 'rb') as f:
        yield f

    os.remove(output_filepath)

@pytest.fixture
def grib_tempfile_wrong_second_surface_ocean(grib_file_o3d):
    msgid = ecc.codes_new_from_file(grib_file_o3d, 0)
    # Transform output to new DestinE DGOV schema
    ecc.codes_set(msgid, "subCentre", 1003)
    ecc.codes_set(msgid, "tablesVersion", 31)
    ecc.codes_set(msgid, "localTablesVersion", 1)
    ecc.codes_set(msgid, "significanceOfReferenceTime", 2)
    ecc.codes_set(msgid, "productionStatusOfProcessedData", 12)
    ecc.codes_set(msgid, "destineLocalVersion", 1)
    ecc.codes_set(msgid, "dataset", 1)
    ecc.codes_set(msgid, "activity", 2)
    ecc.codes_set(msgid, "experiment", 7)
    ecc.codes_set(msgid, "generation", 1)
    ecc.codes_set(msgid, "realization", 1)
    ecc.codes_set(msgid, "resolution", 1)
    ecc.codes_set(msgid, "model", 3)
    ecc.codes_set(msgid, "marsStream", 1098)
    # Set paramId to 263507
    ecc.codes_set(msgid, "parameterNumber", 27)
    # The original GRIB file contains typeOfSecondFixedSurface=168 which
    # is not correct for param 263507, but still the paramId is correctly
    # computed. This makes it a good test case for param definition key
    # missmatching,

    output_filepath = TEST_FILES / "tempfile.grb"
    with open(output_filepath, 'wb') as f:
        ecc.codes_write(msgid, f)

    with open(output_filepath, 'rb') as f:
        yield f

    os.remove(output_filepath)

@pytest.fixture
def grib_tempfile_wrong_values(grib_file_h128_nest):
    msgid = ecc.codes_new_from_file(grib_file_h128_nest, 0)
    values = ecc.codes_get_array(msgid, 'values')
    values[10] = -1.0
    ecc.codes_set_array(msgid, "values", values)
    output_filepath = TEST_FILES / "tempfile.grb"
    with open(output_filepath, 'wb') as f:
        ecc.codes_write(msgid, f)

    with open(output_filepath, 'rb') as f:
        yield f

    os.remove(output_filepath)

@pytest.fixture
def grib_tempfile_wrong_tables_version(grib_file_h128_nest):
    msgid = ecc.codes_new_from_file(grib_file_h128_nest, 0)
    ecc.codes_set(msgid, "tablesVersion", 2)
    output_filepath = TEST_FILES / "tempfile.grb"
    with open(output_filepath, 'wb') as f:
        ecc.codes_write(msgid, f)

    with open(output_filepath, 'rb') as f:
        yield f

    os.remove(output_filepath)

@pytest.fixture
def modified_definition_path():
    tmp_def_path = Path("./tmp_defs.yaml")
    with open(tmp_def_path, 'w') as f:
        f.write('"2t": "1"')
    yield tmp_def_path
    tmp_def_path.unlink()

@pytest.fixture
def user_variables_database():
    db_content = """167:
      min: 0.0
      max: 100.0"""
    tmp_db_path = Path("./tmp_vars.yaml")
    with open(tmp_db_path, 'w') as f:
        f.write(db_content)
    yield tmp_db_path
    tmp_db_path.unlink()

@pytest.fixture
def user_variables_db_167_disabled():
    db_content = """167:
      check_enabled: False"""
    tmp_db_path = Path("./tmp_vars_167_disabled.yaml")
    with open(tmp_db_path, 'w') as f:
        f.write(db_content)
    yield tmp_db_path
    tmp_db_path.unlink()

@pytest.fixture
def dqc_dac_passed_2t_disabeld(request_dqc_base, user_variables_db_167_disabled):
    dqc = dqc_wrapper.DQCWrapper(
        profile_path=Path(dqc_wrapper.__file__).parent / "profiles/production/ifs-nemo",
        profiles=["sfc_hourly_healpix_standard.yaml"],
        expver="0001",
        date="20200101",
        model="ifs-nemo",
        experiment="ssp3-7.0",
        activity="scenariomip",
        logging_level="DEBUG",
        sample_length=None,
        halt_mode="end",
        use_stream_iterator=True,
        check_standard_compliance=True,
        check_spatial_completeness=True,
        check_spatial_consistency=True,
        check_physical_plausibility=True,
        variables_config=user_variables_db_167_disabled
    )
    dqc.profile = dqc.profiles[0]
    dqc.profile_name = dqc.profile["file"]
    dqc.profile_status = 0
    # dqc.variable_db = dqc.read_variable_database()
    dqc.expected_n_checked_messages = 1
    dqc.request = request_dqc_base
    return dqc

@pytest.fixture
def dqc_dac_passed_halt_always(request_dqc_base):
    dqc = dqc_wrapper.DQCWrapper(
        profile_path=Path(dqc_wrapper.__file__).parent / "profiles/production/ifs-nemo",
        profiles=["sfc_hourly_healpix_standard.yaml"],
        expver="0001",
        date="20200101",
        model="ifs-nemo",
        experiment="ssp3-7.0",
        activity="scenariomip",
        logging_level="DEBUG",
        sample_length=None,
        halt_mode="always",
        use_stream_iterator=True,
        check_standard_compliance=True,
        check_spatial_completeness=True,
        check_spatial_consistency=True,
        check_physical_plausibility=True,
    )
    dqc.profile = dqc.profiles[0]
    dqc.profile_name = dqc.profile["file"]
    dqc.profile_status = 0
    dqc.expected_n_checked_messages = 1
    dqc.request = request_dqc_base
    return dqc

@pytest.fixture
def derived_variables_db():
    default_db_file = Path(gsv.__file__).parent / "derived/derived_variables.yaml"
    with open(default_db_file, 'r') as f:
        db = yaml.safe_load(f)
    return db

@pytest.fixture
def reference_values_2t_r360x180_nn():
    file = TEST_FILES / "2t_r360x180_nn.nc"
    ds = xr.open_dataset(file)
    return ds["2t"].isel(time=0).values

@pytest.fixture
def reference_values_2t_r360x180_con():
    file = TEST_FILES / "2t_r360x180_con.nc"
    ds = xr.open_dataset(file)
    return ds["2t"].isel(time=0).values

@pytest.fixture
def reference_values_avg_sithick_r360x180_nn():
    file = TEST_FILES / "avg_sithick_r360x180_nn.nc"
    ds = xr.open_dataset(file)
    return ds["avg_sithick"].isel(time=0).values

@pytest.fixture
def reference_values_avg_sithick_r360x180_con():
    file = TEST_FILES / "avg_sithick_r360x180_con.nc"
    ds = xr.open_dataset(file)
    return ds["avg_sithick"].isel(time=0).values

@pytest.fixture
def reference_values_avg_sithick_r360x180_con_remap_area_05():
    file = TEST_FILES / "avg_sithick_r360x180_con_remap_area_05.nc"
    ds = xr.open_dataset(file)
    return ds["avg_sithick"].isel(time=0).values

@pytest.fixture
def grib_message_100u(eccodes_msgid_inst):
    ecc.codes_set(eccodes_msgid_inst, "paramId", 228246)
    return ecc.codes_get_message(eccodes_msgid_inst)

@pytest.fixture
def grib_message_100v(eccodes_msgid_inst):
    ecc.codes_set(eccodes_msgid_inst, "paramId", 228247)
    return ecc.codes_get_message(eccodes_msgid_inst)
