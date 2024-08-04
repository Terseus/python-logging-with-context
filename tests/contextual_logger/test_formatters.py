import logging
from typing import Callable, Generator

import pytest
from pytest import LogCaptureFixture

from contextual_logger.formatters import ExtraTextFormatter

CaplogFactory = Callable[[logging.Formatter], LogCaptureFixture]


@pytest.fixture
def caplog_factory(caplog: LogCaptureFixture) -> Generator[CaplogFactory, None, None]:
    def factory(formatter: logging.Formatter) -> LogCaptureFixture:
        caplog.handler.setFormatter(formatter)
        return caplog

    original_formatter = caplog.handler.formatter
    try:
        yield factory
    finally:
        caplog.handler.setFormatter(original_formatter)


def test_extra_text_formatter_ok(caplog_factory: CaplogFactory):
    caplog = caplog_factory(ExtraTextFormatter(fmt="%(message)s"))
    logger = logging.getLogger(__name__)
    with caplog.at_level(logging.INFO):
        logger.info("Testing", extra={"key": "value"})
    expected = 'Testing; key="value"\n'
    assert caplog.text == expected
