from pathlib import Path
from polytope.api import Client
from pyfdb import FDB

from gsv.engines import FDBEngine, PolytopeEngine


def test_fdb_engine_init():
    engine = FDBEngine()
    assert isinstance(engine.fdb, FDB)
    assert engine.datareader is None

def test_fdb_engine_list(fdb_request):
    engine = FDBEngine()
    messages = list(engine.list_(fdb_request))
    assert len(messages) == 12

def test_fdb_engine_retrieve(fdb_request):
    engine = FDBEngine()
    fdb_request["step"] = "0"
    fdb_request["param"] = "167"
    datareader = engine.retrieve(fdb_request)
    assert datareader.read(4) == b'GRIB'

def test_fdb_engine_close():
    engine = FDBEngine()
    engine.close()

def test_polytope_engine_init():
    engine = PolytopeEngine()
    assert isinstance(engine.polytope_client, Client)
    assert isinstance(engine.temp_path, Path)

def test_polytope_engine_client():
    engine = PolytopeEngine()
    assert engine.polytope_client.config.get()["address"] == "polytope.lumi.apps.dte.destination-earth.eu"

def test_polytope_engine_tmp_path():
    engine = PolytopeEngine()
    assert engine.temp_path.suffix == '.grb'

# def test_polytope_engine_retrieve(fdb_new_hourly_request):
#     fdb_request = fdb_new_hourly_request
#     engine = PolytopeEngine()
#     fdb_request["time"] = "0000"
#     datareader = engine._retrieve(fdb_request)
#     assert datareader.read(4) == b'GRIB'

#     # Check removal of temp file
#     engine._close()
#     assert not engine.temp_path.exists()
