import logging
import re

from pytest import LogCaptureFixture, fixture, mark

from ..src.logs import MyLogger
from ..src.timing import time_me

LOGGER_NAME = 'TestLogger'

@fixture(autouse= True)
def set_caplog_lvl(caplog: LogCaptureFixture) -> None:
    caplog.set_level(logging.DEBUG)
    caplog.clear()


class TestTiming:
    def test_timing_normal(self, caplog: LogCaptureFixture) -> None:
        @time_me
        def test_func() -> None:
            [_ for _ in range(90000)]
        test_func()
        record: logging.LogRecord = caplog.records[0]
        assert record.levelno == logging.DEBUG
        print(record.message)
        assert bool(re.fullmatch(r'.* execution time: .*s\.$', record.message))

    def test_timing_called(self, caplog: LogCaptureFixture) -> None:
        @time_me()
        def test_func() -> None:
            [_ for _ in range(90000)]
        test_func()
        record: logging.LogRecord = caplog.records[0]
        assert record.levelno == logging.DEBUG
        print(record.message)
        assert bool(re.fullmatch(r'.* execution time: .*s\.$', record.message))

    def test_timing_muted(self, caplog: LogCaptureFixture) -> None:
        @time_me(debug= False)
        def test_func() -> None:
            [_ for _ in range(90000)]
        test_func()
        assert len(caplog.records) == 0
