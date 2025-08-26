
from logging import getLogger as getPythonLogger
from logging import Logger as PythonLogger
from typing import Dict, Tuple, Any

ExcInfoType = bool | BaseException | tuple[type[BaseException], BaseException, Any] | None

def getLogger(name: str) -> "SnakeLogger":
    return SnakeLogger(name)

def get_logger(name:str) -> "SnakeLogger":
    return getLogger(name)

class SnakeLogger:
    """
    Basic wrapper around the python logger.
    The main (optional) feature is to merge any extra kwargs into the extra dictionary
    before calling the python log implementation
    """
    def __init__(self, name: str) -> None:
        self._logger = getPythonLogger(name)

    def __getattr__(self, item):
        # attempt to proxy non-existent methods & attributes to the logger class
        return getattr(self._logger, item)


    # TODO: add more features later
    def set_level(self, level:int|str):
        self._logger.setLevel(level)

    def _build_args(self, exc_info: ExcInfoType = None,
        stack_info: bool = False,
        stacklevel: int = 1,
        extra: dict[str, Any] | None = None, **kwargs)->Dict[str,Any]:

        if len(kwargs) == 0:
            return kwargs

        extras = extra if extra is not None else {}  # kwargs['extra'] if 'extra' in kwargs else {}
        kwargs_processed = {'extra': extras, exc_info:exc_info, stack_info:stack_info, stacklevel:stacklevel}
        for x in kwargs.items():
            extras[x[0]] = x[1]
        return kwargs_processed

    def debug(self,msg,  *args,
                  exc_info: ExcInfoType = False,
                  stack_info: bool = False,
                  stacklevel: int = 1,
                  extra: dict[str, Any] | None = None, **kwargs):
        kwargs = self._build_args(exc_info, stack_info, stacklevel, extra, **kwargs)
        self._logger.debug(msg, *args, **kwargs)

    def info(self, msg, *args,
                  exc_info: ExcInfoType = False,
                  stack_info: bool = False,
                  stacklevel: int = 1,
                  extra: dict[str, Any] | None = None, **kwargs):
        kwargs = self._build_args(exc_info, stack_info, stacklevel, extra, **kwargs)
        self._logger.info(msg, *args, **kwargs)

    def warning(self,msg,  *args,
                  exc_info: ExcInfoType = False,
                  stack_info: bool = False,
                  stacklevel: int = 1,
                  extra: dict[str, Any] | None = None, **kwargs):
        kwargs = self._build_args(exc_info, stack_info, stacklevel, extra, **kwargs)
        self._logger.warning(msg, *args, **kwargs)

    def error(self, msg, *args,
                  exc_info: ExcInfoType = False,
                  stack_info: bool = False,
                  stacklevel: int = 1,
                  extra: dict[str, Any] | None = None, **kwargs):
        kwargs = self._build_args(exc_info, stack_info, stacklevel, extra, **kwargs)
        self._logger.error(msg, *args, **kwargs)


    def critical(self, msg, *args,
                  exc_info: ExcInfoType = False,
                  stack_info: bool = False,
                  stacklevel: int = 1,
                  extra: dict[str, Any] | None = None, **kwargs):
        kwargs = self._build_args(exc_info, stack_info, stacklevel, extra, **kwargs)
        self._logger.critical(msg,*args, **kwargs)

    def fatal(self, msg, *args,
                  exc_info: ExcInfoType = False,
                  stack_info: bool = False,
                  stacklevel: int = 1,
                  extra: dict[str, Any] | None = None, **kwargs):
        kwargs = self._build_args(exc_info, stack_info, stacklevel, extra, **kwargs)
        self._logger.fatal(msg,*args, **kwargs)

    def exception(self, msg, *args,
                  exc_info: ExcInfoType = True,
                  stack_info: bool = False,
                  stacklevel: int = 1,
                  extra: dict[str, Any] | None = None, **kwargs):
        kwargs = self._build_args(exc_info, stack_info, stacklevel, extra, **kwargs)
        """
        Convenience method for logging an ERROR with exception information.
        """
        self._logger.exception(msg, *args, **kwargs)

    def log(self, level, msg, *args, **kwargs):
        self._logger.log(level, msg, *args, **kwargs)
