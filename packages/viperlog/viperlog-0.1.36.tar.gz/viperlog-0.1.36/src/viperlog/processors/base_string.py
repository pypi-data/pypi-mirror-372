from abc import ABC
from logging import LogRecord
from typing import List
from abc import abstractmethod

from .base_generic import GenericProcessor
from ..formatters import BaseFormatter, BasicFormatter

class BaseStringProcessor(GenericProcessor[str], ABC):
    """
    Formats the messages using the formatter and calls process_messages
    """
    def __init__(self, formatter:BaseFormatter[str] = BasicFormatter()):
        super().__init__(formatter=formatter)

    # @abstractmethod
    #def process_records(self, records: List[LogRecord]) -> None:
    #    """
    #    Process & format the LogRecords. Default implementation just formats them and calls process_messages
    #    :param records:
    #    :return:
    #    """#
    #
    #    items = [self._formatter.format(x) for x in records]
    #    self.process_messages(items)

    @abstractmethod
    def process_messages(self, records: List[str]) -> None:
        """
        Process the formatted log messages
        :param records:
        :return:
        """
        pass

