
from abc import ABC
from logging import LogRecord
from typing import List, Protocol
from abc import abstractmethod

from .base import BaseProcessor, IProcessor
#from ..formatters import BaseFormatter, IFormatter  # , BasicFormatter, JsonStringFormatter
from ..formatters.base import IFormatter
from typing import TypeVar, Generic
T = TypeVar('T')


class IGenericProcessor(IProcessor, Protocol[T]):
    def process_messages(self, records: List[T]) -> None: ...

class GenericProcessor(Generic[T], BaseProcessor, ABC):
    """
    Formats the messages using the formatter and calls process_messages
    """

    def __init__(self, formatter:IFormatter[T]):
        super().__init__()
        self._formatter = formatter

    # implement abstract method
    def process_records(self, records: List[LogRecord]) -> None:
        """
        Process & format the LogRecords. Default implementation just formats htem and calls process_messages
        :param records:
        :return:
        """
        items = [self._formatter.format(x) for x in records]
        self.process_messages(items)

    @abstractmethod
    def process_messages(self, records: List[T]) -> None:
        """
        Process the formatted log messages
        :param records:
        :return:
        """
        pass