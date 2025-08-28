from io import BytesIO
import numpy as np
from pathlib import Path
import pytest
from types import SimpleNamespace
from unittest import mock
import os

import pyfdb

from gsv.retriever import GSVRetriever
from gsv.iterator import MessageIterator, StreamMessageIterator
from gsv.area import RectangularAreaSelector
from gsv.engines import FDBEngine, PolytopeEngine
from gsv.exceptions import (
    MissingGSVMessageError, MissingDatasetError, MissingKeyError,
    InvalidLoggingLevelError, InvalidEngineError, InvalidOutputTypeError,
    UnknownDatabridgeError
)


HOSTNAME = os.environ.get("HOSTNAME", "dummy")


def mock_list_clte_normal(request, duplicates=True, keys=True):
        """
        Mock fdb-list behaviour to test the check_messages_in_fdb allows

        Return list must match the length of the expected messages,
        which for the tests which this is being used is four.
        """
        mars_keys = {
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
                "param": "167",
        }
        msg = {"data": "dummy", "keys": mars_keys}
        n_msgs = 4
        return [msg for _ in range(n_msgs)]

def mock_list_clte_month(request, duplicates=True, keys=True):
        """
        Mock fdb-list behaviour to test the check_messages_in_fdb allows

        Return list must match the length of the expected messages,
        which for the tests which this is being used is four.
        """
        mars_keys = {
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
                "param": "167",
                "month": "02",
                "year": "2020",
        }
        msg = {"data": "dummy", "keys": mars_keys}
        n_msgs = 4
        return [msg for _ in range(n_msgs)]

def mockfdb_clte_normal():
    return SimpleNamespace(list=mock_list_clte_normal)

def mockfdb_clte_month():
    return SimpleNamespace(list=mock_list_clte_month)


def test_get_output_region(basic_request):
    gsv = GSVRetriever()
    basic_request["grid"] = "1.0/1.0"
    basic_request["area"] = [70.0, -10.0, 30.0, 40.0]
    gsv._get_output_area(basic_request)

    assert gsv.area == RectangularAreaSelector([70.0, -10.0, 30.0, 40.0])


def test_fdb_retrieve(fdb_request):
    gsv = GSVRetriever()
    reader = gsv._retrieve(fdb_request)
    assert reader.read(4) == b'GRIB'


def test_fdb_retrieve_missing_data():
    gsv = GSVRetriever()
    reader = gsv._retrieve({"param": "165"})
    assert reader.read(1) == b''


def test_fdb_list(fdb_request):
    gsv = GSVRetriever()
    field_list = list(gsv._list(fdb_request))
    assert len(field_list) == 12


def test_fdb_list_missing_data(fdb_request):
    gsv = GSVRetriever()
    fdb_request["date"] = "19970323"
    field_list = list(gsv._list(fdb_request))
    assert not field_list

# # MOVE test
# def test_add_array_sfc(da_sfc_atmos):
#     gsv = GSVRetriever()
#     gsv._add_array(da_sfc_atmos)
#     assert '2t' in gsv.data_variables
#     assert 'sfc' in gsv.data_variables["2t"]
#     assert isinstance(gsv.data_variables["2t"]["sfc"], list)
#     assert len(gsv.data_variables["2t"]["sfc"]) == 1
#     assert isinstance(gsv.data_variables['2t']["sfc"][0], xr.DataArray)

# # Move test
# def test_add_array_pl(da_pl_atmos):
#     gsv = GSVRetriever()
#     gsv._add_array(da_pl_atmos)
#     assert '2t' in gsv.data_variables
#     assert 0 in gsv.data_variables["2t"]
#     assert isinstance(gsv.data_variables["2t"][0], list)
#     assert len(gsv.data_variables["2t"][0]) == 1
#     assert isinstance(gsv.data_variables["2t"][0][0], xr.DataArray)


def test_decode_messages(gsv_with_datareader):
    gsv = gsv_with_datareader
    gsv.ds = gsv._decode_messages()

    assert gsv.decoder.input_grid.grid_id == "r180x91"
    assert gsv.decoder.output_grid.grid_id == "r180x91"
    assert 'sst' in gsv.decoder.data_variables
    assert set(gsv.ds.data_vars) == {"sst"}
    assert np.isnan(gsv.ds["sst"].values).any()


# Rethink if this tests makes any sense at all
def test_decode_before_retrieve():
    gsv = GSVRetriever()

    with pytest.raises(MissingDatasetError):
        gsv._decode_messages()

# MOVE test
# def test_create_dataset_sfc(da_sfc_atmos):
#     gsv = GSVRetriever()
#     gsv.input_grid = LonLatGrid(10, 10)
#     gsv._add_array(da_sfc_atmos)
#     gsv._create_dataset()

