import os

import pytest

from gsv.retriever import GSVRetriever

HOSTNAME = os.environ.get("HOSTNAME", "dummy")

def test_no_source():
    gsv = GSVRetriever(engine="polytope")
    assert gsv.engine.databridge == "lumi"
    assert gsv.engine.address is not None

def test_source_lumi():
    gsv = GSVRetriever(engine="polytope", source="lumi")
    assert gsv.engine.databridge == "lumi"
    assert gsv.engine.address is not None

def test_source_mn5():
    gsv = GSVRetriever(engine="polytope", source="mn5")
    assert gsv.engine.databridge == "mn5"
    assert gsv.engine.address is not None

@pytest.mark.skipif("glogin" in HOSTNAME, reason="Skipping test on Marenostrum, since it cannot connect to the internet.")
def test_polytope_request_lumi():
    gsv = GSVRetriever(engine="polytope", source="lumi")
    request = {
        "class": "d1",
        "dataset": "climate-dt",
        "experiment": "hist",
        "activity": "cmip6",
        "model": "ifs-nemo",
        "realization": 1,
        "generation": 1,
        "type": "fc",
        "stream": "clte",
        "resolution": "standard",
        "expver": "0001",
        "levtype": "sfc",
        "param": [167],
        "date": 19900101,
        "time": "0000"

    }
    ds = gsv.request_data(request)
    assert "2t" in ds.variables 

@pytest.mark.skipif("glogin" in HOSTNAME, reason="Skipping test on Marenostrum, since it cannot connect to the internet.")
def test_polytope_request_mn5():
    gsv = GSVRetriever(engine="polytope", source="mn5")
    request = {
        "class": "d1",
        "dataset": "climate-dt",
        "experiment": "cont",
        "activity": "highresmip",
        "model": "ifs-fesom",
        "realization": 1,
        "generation": 1,
        "type": "fc",
        "stream": "clte",
        "resolution": "high",
        "expver": "0001",
        "levtype": "sfc",
        "param": [167],
        "date": 19900101,
        "time": "0000"
    }
    ds = gsv.request_data(request)
    assert "2t" in ds.variables