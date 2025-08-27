
import json
from logging import LogRecord
from typing import Optional

from .base import BaseFormatter
from .dict_formatter import DictFormatter
from .template import IMessageTemplate


class JsonStringFormatter(BaseFormatter[str]):
    def __init__(self, template:Optional[str|IMessageTemplate] = None):
        super().__init__()
        self._helper = DictFormatter(template)


    def format(self, record: LogRecord) -> str:
        # call dict_formatter to keep creating the props the same for most
        result = self._helper.format(record)
        return json.dumps(result)
