
from abc import ABC
from logging import LogRecord
from typing import List, Protocol
from abc import abstractmethod

class IProcessor(Protocol):
    @property
    def supports_batching(self)->bool: ...
    def process_records(self, records: List[LogRecord]) -> None: ...

class BaseProcessor(ABC):
    """ Base class for all processors """
    @property
    def supports_batching(self)->bool:
        return self._supports_batching
    @supports_batching.setter
    def supports_batching(self, value:bool)->None:
        self._supports_batching = value

    def __init__(self):
        self._supports_batching = True

    @abstractmethod
    def process_records(self, records:List[LogRecord])->None:
        pass