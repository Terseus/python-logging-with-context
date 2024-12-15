import logging

import pytest

from contextual_logging.global_context import (
    add_global_context,
    init_global_context,
    shutdown_global_context,
)


@pytest.fixture(autouse=True)
def shutdown_global_context_on_end():
    yield
    shutdown_global_context()


def test_add_global_context_ok(caplog: pytest.LogCaptureFixture):
    logger = logging.getLogger(__name__)
    init_global_context()
    with add_global_context({"key": "value"}):
        with caplog.at_level(logging.INFO):
            logger.info("Test message")
    assert len(caplog.records) == 1
    result = caplog.records[0]
    assert result.key == "value"  # type: ignore


def test_add_global_context_without_init_ignored_ok(caplog: pytest.LogCaptureFixture):
    logger = logging.getLogger(__name__)
    with add_global_context({"key": "value"}):
        with caplog.at_level(logging.INFO):
            logger.info("Test message")
    assert len(caplog.records) == 1
    result = caplog.records[0]
    assert not hasattr(result, "key")


def test_add_global_context_after_shutdown_ignored_ok(caplog: pytest.LogCaptureFixture):
    logger = logging.getLogger(__name__)
    init_global_context()
    shutdown_global_context()
    with add_global_context({"key": "value"}):
        with caplog.at_level(logging.INFO):
            logger.info("Test message")
    assert len(caplog.records) == 1
    result = caplog.records[0]
    assert not hasattr(result, "key")