#     assert isinstance(gsv.ds, xr.Dataset)
#     assert isinstance(gsv.ds["2t"], xr.DataArray)
#     assert gsv.ds["2t"].dims == ("time", "lat", "lon")

# # MOVE test
# def test_create_dataset_pl(da_pl_atmos):
#     gsv = GSVRetriever()
#     gsv.input_grid = LonLatGrid(10, 10)
#     gsv._add_array(da_pl_atmos)
#     gsv._create_dataset()

#     assert isinstance(gsv.ds, xr.Dataset)
#     assert isinstance(gsv.ds["2t"], xr.DataArray)
#     assert gsv.ds["2t"].dims == ("time", "level", "lat", "lon")


def test_check_messages_in_fdb(fdb_request):
    gsv = GSVRetriever()
    gsv.check_messages_in_fdb(fdb_request, process_request=False)
    gsv.check_messages_in_fdb(fdb_request, process_request=True)


def test_check_messages_in_fdb_missing(fdb_request):
    gsv = GSVRetriever()
    fdb_request["date"] = "19970323"

    with pytest.raises(MissingGSVMessageError):
        gsv.check_messages_in_fdb(fdb_request)


def test_check_messages_in_fdb_missing_keys(fdb_request):
    gsv = GSVRetriever()
    del(fdb_request["domain"])
    with pytest.raises(MissingKeyError):
        gsv.check_messages_in_fdb(fdb_request, process_request=False)

def test_request_data_fdb_sfc(fdb_request):
    gsv = GSVRetriever()
    gsv.request_data(fdb_request, check_messages_in_fdb=True)

    assert gsv.decoder.input_grid.grid_id == "O400"
    assert gsv.decoder.output_grid.grid_id == "O400"
    assert gsv.decoder.interpolation_method is None
    assert gsv.decoder.iterator_class == MessageIterator
    assert '10u' in gsv.decoder.data_variables
    assert '10v' in gsv.decoder.data_variables
    assert '2t' in gsv.decoder.data_variables
    assert set(gsv.ds.data_vars) == {"10u", "2t", "10v"}
    assert not np.isnan(gsv.ds["10u"].values).any()
    assert not np.isnan(gsv.ds["10v"].values).any()
    assert not np.isnan(gsv.ds["2t"].values).any()

def test_request_data_fdb_pl(fdb_request):
    fdb_request["param"] = "129"
    fdb_request["levtype"] = "pl"
    fdb_request["levelist"] = ["850", "500"]
    gsv = GSVRetriever()
    gsv.request_data(fdb_request)

    assert gsv.decoder.output_grid.grid_id == "O400"
    assert gsv.decoder.interpolation_method is None
    assert 'z' in gsv.decoder.data_variables
    assert set(gsv.ds.data_vars) == {"z"}
    assert not np.isnan(gsv.ds["z"].values).any()

def test_data_request_fdb_interpolation(fdb_request):
    gsv = GSVRetriever()
    fdb_request["grid"] = (72.0, 36.0)
    gsv.request_data(fdb_request)

    assert gsv.decoder.input_grid.grid_id == "O400"
    assert gsv.decoder.output_grid.grid_id == "r5x5"
    assert gsv.decoder.interpolation_method == 'nn'
    assert gsv.decoder.iterator_class == MessageIterator
    assert '10u' in gsv.decoder.data_variables
    assert '10v' in gsv.decoder.data_variables
    assert '2t' in gsv.decoder.data_variables
    assert set(gsv.ds.data_vars) == {"10u", "10v", "2t"}
    assert "weights_nn_O400_r5x5_atmos" in gsv.decoder.interpolator.weights
    assert not np.isnan(gsv.ds["10u"].values).any()
    assert not np.isnan(gsv.ds["10v"].values).any()
    assert not np.isnan(gsv.ds["2t"].values).any()

def test_data_request_fdb_area(fdb_request_area):
    gsv = GSVRetriever()
    gsv.request_data(fdb_request_area)

    assert abs(min(gsv.ds.coords["lat"].values) +89.5) < 1e-5
    assert abs(max(gsv.ds.coords["lat"].values) - 89.5) < 1e-5
    assert abs(min(gsv.ds.coords["lon"].values) - 0.0) < 1e-5
    assert abs(max(gsv.ds.coords["lon"].values) - 180.0) < 1e-5

def test_clear_data(gsv_with_data):
    gsv_with_data.clear_data()

    assert gsv_with_data.request is None
    assert gsv_with_data.decoder is None
    assert gsv_with_data.datareader is None
    assert gsv_with_data.area is None
    assert gsv_with_data.ds is None


