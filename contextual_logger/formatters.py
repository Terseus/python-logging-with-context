from logging import Formatter, LogRecord
from typing import Set


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

    def format(self, record: LogRecord) -> str:
        extras = set(record.__dict__.keys()) - self._LOG_RECORD_ATTRIBUTES
        message = super().format(record)
        if not extras:
            return message

        extras_msg = ", ".join(f'{name}="{getattr(record, name)}"' for name in extras)
        return f"{message}; {extras_msg}"
