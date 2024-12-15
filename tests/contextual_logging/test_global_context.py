import logging

import pytest

from contextual_logging.global_context import (
    add_global_context,
    global_context_initialized,
)


def test_add_global_context_ok(caplog: pytest.LogCaptureFixture):
    logger = logging.getLogger(__name__)
    with (
        global_context_initialized(),
        add_global_context({"key": "value"}),
        caplog.at_level(logging.INFO),
    ):
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
    with global_context_initialized():
        pass
    with add_global_context({"key": "value"}), caplog.at_level(logging.INFO):
        logger.info("Test message")
    assert len(caplog.records) == 1
    result = caplog.records[0]
    assert not hasattr(result, "key")
