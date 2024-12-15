from contextvars import ContextVar
from logging import Filter, LogRecord
from typing import Any


class FilterWithContextVar(Filter):
    _context_var: ContextVar[dict[str, Any]]

    def __init__(self, context_var: ContextVar[dict[str, Any]]) -> None:
        self._context_var = context_var

    def filter(self, record: LogRecord) -> bool:
        for key, value in self._context_var.get().items():
            setattr(record, key, value)
        return True
