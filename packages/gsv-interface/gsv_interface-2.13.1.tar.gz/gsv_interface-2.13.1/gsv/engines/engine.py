from abc import ABC, abstractmethod
from typing import Dict ,BinaryIO

class Engine(ABC):

    @abstractmethod
    def retrieve(self, request: Dict) -> BinaryIO:
        pass

    @abstractmethod
    def close(self) -> None:
        pass

    @abstractmethod
    def grib_dump(self, grib_filename: str) -> None:
        pass
