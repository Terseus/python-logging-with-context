import logging
import math
from dataclasses import dataclass
from typing import Callable, Generator

import pytest
from pytest import LogCaptureFixture

from logging_with_context.formatters import ExtraTextFormatter

CaplogFactory = Callable[[logging.Formatter], LogCaptureFixture]


@dataclass
class MyValue:
    name: str
    value: str


def _my_value_serializer(value: MyValue) -> str:
    return f"MyValue({value.name}={value.value})"


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
        logger.info(
            "Testing",
            extra={"key1": "value", "key2": 100, "key3": None, "key4": math.pi},
        )
    expected = 'Testing |key1="value"|key2=100|key3=<None>|key4=3.14159|\n'
    assert caplog.text == expected


def test_extra_text_formatter_custom_serializer_ok(caplog_factory: CaplogFactory):
    caplog = caplog_factory(
        ExtraTextFormatter(
            fmt="%(message)s", serializers={MyValue: _my_value_serializer}
        )
    )
    logger = logging.getLogger(__name__)
    with caplog.at_level(logging.INFO):
        logger.info(
            "Testing", extra={"key1": "value1", "key2": MyValue("my_name", "my_value")}
        )
    expected = 'Testing |key1="value1"|key2=MyValue(my_name=my_value)|\n'
    assert caplog.text == expected


def test_extra_text_formatter_default_serializer_ok(caplog_factory: CaplogFactory):
    caplog = caplog_factory(
        ExtraTextFormatter(fmt="%(message)s", default_serializer=_my_value_serializer)
    )
    logger = logging.getLogger(__name__)
    with caplog.at_level(logging.INFO):
        logger.info(
            "Testing", extra={"key1": "value1", "key2": MyValue("my_name", "my_value")}
        )
    expected = 'Testing |key1="value1"|key2=MyValue(my_name=my_value)|\n'
    assert caplog.text == expected


def test_extra_text_formatter_override_default_serializer_ok(
    caplog_factory: CaplogFactory,
):
    caplog = caplog_factory(
        ExtraTextFormatter(
            fmt="%(message)s", serializers={float: lambda value: f"{value:.3f}"}
        )
    )
    logger = logging.getLogger(__name__)
    with caplog.at_level(logging.INFO):
        logger.info("Testing", extra={"key1": math.pi})
    expected = "Testing |key1=3.142|\n"
    assert caplog.text == expected


def test_extra_text_formatter_with_parent_ok(caplog_factory: CaplogFactory):
    caplog = caplog_factory(
        ExtraTextFormatter(
            fmt="%(message)s", parent=logging.Formatter(fmt="%(message)s - from parent")
        )
    )
    logger = logging.getLogger(__name__)
    with caplog.at_level(logging.INFO):
        logger.info("Testing", extra={"key": "value"})
    expected = 'Testing - from parent |key="value"|\n'
    assert caplog.text == expected
