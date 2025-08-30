from __future__ import annotations

import inspect
import operator
import sys
from functools import reduce
from pathlib import Path
from typing import Any, Optional

import tomli
import tomli_w
from typing_extensions import Self

from .logs import MyLogger

my_logger: MyLogger = MyLogger(
    __name__,
    file_path= 'PyUtils.log',
    save_logs= True
)


class ProjectPathsDict(dict):
    APP_PATH = 'APPPATH'
    DIST_PATH = 'DISTPATH'
    CONFIG_PATH = 'CONFIGPATH'
    CONFIG_FILE_PATH = 'CONFIGFILEPATH'
    
    def __getattr__(self, name: str) -> Any:
        try:
            return self[name]
        except KeyError:
            return None

    def __setitem__(self, key, value) -> None:
        if value is not None:
            if Path(value).exists():
                return super().__setitem__(key, Path(value))
        my_logger.warning(f'"{value}" path does not exists.')
        return super().__setitem__(key, None)

    def set_app_path(self, new_app_path: Optional[str | Path]) -> Self:
        if new_app_path is None:
            self[self.APP_PATH] = None
            self[self.DIST_PATH] = None
            self[self.CONFIG_PATH] = None
            self[self.CONFIG_FILE_PATH] = None
            return self
        self[self.APP_PATH] = Path(new_app_path).resolve()
        try:
            self[self.DIST_PATH] = self[self.APP_PATH] / 'dist'
        except TypeError:
            self[self.DIST_PATH] = None
        try:
            self[self.CONFIG_PATH] = self[self.APP_PATH] / 'dist' / 'config'
        except TypeError:
            self[self.CONFIG_PATH] = None
        try:
            self[self.CONFIG_FILE_PATH] = self[self.APP_PATH] / 'dist' / 'config' / 'config.toml'
        except TypeError:
            self[self.CONFIG_FILE_PATH] = None
        return self

    @staticmethod
    def get_exec_folder() -> Optional[Path]:
        if getattr(sys, 'frozen', False):
            return Path(sys.executable).parents[1]  #CHECK
            #path.abspath(path.join(path.dirname(sys.executable),'..'))
        elif __file__:
            try:
                return Path(inspect.stack()[-1].filename).parents[1]  #CHECK
            except IndexError:
                return None


class ConfigDict(dict):
    def __init__(
        self,
        *args,
        route: Optional[list] = None,
        file_manager: Optional[ConfigFileManager] = None,
        **kwargs
    ) -> None:
        self.route: Optional[list] = route
        self.file_manager: Optional[ConfigFileManager] = file_manager
        super().__init__(*args, **kwargs)

    def __repr__(self) -> str:
        return f'{self.__class__.__name__}(route: {self.route}, fileManager: {self.file_manager})'

    def __str__(self) -> str:
        return str(dict(self.items()))

    def __getattr__(self, name: str) -> Any:
        try:
            return super().__getattribute__(name)
        except AttributeError:
            try:
                return self[str(name)]
            except KeyError:
                msg: str = f'"{name}" not found in the route "{self.route}" of file "{self.file_manager}".'
                my_logger.error(msg)
                raise AttributeError(msg)

    def __getitem__(self, key: str) -> Any:
        result: Any =  super().__getitem__(key)
        if isinstance(result, dict):
            new_route: Optional[list] = self.route
            if new_route is None:
                new_route = [str(key)]
            else:
                new_route.append(str(key))
            return ConfigDict(
                result,
                route= new_route,
                file_manager= self.file_manager
            )
        return result

    def __setattr__(self, name, value: Any) -> None:
        if name in self.keys() and self.file_manager is not None:
            if self.route is None:
                route: list = [name]
            else:
                route: list = self.route + [name]
            self.file_manager.write_var(route, value)
        return super().__setattr__(name, value)


class ConfigFileManager:
    def __init__(self, file_path: str | Path) -> None:
        self._set_file_path(file_path)

    def __repr__(self) -> str:
        return f'{self.__class__.__name__}(file_path: {self._file_path}, data: {self._data})'

    def __str__(self) -> str:
        return str(self._data)

    def __getattr__(self, name: str) -> Any:
        try:
            return self.__dict__[str(name)]
        except KeyError:
            result: Any = self._data[str(name)]
            if isinstance(result, dict):
                result = ConfigDict(
                    result,
                    route= [str(name)],
                    file_manager= self
                )
            return result

    @property
    def file_path(self) -> Path:
        return self._file_path

    @file_path.setter
    def file_path(self, value: str | Path) -> None:
        self._set_file_path(value)

    @property
    def _data(self) -> dict:
        try:
            with open(self._file_path, 'rb') as f:
                data: dict = tomli.load(f)
        except tomli.TOMLDecodeError:
            msg: str = f'{self._file_path} is not a valid .toml file.'
            my_logger.error(msg)
            raise tomli.TOMLDecodeError(msg)
        return data

    def _set_file_path(self, value: str | Path) -> None:
        value = Path(value).with_suffix('.toml')
        if value.is_file():
            self._file_path: Path = value.resolve()
        else:
            msg: str = f'{value} is not a config file.'
            my_logger.error(msg)
            raise FileExistsError(msg)

    def write_file(self, file_content: str | dict) -> None:
        if isinstance(file_content, str):
            self._file_path.write_text(file_content)
        if isinstance(file_content, dict):
            self._file_path.write_text(tomli_w.dumps(file_content))

    def write_var(self, route: list, value: Any) -> None:
        data: dict = self._data
        operator.setitem(reduce(operator.getitem, route[:-1], data), route[-1], value)
        self.write_file(data)
