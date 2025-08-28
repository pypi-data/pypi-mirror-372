from shutil import copyfileobj
from typing import Dict ,BinaryIO

from gsv.engines.engine import Engine


class FDBEngine(Engine):

    NAME = "fdb"

    def __init__(self):
        import pyfdb
        self.fdb = pyfdb.FDB()
        self.datareader = None

    def __str__(self):
        return "<engine 'fdb'>"

    def list_(self, request: Dict):
        return self.fdb.list(request, duplicates=True, keys=True)

    def retrieve(self, request: Dict) -> BinaryIO:  # This is really pyfdb.DataRetriever
        self.datareader = self.fdb.retrieve(request)
        return self.datareader

    def close(self) -> None:
        pass

    def grib_dump(self, grib_filename: str) -> None:
        with open(grib_filename, 'wb') as f:
            copyfileobj(self.datareader ,f)
