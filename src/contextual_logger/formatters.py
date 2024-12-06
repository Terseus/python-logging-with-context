from collections import defaultdict
from logging import Formatter, LogRecord
from typing import Any, Callable, Dict, Optional, Set, Type, TypeVar

T = TypeVar("T")
ValueSerializerMap = Dict[Type[T], Callable[[T], str]]


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
        str: lambda value: f'"{value}"',
        type(None): lambda _: "<None>",
        float: lambda value: f"{value:.5f}",
    }

    def __init__(
        self,
        *args,
        serializers: Optional[ValueSerializerMap] = None,
        default_serializer: Callable[[Any], str] = str,
        parent: Optional[Formatter] = None,
        **kwargs,
    ):
        super().__init__(*args, **kwargs)
        if serializers is None:
            serializers = {}
        serializers = self._DEFAULT_SERIALIZERS | serializers
        self._serializers = defaultdict(lambda: default_serializer) | serializers
        self._parent = parent

    def _serialize_value(self, value: Any) -> str:
        serializer = self._serializers[type(value)]
        return serializer(value)

    def format(self, record: LogRecord) -> str:
        extras = set(record.__dict__.keys()) - self._LOG_RECORD_ATTRIBUTES
        message = super().format(record)
        if self._parent:
            message = self._parent.format(record)
        if not extras:
            return message

        extras_msg = "|".join(
            f"{name}={self._serialize_value(getattr(record, name))}"
            for name in sorted(extras)
        )
        return f"{message} |{extras_msg}|"
