import logging

from pytest import LogCaptureFixture

from contextual_logger.adapters import ContextualAdapter


def test_contextual_adapter_with_extras_ok(caplog: LogCaptureFixture):
    instance = ContextualAdapter(logging.getLogger(), extra={"extra1": "value1"})
    with caplog.at_level(logging.INFO):
        instance.info("Message", extra={"extra2": "value2"})
    assert len(caplog.records) == 1
    result = caplog.records[0]
    assert result.extra1 == "value1"  # type: ignore
    assert result.extra2 == "value2"  # type: ignore
