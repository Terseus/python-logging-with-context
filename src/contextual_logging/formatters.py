"""
Implementations of `logging.Formatter`
"""

from collections import defaultdict
from logging import Formatter, LogRecord
from typing import Any, Callable, Dict, Optional, Set, Type, TypeVar

T = TypeVar("T")
ValueSerializerMap = Dict[Type[T], Callable[[T], str]]


class ExtraTextFormatter(Formatter):
    """
    A formatter meant to be used when printing to stderr/stdout.

    It prints the `extra` keys of every message with the machine-friendly format:
        message |key_1|value_1|key_2|value_2|

    """

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
        default_serializer: Callable[[Any], str] = repr,
        parent: Optional[Formatter] = None,
        **kwargs,
    ):
        """
        Constructor.

        Parameters:
            serializers: A map of serializer functions that takes a value of a specific
                type and return its string representation as an `extra` value.
                The default serializers support the following types:
                - `str`: Returns its value inside double quotes.
                - `None`: Returns `"<None>"`.
                - `float`: Returns its representation with a limit of 5 decimal digits.
            default_serializer: The serializer to use in case the type doesn't have a
                match in `serializers`.
                By default it uses `repr`.
            parent: A parent formatter to decorate.
                Use this if you're modifying an already existing handler at runtime and
                don't want to lose the format in its formatter.
                For example:

                    >>> import logging
                    >>> from contextual_logging.formatters import ExtraTextFormatter
                    >>> logging.basicConfig(level=logging.INFO)
                    >>> for handler in logging.getLogger().handlers:
                    >>>     handler.setFormatter(ExtraTextFormatter(
                    ...        parent=handler.formatter
                    ...     ))
        """
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
        """
        Format the record, adding the `extra` keys in a machine-friendly format.
        """
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
