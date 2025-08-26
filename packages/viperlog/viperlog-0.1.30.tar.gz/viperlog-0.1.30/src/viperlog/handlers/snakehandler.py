from ..processors.base import IProcessor
from ..filters.base import IFilter
from logging import LogRecord, Logger
from logging.handlers import MemoryHandler
import logging
from ..types import LoggingType
#import logging.handlers
from typing import List, Optional, Union


class SnakeHandler(MemoryHandler):
    def __init__(self, processors:Optional[Union[IProcessor,List[IProcessor]]] = None, filters:Optional[Union[IFilter,List[IFilter]]] = None, min_level:int=logging.NOTSET, batch_size:int=100, flush_level:int=logging.ERROR):
        """
        Initialize the handler with the buffer size, the level at which
        flushing should occur and an optional target.

        The SnakeHandler taps into the python logging framework collects the information
        and batches the records
        The actual processing is done by adding a processor
        """
        #MemoryHandler.__init__(self, batch_size, flush_level)
        super().__init__(batch_size, flush_level, flushOnClose=True)
        self.__loggers:List[Logger] = []
        self._min_level = min_level
        self._processors:List[IProcessor] = []
        self._filters:List[IFilter] = []

        # we override flush, so we don't need a target, but I set it in case the base class changes in the future
        # NOTE: setting myself as target is inconvenient
        #       bc the logging framework calls handle(..) which should put the message in the buffer
        #       but the flush of the memoryhandler also calls handle on the target
        #       while in our case emit would be better
        # self.setTarget(self)
        if processors:
            if not isinstance(processors, list):
                processors = [processors]
            for p in processors:
                self.add_processor(p)

        if filters:
            if not isinstance(filters, list):
                filters = [filters]
            for f in filters:
                self.add_filter(f)

    def attach_to(self, logger:LoggingType):
        logger.addHandler(self)
        self.__loggers.append(logger)

    def detach_all(self):
        for l in self.__loggers:
            l.removeHandler(self)
        self.__loggers.clear()


    # note naming this is
    def handle(self, record):
        if self._min_level and record.levelno < self._min_level:
            return
        # check filters
        for f in self._filters:
            if f.is_match(record):
                return
        # I don't call super here, because that would end up calling emit()
        #  and i find it more logically to have emit and emit_multi do the same thing
        #super().handle(record)
        self.buffer.append(record)
        if self.shouldFlush(record):
            self.flush()

        # push through to all handlers that don't support batching
        for p in self._processors:
            if not p.supports_batching:
                p.process_records([record])

    def add_filter(self, record_filter:IFilter):
        self._filters.append(record_filter)

    def add_processor(self, processor:IProcessor):
        self._processors.append(processor)

    def flush(self):
        """
        For a MemoryHandler, flushing means just sending the buffered
        records to the target handler, if there is one
        """
        with self.lock:
            #if self.target:
            #    for record in self.buffer:
            #        self.target.handle(record)
            #    self.buffer.clear()
            self.emit_many(self.buffer)
            self.buffer.clear()

    def emit(self, record: LogRecord) -> None:
        self.emit_many([record])

    def emit_many(self, records: List[LogRecord]) -> None:
        if len(records) > 0:
          for p in self._processors:
              # skip handlers that don't support batching because they will already have received the messages
              if p.supports_batching:
                p.process_records(records)