def test_data_request_non_empty(gsv_with_data, fdb_request):
    gsv = gsv_with_data
    gsv.request_data(fdb_request)

    assert gsv.decoder.output_grid.grid_id == "O400"
    assert gsv.decoder.interpolation_method is None
    assert '10u' in gsv.decoder.data_variables
    assert '10v' in gsv.decoder.data_variables
    assert '2t' in gsv.decoder.data_variables
    assert 'dummy' not in gsv.decoder.data_variables
    assert set(gsv.ds.data_vars) == {"10u", "10v", "2t"}
    assert 'dummy' in gsv.weights
    assert not np.isnan(gsv.ds["10u"].values).any()
    assert not np.isnan(gsv.ds["10v"].values).any()
    assert not np.isnan(gsv.ds["2t"].values).any()


def test_invalid_logging_level():
    with pytest.raises(InvalidLoggingLevelError):
        GSVRetriever(logging_level="DUMMY")


#TODO: Rethink, get_input_grid is not part of retriver
def test_missing_data_error(basic_request):
    gsv = GSVRetriever()
    basic_request["date"]="19000101"
    gsv.datareader = gsv._retrieve(basic_request)

    with pytest.raises(MissingGSVMessageError):
        gsv._decode_messages()

@pytest.mark.skipif("uan" not in HOSTNAME, reason="Databridge connection can only be tested in Lumi")
@mock.patch.dict(os.environ, {"FDB_HOME": "/appl/local/climatedt/databridge", "FDB5_CONFIG_FILE": "/appl/local/climatedt/databridge/etc/fdb/config.yaml"})
def test_databridge_retrieval(fdb_new_hourly_request):
    gsv = GSVRetriever()
    gsv.request_data(fdb_new_hourly_request, use_stream_iterator=True)
    assert gsv.ds.sizes["time"] == 4


def test_databridge_mock_check_messages_in_fdb_clte_normal(monkeypatch, fdb_new_hourly_request):
    """
    Mock fdb-lsit behaviour to test the check_messages_in_fdb allows
    clte messages being returned with month and year in addition
    to the expected MARS keys.
    """
    monkeypatch.setattr(pyfdb, "FDB", mockfdb_clte_normal)
    gsv = GSVRetriever()
    gsv.check_messages_in_fdb(fdb_new_hourly_request)


def test_databridge_mock_check_messages_in_fdb_clte_month(monkeypatch, fdb_new_hourly_request):
    """
    Mock fdb-lsit behaviour to test the check_messages_in_fdb allows
    clte messages being returned with month and year in addition
    to the expected MARS keys.
    """
    monkeypatch.setattr(pyfdb, "FDB", mockfdb_clte_month)
    gsv = GSVRetriever()
    gsv.check_messages_in_fdb(fdb_new_hourly_request)


def test_invalid_engine():
    with pytest.raises(InvalidEngineError):
        GSVRetriever(engine="dummy")

def test_get_engine_invalid():
    with pytest.raises(InvalidEngineError):
        GSVRetriever.get_engine("dummy")

def test_engine_fdb():
    gsv = GSVRetriever(engine="fdb")
    assert isinstance(gsv.engine, FDBEngine)

def test_get_engine_fdb():
    assert isinstance(GSVRetriever.get_engine("fdb"), FDBEngine)
    assert isinstance(GSVRetriever.get_engine("FDB"), FDBEngine)

def test_engine_polytope():
    gsv = GSVRetriever(engine="polytope")
    assert isinstance(gsv.engine, PolytopeEngine)

def test_get_engine_polytope():
    assert isinstance(GSVRetriever.get_engine("polytope"), PolytopeEngine)
    assert isinstance(GSVRetriever.get_engine("POLYTOPE"), PolytopeEngine)

def test_messages_fdb_polytope(basic_request):
    gsv = GSVRetriever(engine="polytope")
    with pytest.raises(NotImplementedError):
        gsv.check_messages_in_fdb(basic_request)

def test_engine_fdb_with_databridge():
    with pytest.raises(InvalidEngineError):
        gsv = GSVRetriever(engine="fdb", source="lumi")

def test_engine_polytope_default_databridge():
    gsv = GSVRetriever(engine="polytope")
    assert gsv.engine.databridge == "lumi"

def test_engine_polytope_databridge_lumi():
    gsv = GSVRetriever(engine="polytope", source="lumi")
    assert gsv.engine.databridge == "lumi"

def test_engine_polytope_databridge_mn5():
    gsv = GSVRetriever(engine="polytope", source="mn5")
    assert gsv.engine.databridge == "mn5"

def test_engine_polytope_invalid_databridge():
    with pytest.raises(UnknownDatabridgeError):
        GSVRetriever(engine="polytope", source="dummy")

def test_invalid_output_type(basic_request):
    gsv = GSVRetriever()
    with pytest.raises(InvalidOutputTypeError):
        gsv.request_data(basic_request, output_type="dummy")

