#from logging import getLogger

from logging import Logger, getLogger, NOTSET, ERROR
from typing import Optional, Self, Dict, List

from .builders import HandlerBuilder
from .processors.base import BaseProcessor


def get_builder()->HandlerBuilder:
    return HandlerBuilder()

def configure_handler(
        processor:BaseProcessor,
        min_level:int = NOTSET,
        root_logger:Optional[Logger] = None):

    # SnakeHandler
    if not root_logger:
        # get root logger
        root_logger = getLogger()
    #handler = SnakeHandler(processor, min_level=min_level, flush_level=ERROR)
    #root_logger.addHandler(handler)
    get_builder().set_min_level(min_level).configure().add_processor(processor).attach_to(root_logger)

