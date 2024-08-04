import logging

from pytest import LogCaptureFixture

from contextual_logger.adapters import ContextualAdapter


def test_contextual_adapter_with_extras_ok(caplog: LogCaptureFixture):
    instance = ContextualAdapter(logging.getLogger(), context={"extra1": "value1"})
    with caplog.at_level(logging.INFO):
        instance.info("Message", extra={"extra2": "value2"})
    assert len(caplog.records) == 1
    result = caplog.records[0]
    assert result.extra1 == "value1"  # type: ignore
    assert result.extra2 == "value2"  # type: ignore


def test_contextual_adapter_with_context_ok(caplog: LogCaptureFixture):
    instance = ContextualAdapter(logging.getLogger())
    with instance.context({"extra1": "value1"}) as child:
        with caplog.at_level(logging.INFO):
            child.info("Message from child")
            instance.info("Message from parent")
    assert len(caplog.records) == 2
    result_child, result_parent = tuple(caplog.records)
    assert result_child.message == "Message from child"
    assert result_child.extra1 == "value1"  # type: ignore
    assert result_parent.message == "Message from parent"
    assert not hasattr(result_parent, "extra1")


def test_contextual_adapter_with_context_multiple_ok(caplog: LogCaptureFixture):
    instance = ContextualAdapter(logging.getLogger())
    with instance.context({"extra1": "value1"}) as child_1:
        with child_1.context({"extra2": "value2"}) as child_2:
            with caplog.at_level(logging.INFO):
                child_1.info("Message from child 1")
                child_2.info("Message from child 2")
    assert len(caplog.records) == 2
    result_child_1, result_child_2 = tuple(caplog.records)
    assert result_child_1.message == "Message from child 1"
    assert result_child_1.extra1 == "value1"  # type: ignore
    assert result_child_2.message == "Message from child 2"
    assert result_child_2.extra1 == "value1"  # type: ignore
    assert result_child_2.extra2 == "value2"  # type: ignore


def test_contextual_adapter_with_context_override_ok(caplog: LogCaptureFixture):
    instance = ContextualAdapter(logging.getLogger())
    with instance.context({"extra1": "value1"}) as child_1:
        with child_1.context({"extra1": "value2"}) as child_2:
            with caplog.at_level(logging.INFO):
                child_1.info("Message from child 1")
                child_2.info("Message from child 2")
    assert len(caplog.records) == 2
    result_child_1, result_child_2 = tuple(caplog.records)
    assert result_child_1.message == "Message from child 1"
    assert result_child_1.extra1 == "value1"  # type: ignore
    assert result_child_2.message == "Message from child 2"
    assert result_child_2.extra1 == "value2"  # type: ignore
