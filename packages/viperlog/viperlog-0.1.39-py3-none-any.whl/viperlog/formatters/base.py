
from abc import ABC, abstractmethod
from logging import LogRecord
from typing import Dict, Any, Optional, Protocol
from typing import TypeVar, Generic
from .template import MessageTemplate, IMessageTemplate

T = TypeVar('T')

class IFormatter(Protocol[T]):
    def format(self, record: LogRecord) -> T: ...


#class BaseFormatter(Generic[T], ABC):
class BaseFormatter(IFormatter[T], ABC):
    def __init__(self, template:Optional[str|IMessageTemplate] = None):
        super().__init__()
        if isinstance(template, str):
            template = MessageTemplate(template)
        self.template:Optional[IMessageTemplate] = template


    @abstractmethod
    def format(self, record:LogRecord)->T:
        """
        Formats a log record into a string
        :param record:
        :return: the string representation of a log record
        """
        pass
