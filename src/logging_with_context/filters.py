"""
Implementations of `logging.Filter`.
"""

from contextvars import ContextVar
from logging import Filter, LogRecord
from typing import Any


class FilterWithContextVar(Filter):
    """
    Add the values from the current context to all the log messages as `extra` keys.

    This class is not meant to be used directly, instead it's used by the
    `global_context` module.
    """

    _context_var: ContextVar[dict[str, Any]]

    def __init__(self, context_var: ContextVar[dict[str, Any]]) -> None:
        """
        Constructor.

        Parameters:
            context_var: The context storage to use.
        """
        self._context_var = context_var

    def filter(self, record: LogRecord) -> bool:
        """
        Add the context values to the log message.

        Returns:
            Always returns `True`.
        """
        for key, value in self._context_var.get().items():
            setattr(record, key, value)
        return True
