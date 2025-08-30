from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Optional

from pytest import fixture, mark, raises

from ..src.validation import *


@dataclass
class ClassWithValidation(ValidationClass):
    int_var: int = 0
    int_opt_var: Optional[int] = None
    pos_int_var: int = 0
    pos_int_opt_var: Optional[int] = None
    str_var: str = ''
    str_opt_var: Optional[str] = None
    dt_var: datetime = datetime.now()
    dt_opt_var: Optional[datetime] = None
    float_var: float = 0.0
    float_opt_var: Optional[float] = None
    bool_var: bool = False
    bool_opt_var: Optional[bool] = None
    tuple_var: tuple = ()
    list_var: list = field(default_factory= list)
    dict_var: dict = field(default_factory= dict)

    def validate_int_var(self, value: Any) -> int:
        return self.validateInt(value)

    def validate_int_opt_var(self, value: Any) -> Optional[int]:
        return self.validateOptInt(value)

    def validate_pos_int_var(self, value: Any) -> int:
        return self.validatePositiveInt(value)

    def validate_pos_int_opt_var(self, value: Any) -> Optional[int]:
        return self.validateOptPositiveInt(value)

    def validate_str_var(self, value: Any) -> str:
        return self.validateStr(value)

    def validate_str_opt_var(self, value: Any) -> Optional[str]:
        return self.validateOptStr(value)

    def validate_dt_var(self, value: Any) -> datetime:
        return self.validateDatetime(value)

    def validate_dt_opt_var(self, value: Any) -> Optional[datetime]:
        return self.validateOptDatetime(value)

    def validate_float_var(self, value: Any) -> float:
        return self.validateFloat(value)

    def validate_float_opt_var(self, value: Any) -> Optional[float]:
        return self.validateOptFloat(value)

    def validate_bool_var(self, value: Any) -> bool:
        return self.validateBool(value)

    def validate_bool_opt_var(self, value: Any) -> Optional[bool]:
        return self.validateOptBool(value)

    def validate_tuple_var(self, value: Any) -> tuple:
        return self.validateTuple(value)

    def validate_list_var(self, value: Any) -> list:
        return self.validateList(value)

    def validate_dict_var(self, value: Any) -> dict:
        return self.validateDict(value)

@fixture
def validation_obj() -> ClassWithValidation:
    return ClassWithValidation()

