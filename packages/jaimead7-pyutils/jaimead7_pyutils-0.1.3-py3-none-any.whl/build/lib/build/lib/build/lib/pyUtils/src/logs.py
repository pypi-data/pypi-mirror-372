import logging
import platform
from os import getenv
from pathlib import Path
from typing import Optional


class Styles:
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'
    DEBUG = '\033[0m'
    INFO = '\033[94m'
    WARNING = '\033[93m'
    ERROR = '\033[91m'
    CRITICAL = '\033[101m'
    SUCCEED = '\033[92m'
    PURPLE = '\033[95m'
    BLUE = '\033[94m'
    CYAN = '\033[96m'
    GREEN = '\033[92m'


class _MyFormatter(logging.Formatter):
    CUSTOM_STYLE_NAME = 'custom_style'

    def format(self, record) -> str:
        if hasattr(record, self.CUSTOM_STYLE_NAME):
            custom_style: str = getattr(record, self.CUSTOM_STYLE_NAME)
        else:
            custom_style: str = Styles.ENDC
        arrow: str = '-' * (40 - len(record.levelname + f"[{record.name}]")) + '>'
        log_fmt: str = f'{custom_style}{record.levelname}[{record.name}] {arrow} %(asctime)s:{Styles.ENDC} {record.msg}'
        formatter = logging.Formatter(log_fmt, datefmt='%d/%m/%Y %H:%M:%S')
        return formatter.format(record)


class _MyFileFormatter(logging.Formatter):
    CUSTOM_STYLE_NAME = 'custom_style'

    def format(self, record) -> str:
        arrow: str = '-' * (40 - len(record.levelname + f"[{record.name}]")) + '>'
        log_fmt: str = f'{record.levelname}[{record.name}] {arrow} %(asctime)s: {record.msg}'
        formatter = logging.Formatter(log_fmt, datefmt='%d/%m/%Y %H:%M:%S')
        return formatter.format(record)


class MyLogger():
    _lvls_mapping: dict[str, int] = {
        'NOTSET': logging.NOTSET,
        'DEBUG': logging.DEBUG,
        'INFO': logging.INFO,
        'WARNING': logging.WARNING,
        'WARN': logging.WARN,
        'ERROR': logging.ERROR,
        'CRITICAL': logging.CRITICAL,
        'FATAL': logging.FATAL,
    }

    def __init__(
        self,
        logger_name: str,
        logging_level: int = logging.DEBUG,
        file_path: Optional[Path | str] = None,
        save_logs: bool = False
    ) -> None:
        if logger_name not in logging.Logger.manager.loggerDict.keys():
            self._logger: logging.Logger = logging.getLogger(logger_name)
            self.set_logging_level(logging_level)
            stream_handler: logging.StreamHandler  = logging.StreamHandler()
            stream_handler.setFormatter(_MyFormatter())
            self._logger.addHandler(stream_handler)
        else:
            self._logger: logging.Logger = logging.getLogger(logger_name)
            self.set_logging_level(logging_level)
        if file_path is not None:
            file_path = Path(file_path)
        self._save_logs = False
        self._create_file_handler(file_path)
        self.save_logs = save_logs

    @property
    def name(self) -> str:
        return self._logger.name

    @property
    def level(self) -> int:
        return self._logger.level

    @property
    def parent(self) -> Optional[logging.Logger]:
        return self._logger.parent

    @property
    def level_str(self) -> str:
        return logging.getLevelName(self.level)

    @property
    def save_logs(self) -> bool:
        return self._save_logs

    @save_logs.setter
    def save_logs(self, value: bool) -> None:
        if value:
            self._add_file_handler()
        else:
            self._remove_file_handler()
        self._save_logs: bool = value

    @property
    def logs_file_path(self) -> Path:
        return self._file_path

    @logs_file_path.setter
    def logs_file_path(self, new_path: Path | str) -> None:
        self._remove_file_handler()
        if new_path is not None:
            new_path = Path(new_path)
        self._create_file_handler(new_path)
        self.save_logs = self.save_logs
            

    def _create_file_path(self, file_path: Optional[Path] = None) -> None:
        self._file_path: Path
        if file_path is None or file_path.suffix != '.log':
            relative_path: Path = Path(f'{self.name}.log')
        else:
            if file_path.is_absolute():
                self._file_path = file_path
                return
            relative_path = file_path
        system: str = platform.system().lower()
        temp_path: str
        if system == 'windows':
            temp_path = getenv('TEMP', getenv('TMP', '.'))
        else:
            temp_path = '/tmp'
        self._file_path= Path(getenv('LOGS_PATH', temp_path)) / relative_path

    def _create_file_handler(self, file_path: Optional[Path] = None) -> None:
        self._create_file_path(file_path)
        if not self._file_path.parent.is_dir():
            self._file_path.parent.mkdir(parents= True)
            self._logger.debug(f'Created logs dir "{self._file_path}".')
        self._file_handler = logging.FileHandler(
            self.logs_file_path,
            mode= 'a',
            encoding= 'UTF-8'
        )
        self._file_handler.setFormatter(_MyFileFormatter())
        self._file_handler.setLevel(self._logger.level)

    def _add_file_handler(self) -> None:
        if self._file_handler not in self._logger.handlers:
            self._logger.addHandler(self._file_handler)

    def _remove_file_handler(self) -> None:
        if self._file_handler in self._logger.handlers:
            self._logger.removeHandler(self._file_handler)

    def set_logging_level(self, lvl: int = logging.DEBUG) -> None:
        self._logger.setLevel(lvl)

    def debug(self, msg: str, style: str = Styles.DEBUG) -> None:
        self._logger.debug(
            f'{msg}',
            extra= {_MyFormatter.CUSTOM_STYLE_NAME: style}
        )

    def info(self, msg: str, style: str = Styles.INFO) -> None:
        self._logger.info(
            f'{msg}',
            extra= {_MyFormatter.CUSTOM_STYLE_NAME: style}
        )

    def warning(self, msg: str, style: str = Styles.WARNING) -> None:
        self._logger.warning(
            f'{msg}',
            extra= {_MyFormatter.CUSTOM_STYLE_NAME: style}
        )

    def error(self, msg: str, style: str = Styles.ERROR) -> None:
        self._logger.error(
            f'{msg}',
            extra= {_MyFormatter.CUSTOM_STYLE_NAME: style}
        )

    def critical(self, msg: str, style: str = Styles.CRITICAL) -> None:
        self._logger.critical(
            f'{msg}',
            extra= {_MyFormatter.CUSTOM_STYLE_NAME: style}
        )

    # For compatibility with python < 3.11.
    # Equivalent to logging.getLevelNamesMapping()[lvl_str.upper()] in python >= 3.11.
    @classmethod
    def get_lvl_int(cls, lvl_str: str) -> int:
        try:
            return cls._lvls_mapping[lvl_str.upper()]
        except KeyError:
            return logging.DEBUG
