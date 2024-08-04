from collections import defaultdict
from logging import Formatter, LogRecord
from typing import Any, Callable, Mapping, Optional, Set, Type, TypeVar

T = TypeVar("T")
ValueSerializerMap = Mapping[Type[T], Callable[[T], str]]


def _str_serializer(value: str) -> str:
    return f'"{value}"'


def _none_serializer(_: None) -> str:
    return "<null>"


def _float_serializer(value: float) -> str:
    return f"{value:.5f}"


class ExtraTextFormatter(Formatter):
    _LOG_RECORD_ATTRIBUTES: Set[str] = {
        "args",
        "asctime",
        "created",
        "exc_info",
        "exc_text",
        "filename",
        "funcName",
        "levelname",
        "levelno",
        "lineno",
        "message",
        "module",
        "msecs",
        "msg",
        "name",
        "pathname",
        "process",
        "processName",
        "relativeCreated",
        "stack_info",
        "taskName",
        "thread",
        "threadName",
    }
    _DEFAULT_SERIALIZERS: ValueSerializerMap = {
        str: _str_serializer,
        type(None): _none_serializer,
        float: _float_serializer,
    }

    def __init__(
        self,
        *args,
        serializers: Optional[ValueSerializerMap] = None,
        default_serializer: Callable[[Any], str] = str,
        **kwargs,
    ):
        super().__init__(*args, **kwargs)
        if serializers is None:
            serializers = {}
        serializers = self._DEFAULT_SERIALIZERS | serializers  # type: ignore
        self._serializers = defaultdict(lambda: default_serializer) | serializers  # type: ignore

    def _serialize_value(self, value: Any) -> str:
        serializer = self._serializers[type(value)]
        return serializer(value)

    def format(self, record: LogRecord) -> str:
        extras = set(record.__dict__.keys()) - self._LOG_RECORD_ATTRIBUTES
        message = super().format(record)
        if not extras:
            return message

        extras_msg = ", ".join(
            f"{name}={self._serialize_value(getattr(record, name))}" for name in sorted(extras)
        )
        return f"{message}; {extras_msg}"