class TestValidation:
    @mark.parametrize('in_value, out_value', [
        (1, 1),
        (1.4, 1),
        (-1, -1),
        ('1', 1),
        ('-1', -1),
    ])
    def test_int(
        self,
        validation_obj: ClassWithValidation,
        in_value: Any,
        out_value: int
    ) -> None:
        validation_obj.int_var = in_value
        assert validation_obj.int_var == out_value
        assert type(validation_obj.int_var) == type(out_value)

    @mark.parametrize('in_value', [
        None,
        'a',
    ])
    def test_int_errors(
        self,
        validation_obj: ClassWithValidation,
        in_value: Any
    ) -> None:
        with raises(TypeError):
            validation_obj.int_var = in_value

    @mark.parametrize('in_value, out_value', [
        (1, 1),
        (1.4, 1),
        (-1, -1),
        ('1', 1),
        ('-1', -1),
        (None, None),
    ])
    def test_int_opt(
        self,
        validation_obj: ClassWithValidation,
        in_value: Any,
        out_value: Optional[int]
    ) -> None:
        validation_obj.int_opt_var = in_value
        assert validation_obj.int_opt_var == out_value
        assert type(validation_obj.int_opt_var) == type(out_value)

    @mark.parametrize('in_value', [
        'a',
    ])
    def test_int_opt_errors(
        self,
        validation_obj: ClassWithValidation,
        in_value: Any
    ) -> None:
        with raises(TypeError):
            validation_obj.int_opt_var = in_value

    @mark.parametrize('in_value, out_value', [
        (1, 1),
        (1.4, 1),
        ('1', 1),
    ])
    def test_pos_int(
        self,
        validation_obj: ClassWithValidation,
        in_value: Any,
        out_value: int
    ) -> None:
        validation_obj.pos_int_var = in_value
        assert validation_obj.pos_int_var == out_value
        assert type(validation_obj.pos_int_var) == type(out_value)

    @mark.parametrize('in_value', [
        None,
        'a',
        -1,
        '-1',
    ])
    def test_pos_int_errors(
        self,
        validation_obj: ClassWithValidation,
        in_value: Any
    ) -> None:
        with raises(TypeError):
            validation_obj.pos_int_var = in_value

    @mark.parametrize('in_value, out_value', [
        (1, 1),
        (1.4, 1),
        ('1', 1),
        (None, None),
    ])
    def test_pos_int_opt(
        self,
        validation_obj: ClassWithValidation,
        in_value: Any,
        out_value: Optional[int]
    ) -> None:
        validation_obj.pos_int_opt_var = in_value
        assert validation_obj.pos_int_opt_var == out_value
        assert type(validation_obj.pos_int_opt_var) == type(out_value)

    @mark.parametrize('in_value', [
        'a',
        -1,
        '-1',
    ])
    def test_pos_int_opt_errors(
        self,
        validation_obj: ClassWithValidation,
        in_value: Any
    ) -> None:
        with raises(TypeError):
            validation_obj.pos_int_opt_var = in_value

    @mark.parametrize('in_value, out_value', [
        ('a', 'a'),
        (1, '1'),
        (None, 'None'),
    ])
    def test_str(
        self,
        validation_obj: ClassWithValidation,
        in_value: Any,
        out_value: str
    ) -> None:
        validation_obj.str_var = in_value
        assert validation_obj.str_var == out_value
        assert type(validation_obj.str_var) == type(out_value)

    @mark.parametrize('in_value', [
    ])
    def test_str_errors(
        self,
        validation_obj: ClassWithValidation,
        in_value: Any
    ) -> None:
        with raises(TypeError):
            validation_obj.str_var = in_value

    @mark.parametrize('in_value, out_value', [
        ('a', 'a'),
        (1, '1'),
        (None, None),
    ])
    def test_str_opt(
        self,
        validation_obj: ClassWithValidation,
        in_value: Any,
        out_value: Optional[str]
    ) -> None:
        validation_obj.str_opt_var = in_value
        assert validation_obj.str_opt_var == out_value
        assert type(validation_obj.str_opt_var) == type(out_value)

    @mark.parametrize('in_value', [
    ])
    def test_str_opt_errors(
        self,
        validation_obj: ClassWithValidation,
        in_value: Any
    ) -> None:
        with raises(TypeError):
            validation_obj.str_opt_var = in_value

    @mark.parametrize('in_value, out_value', [
        (datetime(2000, 2, 1, 12, 15, 30, 123000), datetime(2000, 2, 1, 12, 15, 30, 123000)),
        ('2000-02-01 12:15:30.123', datetime(2000, 2, 1, 12, 15, 30, 123000)),
        ('2000-02-01 12:15:30', datetime(2000, 2, 1, 12, 15, 30)),
        ('2000-02-01T12:15:30.123', datetime(2000, 2, 1, 12, 15, 30, 123000)),
        ('2000-02-01T12:15:30.123Z', datetime(2000, 2, 1, 12, 15, 30, 123000)),
    ])
    def test_dt(
        self,
        validation_obj: ClassWithValidation,
        in_value: Any,
        out_value: datetime
    ) -> None:
        validation_obj.dt_var = in_value
        assert validation_obj.dt_var == out_value
        assert type(validation_obj.dt_var) == type(out_value)

    @mark.parametrize('in_value', [
        '1',
        'a',
        None,
    ])
    def test_dt_errors(
        self,
        validation_obj: ClassWithValidation,
        in_value: Any
    ) -> None:
        with raises(TypeError):
            validation_obj.dt_var = in_value

    @mark.parametrize('in_value, out_value', [
        (datetime(2000, 2, 1, 12, 15, 30, 123000), datetime(2000, 2, 1, 12, 15, 30, 123000)),
        ('2000-02-01 12:15:30.123', datetime(2000, 2, 1, 12, 15, 30, 123000)),
        ('2000-02-01 12:15:30', datetime(2000, 2, 1, 12, 15, 30)),
        ('2000-02-01T12:15:30.123', datetime(2000, 2, 1, 12, 15, 30, 123000)),
        ('2000-02-01T12:15:30.123Z', datetime(2000, 2, 1, 12, 15, 30, 123000)),
        (None, None)
    ])
    def test_dt_opt(
        self,
        validation_obj: ClassWithValidation,
        in_value: Any,
        out_value: Optional[datetime]
    ) -> None:
        validation_obj.dt_opt_var = in_value
        assert validation_obj.dt_opt_var == out_value
        assert type(validation_obj.dt_opt_var) == type(out_value)

    @mark.parametrize('in_value', [
        '1',
        'a',
    ])
    def test_dt_opt_errors(
        self,
        validation_obj: ClassWithValidation,
        in_value: Any
    ) -> None:
        with raises(TypeError):
            validation_obj.dt_opt_var = in_value

    @mark.parametrize('in_value, out_value', [
        (1, 1.0),
        (1.4, 1.4),
        (-1, -1.0),
        ('1.5', 1.5),
        ('-1.7', -1.7),
    ])
    def test_float(
        self,
        validation_obj: ClassWithValidation,
        in_value: Any,
        out_value: float
    ) -> None:
        validation_obj.float_var = in_value
        assert validation_obj.float_var == out_value
        assert type(validation_obj.float_var) == type(out_value)

    @mark.parametrize('in_value', [
        None,
        'a',
    ])
    def test_float_errors(
        self,
        validation_obj: ClassWithValidation,
        in_value: Any
    ) -> None:
        with raises(TypeError):
            validation_obj.float_var = in_value

    @mark.parametrize('in_value, out_value', [
        (1, 1.0),
        (1.4, 1.4),
        (-1, -1.0),
        ('1.5', 1.5),
        ('-1.7', -1.7),
        (None, None),
    ])
    def test_float_opt(
        self,
        validation_obj: ClassWithValidation,
        in_value: Any,
        out_value: Optional[float]
    ) -> None:
        validation_obj.float_opt_var = in_value
        assert validation_obj.float_opt_var == out_value
        assert type(validation_obj.float_opt_var) == type(out_value)

    @mark.parametrize('in_value', [
        'a',
    ])
    def test_float_opt_errors(
        self,
        validation_obj: ClassWithValidation,
        in_value: Any
    ) -> None:
        with raises(TypeError):
            validation_obj.float_opt_var = in_value

    @mark.parametrize('in_value, out_value', [
        (True, True),
        (1, True),
        (0, False),
        ('true', True),
        ('TRUE', True),
        ('false', False),
        ('FALSE', False),
    ])
    def test_bool(
        self,
        validation_obj: ClassWithValidation,
        in_value: Any,
        out_value: bool
    ) -> None:
        validation_obj.bool_var = in_value
        assert validation_obj.bool_var == out_value
        assert type(validation_obj.bool_var) == type(out_value)

    @mark.parametrize('in_value', [
        None,
        'a',
        5,
    ])
    def test_bool_errors(
        self,
        validation_obj: ClassWithValidation,
        in_value: Any
    ) -> None:
        with raises(TypeError):
            validation_obj.bool_var = in_value

    @mark.parametrize('in_value, out_value', [
        (True, True),
        (1, True),
        (0, False),
        ('true', True),
        ('TRUE', True),
        ('false', False),
        ('FALSE', False),
        (None, None),
    ])
    def test_bool_opt(
        self,
        validation_obj: ClassWithValidation,
        in_value: Any,
        out_value: Optional[bool]
    ) -> None:
        validation_obj.bool_opt_var = in_value
        assert validation_obj.bool_opt_var == out_value
        assert type(validation_obj.bool_opt_var) == type(out_value)

    @mark.parametrize('in_value', [
        'a',
        5,
    ])
    def test_bool_opt_errors(
        self,
        validation_obj: ClassWithValidation,
        in_value: Any
    ) -> None:
        with raises(TypeError):
            validation_obj.bool_opt_var = in_value

    @mark.parametrize('in_value, out_value', [
        ((1, 2), (1, 2)),
        ([1, 2], (1, 2)),
        ('abc', ('a', 'b', 'c')),
    ])
    def test_tuple(
        self,
        validation_obj: ClassWithValidation,
        in_value: Any,
        out_value: tuple
    ) -> None:
        validation_obj.tuple_var = in_value
        assert validation_obj.tuple_var == out_value
        assert type(validation_obj.tuple_var) == type(out_value)

    @mark.parametrize('in_value', [
        5,
        None,
    ])
    def test_tuple_errors(
        self,
        validation_obj: ClassWithValidation,
        in_value: Any
    ) -> None:
        with raises(TypeError):
            validation_obj.tuple_var = in_value

    @mark.parametrize('in_value, types, out_value', [
        ((1, 2), (int), (1, 2)),
        ([1, 4, 2.1, 'a'], (int, float, str), (1, 4, 2.1, 'a')),
    ])
    def test_tuple_with_types(
        self,
        validation_obj: ClassWithValidation,
        in_value: Any,
        types: tuple[type],
        out_value: tuple
    ) -> None:
        def validate_tuple_with_types_var(value: Any) -> tuple:
            return ValidationClass.validateTuple(value, types)
        validation_obj.validate_tuple_with_types_var = validate_tuple_with_types_var
        validation_obj.tuple_with_types_var = in_value
        assert getattr(validation_obj, 'tuple_with_types_var') == out_value
        assert type(getattr(validation_obj, 'tuple_with_types_var')) == type(out_value)

    @mark.parametrize('in_value, types', [
        ((1, 2), (float)),
        ([1, 4, 2.1, 'a'], (int, str)),
    ])
    def test_tuple_with_types_errors(
        self,
        validation_obj: ClassWithValidation,
        in_value: Any,
        types: tuple[type]
    ) -> None:
        def validate_tuple_with_types_var(value: Any) -> tuple:
            return ValidationClass.validateTuple(value, types)
        validation_obj.validate_tuple_with_types_var = validate_tuple_with_types_var
        with raises(TypeError):
            validation_obj.tuple_with_types_var = in_value

    @mark.parametrize('in_value, out_value', [
        ((1, 2), [1, 2]),
        ([1, 2], [1, 2]),
        ('abc', ['a', 'b', 'c']),
    ])
    def test_list(
        self,
        validation_obj: ClassWithValidation,
        in_value: Any,
        out_value: list
    ) -> None:
        validation_obj.list_var = in_value
        assert validation_obj.list_var == out_value
        assert type(validation_obj.list_var) == type(out_value)

    @mark.parametrize('in_value', [
        5,
        None,
    ])
    def test_list_errors(
        self,
        validation_obj: ClassWithValidation,
        in_value: Any
    ) -> None:
        with raises(TypeError):
            validation_obj.list_var = in_value

    @mark.parametrize('in_value, types, out_value', [
        ((1, 2), (int), [1, 2]),
        ([1, 4, 2.1, 'a'], (int, float, str), [1, 4, 2.1, 'a']),
    ])
    def test_list_with_types(
        self,
        validation_obj: ClassWithValidation,
        in_value: Any,
        types: tuple[type],
        out_value: list
    ) -> None:
        def validate_list_with_types_var(value: Any) -> list:
            return ValidationClass.validateList(value, types)
        validation_obj.validate_list_with_types_var = validate_list_with_types_var
        validation_obj.list_with_types_var = in_value
        assert getattr(validation_obj, 'list_with_types_var') == out_value
        assert type(getattr(validation_obj, 'list_with_types_var')) == type(out_value)

    @mark.parametrize('in_value, types', [
        ((1, 2), (float)),
        ([1, 4, 2.1, 'a'], (int, str)),
    ])
    def test_list_with_types_errors(
        self,
        validation_obj: ClassWithValidation,
        in_value: Any,
        types: tuple[type]
    ) -> None:
        def validate_list_with_types_var(value: Any) -> list:
            return ValidationClass.validateList(value, types)
        validation_obj.validate_list_with_types_var = validate_list_with_types_var
        with raises(TypeError):
            validation_obj.list_with_types_var = in_value

    @mark.parametrize('in_value, out_value', [
        ({'a': 1, 'b': 2}, {'a': 1, 'b': 2}),
        ([('a', 1), ('b', 2)], {'a': 1, 'b': 2}),
        ((('a', 1), ('b', 2)), {'a': 1, 'b': 2})
    ])
    def test_dict(
        self,
        validation_obj: ClassWithValidation,
        in_value: Any,
        out_value: dict
    ) -> None:
        validation_obj.dict_var = in_value
        assert validation_obj.dict_var == out_value
        assert type(validation_obj.dict_var) == type(out_value)

    @mark.parametrize('in_value', [
        5,
        None,
        (1, 'a'),
        'abcd'
    ])
    def test_dict_errors(
        self,
        validation_obj: ClassWithValidation,
        in_value: Any
    ) -> None:
        with raises(TypeError):
            validation_obj.dict_var = in_value

    @mark.parametrize('in_value, types, out_value', [
        ({'a': 1, 'b': 2}, ((str), (int)), {'a': 1, 'b': 2}),
        ({'a': 1.2, 'b': 2}, ((str), (int, float)), {'a': 1.2, 'b': 2}),
        ([('a', 'a'), ('b', 2)], ((str), (int, str)), {'a': 'a', 'b': 2}),
        ({1: 1, 2: 2}, ((int), (int)), {1: 1, 2: 2}),
        ({1: 1.2, 'b': 2}, ((str, int), (int, float)), {1: 1.2, 'b': 2}),
    ])
    def test_dict_with_types(
        self,
        validation_obj: ClassWithValidation,
        in_value: Any,
        types: Iterable,
        out_value: dict
    ) -> None:
        def validate_dict_with_types_var(value: Any) -> dict:
            return ValidationClass.validateDict(value, types)
        validation_obj.validate_dict_with_types_var = validate_dict_with_types_var
        validation_obj.dict_with_types_var = in_value
        assert getattr(validation_obj, 'dict_with_types_var') == out_value
        assert type(getattr(validation_obj, 'dict_with_types_var')) == type(out_value)

    @mark.parametrize('in_value, types', [
        ({'a': 1.2, 'b': 2}, ((str), (int))),
        ([('a', 'a'), ('b', 2)], ((str), (str))),
        ({1: 1, 'b': 2}, ((str), (int))),
    ])
    def test_dict_with_types_errors(
        self,
        validation_obj: ClassWithValidation,
        in_value: Any,
        types: Iterable
    ) -> None:
        def validate_dict_with_types_var(value: Any) -> dict:
            return ValidationClass.validateDict(value, types)
        validation_obj.validate_dict_with_types_var = validate_dict_with_types_var
        with raises(TypeError):
            validation_obj.dict_with_types_var = in_value
