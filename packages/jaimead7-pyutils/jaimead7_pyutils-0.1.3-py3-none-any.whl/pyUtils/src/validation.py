from dataclasses import FrozenInstanceError
from datetime import datetime
from functools import wraps
from typing import Any, Callable, Iterable, Optional

from .logs import MyLogger

#from PyQt5.QtCore import QDateTime, Qt

my_logger = MyLogger(
    __name__,
    file_path= 'PyUtils.log'
)


class ValidationClass:
    """Helper class for data validation in dataclasses.
       When set variable values, the class will validate it
            - For each variable in the class define a 'validate_Var' function
            - Var is the name of the variable
            - The function will return a ValidationClass function call -> return ValidationClass.validateInt(value)"""
    def __post_init__(self) -> None:
        """After init the object, validate all variables"""
        for name in self.__dict__.keys():
            if (method := getattr(self, f'validate_{name}', None)):
                try:
                    setattr(self, name, method(getattr(self, name)))
                except FrozenInstanceError:
                    object.__setattr__(self, name, method(getattr(self, name)))

    def __setattr__(self, name: str, value: Any) -> None:
        """Validate variables automaticaly on set.
        Args:
            name (str): name of the variable
            value (Any): value to validate
        """
        if (method := getattr(self, f'validate_{name}', None)):
            try:
                super().__setattr__(name, method(value))
            except FrozenInstanceError:
                object.__setattr__(self, name, method(getattr(self, name)))
            except ValueError as eMsg:
                my_logger.error(str(eMsg))
        else:
            super().__setattr__(name, value)

    @staticmethod
    def optional(func: Callable) -> Callable[..., Optional[Any]]:
        """Decorator for optional variables"""
        @wraps(func)
        def wrapper(*args, **kwargs) -> Optional[Any]:
            if args[0] is None:
                return None
            return func(*args, **kwargs)
        return wrapper

    @staticmethod
    def validateInt(value: Any) -> int:
        try:
            return int(value)
        except (ValueError, TypeError):
            raise TypeError(f'Invalid type int: {value}')

    @staticmethod
    @optional
    def validateOptInt(value: Any) -> Optional[int]:
        return ValidationClass.validateInt(value)

    @staticmethod
    def validatePositiveInt(value: Any) -> int:
        try:
            value = ValidationClass.validateInt(value)
        except (ValueError, TypeError):
            raise TypeError(f'Invalid type positiveInt: {value}')
        if value < 0:
            raise TypeError(f'Invalid type positiveInt: {value}')
        return value

    @staticmethod
    @optional
    def validateOptPositiveInt(value: Any) -> Optional[int]:
        return ValidationClass.validatePositiveInt(value)

    @staticmethod
    def validateStr(value: Any) -> str:
        try:
            return str(value)
        except (ValueError, TypeError):
            raise TypeError(f'Invalid type str: {value}')

    @staticmethod
    @optional
    def validateOptStr(value: Any) -> Optional[str]:
        return ValidationClass.validateStr(value)

    @staticmethod
    def validateDatetime(value: Any) -> datetime:
        if isinstance(value, datetime):
            return value
        value = ValidationClass.validateStr(value)
        for format in ('%Y-%m-%d %H:%M:%S.%f', '%Y-%m-%d %H:%M:%S', '%Y-%m-%dT%H:%M:%S.%f', '%Y-%m-%dT%H:%M:%S.%fZ'):
            try:
                return datetime.strptime(value, format)
            except (ValueError, TypeError):
                pass
        raise TypeError(f'Invalid type datetime: {value}')

    @staticmethod
    @optional
    def validateOptDatetime(value: Any) -> Optional[datetime]:
        return ValidationClass.validateDatetime(value)

    # @staticmethod
    # def validateQtDateTime(value: Any) -> QDateTime:
    #     if isinstance(value, QDateTime):
    #         return value
    #     value = ValidationClass.validateStr(value)
    #     try:
    #         qDateTime: QDateTime = QDateTime.fromString(value, Qt.DateFormat.ISODateWithMs)
    #         if qDateTime != QDateTime():
    #             return qDateTime
    #     except (ValueError, TypeError):
    #         pass
    #     raise TypeError(f'Invalid type QDateTime: {value}')

    # @staticmethod
    # @optional
    # def validateOptQtDateTime(value: Any) -> Optional[QDateTime]:
    #     return ValidationClass.validateQtDateTime(value)

    @staticmethod
    def validateFloat(value: Any) -> float:
        try:
            return float(value)
        except (ValueError, TypeError):
            raise TypeError(f'Invalid type float: {value}')

    @staticmethod
    @optional
    def validateOptFloat(value: Any) -> Optional[float]:
        return ValidationClass.validateFloat(value)

    @staticmethod
    def validateBool(value: Any) -> bool:
        if isinstance(value, bool):
            return value
        if isinstance(value, str):
            if value.upper() in ['1', 'TRUE']:
                return True
            elif value.upper() in ['0', 'FALSE']:
                return False
        if isinstance(value, (int, float)):
            if int(value) == 1:
                return True
            elif int(value) == 0:
                return False
        raise TypeError(f'Invalid type bool: {value}')

    @staticmethod
    @optional
    def validateOptBool(value: Any) -> Optional[bool]:
        return ValidationClass.validateBool(value)

    @staticmethod
    def validateTuple(value: Any,
                      elementsTypes: Optional[tuple[type]] = None) -> tuple:
        try:
            value = tuple(value)
            if elementsTypes is not None:
                if not all(isinstance(element, elementsTypes) for element in value):
                    raise TypeError
            return value
        except (ValueError, TypeError):
            raise TypeError(f'Invalid type tuple: {value}')

    @staticmethod
    def validateList(value: Any,
                     elementsTypes: Optional[tuple[type]] = None) -> list:
        try:
            value = list(value)
            if elementsTypes is not None:
                if not all(isinstance(element, elementsTypes) for element in value):
                    raise TypeError
            return value
        except (ValueError, TypeError):
            raise TypeError(f'Invalid type list: {value}')

    @staticmethod
    def validateDict(value: Any,
                     elementsTypes: Optional[Iterable[type]] = None) -> dict:
        try:
            value = dict(value)
            if elementsTypes is not None:
                if not all(isinstance(key, tuple(elementsTypes)[0]) for key in value.keys()):
                    raise TypeError
                if not all(isinstance(element, tuple(elementsTypes)[1]) for element in value.values()):
                    raise TypeError
            return value
        except (ValueError, TypeError):
            raise TypeError(f'Invalid type list: {value}')
