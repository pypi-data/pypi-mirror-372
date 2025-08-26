#from typing import Union
from logging import Logger as PythonLogger
from .logger import SnakeLogger
#LoggingType = Union[SnakeLogger, PythonLogger]
LoggingType = SnakeLogger|PythonLogger
