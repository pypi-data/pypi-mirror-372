import time
from functools import wraps
from typing import Any, Callable, Optional, TypeVar, Union, cast, overload

from .logs import MyLogger

my_logger: MyLogger = MyLogger(
    __name__,
    file_path= 'PyUtils.log'
)

F = TypeVar('F', bound= Callable[..., Any])

@overload
def time_me(_func: F) -> F: ...

@overload
def time_me(*, debug: bool = True) -> Callable[[F], F]: ...

def time_me(
    _func: Optional[F] = None,
    *,
    debug: bool = True
) -> Union[Callable[[F], F], F]:
    def decorator(func: F) -> F:
        @wraps(func)
        def wrapper(*args: Any, **kwargs: Any) -> Any:
            start: float = time.time()
            result: Any = func(*args, **kwargs)
            end: float = time.time()
            if debug:
                my_logger.debug(f'"{func.__name__}" execution time: {end - start:.4f}s.')
            return result
        return cast(F, wrapper)
    if _func is None:
        return decorator
    return decorator(_func)
