import logging
from pathlib import Path

from .src.config import ConfigDict, ConfigFileManager, ProjectPathsDict
from .src.config import my_logger as config_logger
from .src.logs import MyLogger, Styles
from .src.no_instantiable import NoInstantiable
from .src.no_instantiable import my_logger as no_instantiable_logger
from .src.timing import my_logger as timing_logger
from .src.timing import time_me
from .src.validation import ValidationClass
from .src.validation import my_logger as validation_logger

loggers: tuple[MyLogger, MyLogger, MyLogger, MyLogger] = (
    config_logger,
    no_instantiable_logger,
    timing_logger,
    validation_logger
)

def set_pyutils_logs_path(new_path: Path | str) -> None:
    for logger in loggers:
        logger.logs_file_path = new_path

def save_pyutils_logs(value: bool) -> None:
    for logger in loggers:
        logger.save_logs = value

def set_pyutils_logging_level(lvl: int = logging.DEBUG) -> None:
    for logger in loggers:
        logger.set_logging_level(lvl)

MyLogger(
    __name__,
    file_path= 'PyUtils.log'
).debug(f'Package loaded: pyUtils', Styles.SUCCEED)
