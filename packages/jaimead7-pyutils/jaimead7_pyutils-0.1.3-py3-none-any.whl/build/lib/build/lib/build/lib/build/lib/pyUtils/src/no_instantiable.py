from .logs import MyLogger

my_logger = MyLogger(
    __name__,
    file_path= 'PyUtils.log'
)

class NoInstantiable:
    """Class that can't be instantiable"""
    def __new__(cls) -> None:
        raise SyntaxError(f'Class "{cls.__name__}" is not instantiable')
