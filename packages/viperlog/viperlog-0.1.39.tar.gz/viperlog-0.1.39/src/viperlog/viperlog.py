
from logging import getLogger as getPythonLogger, NOTSET, ERROR, FATAL, Logger
from typing import Self, Optional, Union, Dict, List, Any
from .types import LoggingType
from .processors.base import IProcessor
from .filters.base import IFilter
from .handlers.viperhandler import ViperHandler
from .logger import get_logger, SnakeLogger
from uuid import uuid4

class ViperLog:

    __instance:Optional[Self] = None # make sure to assign None here otherwise it doesn't exist

    def __new__(cls, *args, **kwargs):
        # singleton
        if cls.__instance is None:
            cls.__instance = super().__new__(cls)
        return cls.__instance

    # class to maintain some state
    def __init__(self):
        self._logger = getPythonLogger(ViperLog.__name__)
        self._root_logger = getPythonLogger()
        self._processor_map:Dict[str,IProcessor] = {}
        self._handler_map:Dict[str,ViperHandler] = {}

    def get_logger(self, name:str)->SnakeLogger:
        return get_logger(name)

    def register_processor(self, name:str, processor:IProcessor)->None:
        if name in self._processor_map:
            self._logger.warning(f"{name} is already registered as a processor. Overwriting the old value")
        self._processor_map[name] = processor

    def register_handler(self, name:str, handler:ViperHandler)->None:
        if name in self._handler_map:
            self._logger.warning(f"{name} is already registered as a handler. Overwriting the old value")
        self._handler_map[name] = handler

        #def __init__(self, processors: Optional[Union[IProcessor, List[IProcessor]]] = None,
        #             filters: Optional[Union[IFilter, List[IFilter]]] = None, min_level: int = logging.NOTSET,
        #             batch_size: int = 100, flush_level: int = logging.ERROR)

    def setup_handler(self, name:str, logger:Optional[LoggingType|List[LoggingType]] = None, processors:Optional[Union[IProcessor, List[IProcessor]]] = None, filters: Optional[Union[IFilter, List[IFilter]]] = None, min_level: int = NOTSET,
                     batch_size: int = 100, flush_level: int = FATAL, extra:Dict[str,Any] = None)->ViperHandler:
        """

        :param name: The name to register this handler under
        :param logger: A python logger to attach to, If not specified, the root logger will be used
        :param processors: One or more processors to process the messages
        :param filters: Optional filters to add some logic
        :param min_level: The minimum log level (this can also be achieved by a filter)
        :param batch_size: Processors get messages in batches of this size.
        :param flush_level: If a message with this level or higher comes in the log messages are flushed immediately even if the buffer is not yet full
        :param extra: A dictionary with extra values that will be set to all log messages if they are not already present. (Note if multiple handlers modify the same record, the first one wins)
        :return: The SnakeHandler instance
        """
        if not name or len(name) == 0:
            name = str(uuid4())

        handler = ViperHandler(processors=processors, filters=filters, min_level=min_level, batch_size=batch_size, flush_level=flush_level, extra=extra)
        if logger and isinstance(logger, list):
            # process list
            if len(logger) == 0:
                # attach to root
                handler.attach_to(self._root_logger)
            else:
                for x in logger:
                    handler.attach_to(x)
        else: # single object
            handler.attach_to(logger or self._root_logger)
        self.register_handler(name, handler)
        return handler
