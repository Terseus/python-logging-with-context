import logging
import threading

import pytest

from logging_with_context.global_context import (
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


def test_add_global_context_multithread(caplog: pytest.LogCaptureFixture):
    def worker(value: int) -> None:
        with add_global_context({"value": value}):
            logger.info("Message 1 from thread %s", value)
        with add_global_context({"value": value * 10}):
            logger.info("Message 2 from thread %s", value)
        with add_global_context({"value": value * 100}):
            logger.info("Message 3 from thread %s", value)

    logger = logging.getLogger(__name__)
    with global_context_initialized(), caplog.at_level(logging.INFO):
        worker_1 = threading.Thread(target=worker, args=(1,))
        worker_2 = threading.Thread(target=worker, args=(2,))
        worker_1.start()
        worker_2.start()
        worker_1.join()
        worker_2.join()
    assert len(caplog.records) == 6
    result = [
        {"message": record.message, "value": record.value}  # type: ignore
        for record in sorted(caplog.records, key=lambda r: r.value)  # type: ignore
    ]
    expected = [
        {"message": "Message 1 from thread 1", "value": 1},
        {"message": "Message 1 from thread 2", "value": 2},
        {"message": "Message 2 from thread 1", "value": 10},
        {"message": "Message 2 from thread 2", "value": 20},
        {"message": "Message 3 from thread 1", "value": 100},
        {"message": "Message 3 from thread 2", "value": 200},
    ]
    assert result == expected
