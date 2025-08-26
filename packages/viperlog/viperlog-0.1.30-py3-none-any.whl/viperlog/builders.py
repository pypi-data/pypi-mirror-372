#from logging import getLogger

from logging import Logger, getLogger, NOTSET, ERROR, FATAL
from typing import Optional, Self

from .handlers import SnakeHandler
from .processors import BaseProcessor
from .filters import BaseFilter

class HandlerConfigurationBuilder:
    def __init__(self, handler:SnakeHandler):
        self._handler = handler
        pass


    def add_processor(self, processor:BaseProcessor)->Self:
        self._handler.add_processor(processor)
        return self

    def add_filter(self, filter:BaseFilter)->Self:
        self._handler.add_filter(filter)
        return self

    #def build(self)->SnakeHandler:
    #    return self._handler

    def attach_to(self, root_logger:Logger)->SnakeHandler:
        #root_logger.addHandler(self._handler)
        self._handler.attach_to(root_logger)
        return self._handler


class HandlerBuilder:
    def __init__(self):
        self._min_level:int=NOTSET
        self._flush_level:int=ERROR
        self._processor:Optional[BaseProcessor] = None

    def set_flush_level(self, flush_level:int)->Self:
        self._flush_level = flush_level
        return self

    def set_min_level(self, min_level:int)->Self:
        self._min_level = min_level
        return self
    def set_processor(self, processor:BaseProcessor)->Self:
        self._processor = processor
        return self

    def configure(self)->HandlerConfigurationBuilder:
        handler = SnakeHandler(self._processor, min_level=self._min_level, flush_level=self._flush_level)
        return HandlerConfigurationBuilder(handler)
    #def build(self)->SnakeHandler:
    #    handler = SnakeHandler(self._processor, min_level=self._min_level, flush_level=ERROR)
    #    return handler

