from pathlib import Path
from typing import Dict, BinaryIO
import uuid

from gsv.engines.engine import Engine
from gsv.exceptions import UnknownDatabridgeError


class PolytopeEngine(Engine):

    NAME = "polytope"
    DATABRIDGES = {
        "lumi": "polytope.lumi.apps.dte.destination-earth.eu",
        "mn5": "polytope.mn5.apps.dte.destination-earth.eu"
    }

    def __init__(self, databridge: str = "lumi"):
        from polytope.api import Client

        # Validate databridge input
        self.validate_databridge_input(databridge)
        self.databridge = databridge.lower()
        self.address = self.get_databridge_address(databridge)

        # Initialize the Polytope client
        self.polytope_client = Client(address=self.address)
        self.temp_path = Path(str(uuid.uuid4())).with_suffix(".grb")

    def __str__(self):
        return f"<engine 'polytope' databridge='{self.databridge}' address='{self.address}'>"

    @classmethod
    def validate_databridge_input(cls, databridge) -> str:
        if databridge.lower() not in cls.DATABRIDGES:
            raise UnknownDatabridgeError(
                databridge=databridge,
                message=f"Unknown databridge: {databridge}. Possible "
                        f"values are {', '.join(cls.DATABRIDGES.keys())}."
            )

    @classmethod
    def get_databridge_address(cls, databridge: str) -> str:
        return cls.DATABRIDGES[databridge.lower()]

    def retrieve(self, request: Dict) -> BinaryIO:
        self.polytope_client.retrieve(
            "destination-earth", request, self.temp_path
        )

        self.f = open(self.temp_path, 'rb')
        return self.f

    def close(self):
        self.f.close()
        self.temp_path.unlink()

    def grib_dump(self, grib_filename):
        self.f.close()
        self.temp_path.rename(grib_filename)
