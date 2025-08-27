

from .base import BaseFormatter
from logging import LogRecord
from typing import Dict, Any, Callable, Optional

from .template import IMessageTemplate

PropertyFilterFn = Callable[[str], bool]
#class DictFormatter:
#    def format_dict(self, record: LogRecord) -> Dict[str,Any]:
#        # TODO: add more sensible things
#        result = {
#            "name": record.name,
#            "level": record.levelname,
#            "levelNo": record.levelno,
#            "message": record.msg
#       }
#       for k,v in record.__dict__.items():
#           result[k] = v
#        return result

class DictFormatter(BaseFormatter[Dict[str,Any]]):

    def __init__(self, template:Optional[str|IMessageTemplate] = None, property_filter: Optional[PropertyFilterFn] = None):
        """
        Accepts an optional property_filter
        If set then properties are only added if the function returns true
        """
        super().__init__(template)
        self._property_filter = property_filter or (lambda s: True)

    def format(self, record: LogRecord) -> Dict[str,Any]:
        # TODO: add more sensible things
        message = self.template.render(record) if self.template else record.msg
        message_raw = record.msg
        result = {}
        default_props = {
            "name": record.name,
            "level": record.levelname,
            "levelNo": record.levelno,
            "message": message,
            "rawMessage": message_raw
        }
        # add defaults
        for k, v in default_props.items():
            if self._property_filter(k):
                result[k] = v
        # add record props
        for k, v in record.__dict__.items():
            if self._property_filter(k):
                result[k] = v
        return result
