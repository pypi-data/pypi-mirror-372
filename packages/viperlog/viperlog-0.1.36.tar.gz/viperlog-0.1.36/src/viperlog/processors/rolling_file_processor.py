from enum import Enum
from io import TextIOWrapper


from viperlog.formatters.basic import BasicFormatter
from viperlog.formatters.base import IFormatter
from viperlog.processors.file_processor import FileProcessor
from typing import Dict, Any, Optional, List
import datetime
import json
import os


class RollingFileMode(Enum):
    Monthly = 1
    Daily = 2,
    Hourly = 3

class RollingFileProcessor(FileProcessor):

    def __init__(self, file:str, formatter:Optional[IFormatter[Any]]=BasicFormatter(), mode:RollingFileMode=RollingFileMode.Daily, lazy_open:bool=False):
        """
        Logs to a file,
        Output of the formatter is expected to be either a string or an dict (which will be dumped as json)
        """
        # call super, must be lazy
        super().__init__(file, formatter, lazy_open=True)
        self._mode = mode
        self._stream:Optional[TextIOWrapper] = None if lazy_open else open(self._file, "a")
        self._active_file:Optional[str] = None

    def _get_filename(self) -> str:
        # TODO cache this or something
        # apply logic
        file_name_pattern = "%Y%m%d-%H%M%S"
        if self._mode == RollingFileMode.Monthly:
            file_name_pattern = "%Y%m"
        elif self._mode == RollingFileMode.Daily:
            file_name_pattern = "%Y%m%d"
        elif self._mode == RollingFileMode.Hourly:
            file_name_pattern = "%Y%m%d-%H"

        suffix = datetime.datetime.now(datetime.UTC).strftime(file_name_pattern)
        root, ext = os.path.splitext(self._file)
        new_file = f"{root}-{suffix}{ext}"
        return new_file

    def _get_stream(self):
        """ Override this to apply the rolling logic """
        stream_filename = self._get_filename()
        if self._stream and self._active_file and self._active_file != stream_filename:
            self._stream.flush()
            self._stream.close()
            self._stream = None
            self._active_file = stream_filename

        if not self._stream:
            self._stream = open(stream_filename, "a")
        return self._stream


    def process_messages(self, records: List[Any]) -> None:
        if len(records) > 0:
            if not isinstance(records[0], str):
                records = [json.dumps(x) for x in records]
            self._get_stream().writelines(records)
