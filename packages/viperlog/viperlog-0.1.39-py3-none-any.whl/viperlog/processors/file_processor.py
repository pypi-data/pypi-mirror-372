from io import TextIOWrapper

from viperlog.formatters.basic import BasicFormatter
from viperlog.formatters.base import IFormatter
from viperlog.processors import GenericProcessor
from typing import Dict, Any, Optional, List
import json


class FileProcessor(GenericProcessor[Any]):

    def __init__(self, file:str, formatter:Optional[IFormatter[Any]]=BasicFormatter(), lazy_open:bool=False):
        """
        Logs to a file,
        Output of the formatter is expected to be either a string or an dict (which will be dumped as json)
        """
        super().__init__(formatter)
        self._file = file
        self._stream:Optional[TextIOWrapper] = None if lazy_open else open(self._get_filename(), "a")

    def _get_filename(self) -> str:
        return self._file

    def _get_stream(self):
        if not self._stream:
            self._stream = open(self._get_filename(), "a")
        return self._stream


    def process_messages(self, records: List[Any]) -> None:
        if len(records) > 0:
            if not isinstance(records[0], str):
                records = [json.dumps(x) for x in records]
            self._get_stream().writelines(records)