def test_grib_output(fdb_request):
    output_file = Path('tmp_file.grb')
    gsv = GSVRetriever(logging_level="DEBUG")
    gsv.request_data(fdb_request, output_type="grib", output_filename=output_file)

    with open(output_file, 'rb') as f:
        assert f.read(4) == b'GRIB'

    output_file.unlink()

def test_custom_shortnames(fdb_request, modified_definition_path):
    fdb_request["param"] = ["10u", "10v", "2t"]
    gsv = GSVRetriever(logging_level="DEBUG")
    gsv.request_data(fdb_request, definitions=modified_definition_path)
    assert set(gsv.request["param"]) == {'165', '166', '1'}

def test_set_stream_iterator(fdb_request):
    gsv = GSVRetriever(logging_level="DEBUG")
    gsv.request_data(fdb_request, use_stream_iterator=True)
    assert gsv.decoder.iterator_class == StreamMessageIterator

# def test_request_data_fdb_derived_10si(fdb_request):
#     fdb_request["param"] = ["207"]
#     gsv = GSVRetriever()
#     gsv.request_data(fdb_request, process_derived_variables=True)
#     print(fdb_request)
#     assert gsv.decoder.output_grid.grid_id == "O400"
#     assert gsv.decoder.interpolation_method is None
#     assert '10u' not in gsv.decoder.data_variables
#     assert '10v' not in gsv.decoder.data_variables
#     assert '10si' in gsv.decoder.dat_variables
#     assert set(gsv.ds.data_vars) == {"10si"}
#     assert not np.isnan(gsv.ds["10si"].values).any()

def test_request_data_fdb_int(fdb_request):
    """
    Extra FDB requets with param parsed as integer.

    This test is to catch a missmatching of params when applying
    the filtering in the derived variables features.
    """
    fdb_request["param"] = [165]
    gsv = GSVRetriever()
    gsv.request_data(fdb_request)
    assert gsv.decoder.output_grid.grid_id == "O400"
    assert gsv.decoder.interpolation_method is None
    assert '10u' in gsv.decoder.data_variables
    assert set(gsv.ds.data_vars) == {"10u"}
    assert not np.isnan(gsv.ds["10u"].values).any()

def test_request_data_mockfdb_derived(fdb_request, grib_message_100u, grib_message_100v):
    """
    Test that by default a derived variable will be correctly
    processed.

    A mocked _retrieve method is used to simulate the retrieval.
    This will return raw GRIB messages for 100u and 100v is those
    two variables were requested, and throw a MissingGSVMessageError
    otherwise.

    At the end only the derived variable is expected to appear.
    """

    def mock_retrieve_131_and_132(request):
        if "228246" in request["param"] and "228247" in request["param"]:
            return BytesIO(grib_message_100u + grib_message_100v)
        else:
            raise MissingGSVMessageError("Missing variables 228246 and 228247 in request.")

    fdb_request["param"] = ["100si"]
    gsv = GSVRetriever()
    gsv._retrieve = mock_retrieve_131_and_132
    gsv.request_data(fdb_request)
    assert "100si" in gsv.ds.data_vars

def test_request_data_mockfdb_derived_disabled(fdb_request, grib_message_100u, grib_message_100v):
    """
    Test that disabling the derived variables.

    A mocked _retrieve method is used to simulate the retrieval.
    This will return raw GRIB messages for 100u and 100v is those
    two variables were requested, and throw a MissingGSVMessageError
    otherwise if the original variable is still in the request (as expected).

    At the end only the derived variable is expected to appear.
    """
    def mock_retrieve_131_and_132(request):
        if "228246" in request["param"] and "228247" in request["param"]:
            return BytesIO(grib_message_100u + grib_message_100v)
        elif "228249" in request["param"]:
            raise MissingGSVMessageError("228249 was not processed as derived variable.")

    fdb_request["param"] = ["100si"]
    gsv = GSVRetriever()
    gsv._retrieve = mock_retrieve_131_and_132
    with pytest.raises(MissingGSVMessageError):
        gsv.request_data(fdb_request, process_derived_variables=False)

def test_request_data_fdb_derived_custom_defs(fdb_request):
    """
    Test providing custom derived variables definitions.

    The alternative definitions defines 2t as a module of 10u and 10v.
    This is tested with real retrieving, as both 10u and 10v are in the
    testing FDB.

    Additionally 165 is requested as integer to test the
    int dtype. At the end 10u and 2t should appear, and 10v should not
    since it is not requested.
    """
    fdb_request["param"] = [165, "2t"]
    derived_variables_defs = Path(__file__).parent / "testing_misc_files/alternative_derived_variables.yaml"
    gsv = GSVRetriever()
    gsv.request_data(
        fdb_request, process_derived_variables=True,
        derived_variables_definitions=derived_variables_defs)
    assert "2t" in gsv.ds.data_vars
    assert "10u" in gsv.ds.data_vars
    assert "10v" not in gsv.ds.data_vars
