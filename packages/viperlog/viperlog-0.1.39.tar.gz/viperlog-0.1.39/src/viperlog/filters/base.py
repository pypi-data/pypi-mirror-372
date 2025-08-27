
from abc import ABC, abstractmethod
from logging import LogRecord, NOTSET
from typing import Protocol


class IFilter(Protocol):
    def is_match(self, record: LogRecord) -> bool:...
    """
        Determines if the filter matches a row
        if it matches the record should be ignored
        :param record:
        :return: True if the filter is a match, False otherwise
    """

class BaseFilter(ABC):

    @abstractmethod
    def is_match(self, record:LogRecord)->bool:
        """
        Determines if the filter matches a row
        if it matches the record should be ignored
        :param record:
        :return: True if the filter is a match, False otherwise
        """
        return False
