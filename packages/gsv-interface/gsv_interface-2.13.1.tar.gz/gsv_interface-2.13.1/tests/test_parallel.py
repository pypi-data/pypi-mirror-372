import numpy as np
import pytest

from gsv.parallel.mp_retriever import GSVMPRetriever


def test_parallel_retriever(fdb_request):
    gsv = GSVMPRetriever(logging_level="DEBUG", engine="fdb", n_proc=4)
    gsv.request_data(fdb_request)
    assert set(gsv.ds.data_vars) == {"10u", "2t", "10v"}
    assert not np.isnan(gsv.ds["10u"].values).any()
    assert not np.isnan(gsv.ds["10v"].values).any()
    assert not np.isnan(gsv.ds["2t"].values).any()

def test_parallel_retriever_levels(fdb_request):
    gsv = GSVMPRetriever(logging_level="DEBUG", engine="fdb", n_proc=4)
    fdb_request["param"] = "129"
    fdb_request["levtype"] = "pl"
    fdb_request["levelist"] = ["500", "850"]
    fdb_request["step"] = "0"
    gsv.logger.warning(fdb_request)
    gsv.request_data(fdb_request)
    assert set(gsv.ds.data_vars) == {"z"}
    assert not np.isnan(gsv.ds["z"].values).any()

def test_parallel_retriever_param(fdb_request):
    gsv = GSVMPRetriever(logging_level="DEBUG", engine="fdb", n_proc=4)
    fdb_request["step"] = "0"
    gsv.request_data(fdb_request)
    assert set(gsv.ds.data_vars) == {"10u", "2t", "10v"}
    assert not np.isnan(gsv.ds["10u"].values).any()
    assert not np.isnan(gsv.ds["10v"].values).any()
    assert not np.isnan(gsv.ds["2t"].values).any()

def test_parallel_mp_grib(fdb_request):
    gsv = GSVMPRetriever(logging_level="DEBUG", engine="fdb", n_proc=4)
    with pytest.raises(NotImplementedError):
        gsv.request_data(fdb_request, output_type="grib")

def test_parallel_retriever_too_many_cores(fdb_request):
    gsv = GSVMPRetriever(logging_level="DEBUG", engine="fdb", n_proc=8)
    gsv.request_data(fdb_request)
    assert set(gsv.ds.data_vars) == {"10u", "2t", "10v"}
    assert not np.isnan(gsv.ds["10u"].values).any()
    assert not np.isnan(gsv.ds["10v"].values).any()
    assert not np.isnan(gsv.ds["2t"].values).any()
