from contextlib import contextmanager
from contextvars import ContextVar
from logging import Logger, getLogger
from typing import Any, Generator

from contextual_logger.filters import FilterWithContextVar

# NOTE: ContextVar should be created at the top module level.
__global_context_var: ContextVar[dict[str, Any]] = ContextVar("global_context", default={})


def init_global_context(*loggers: Logger):
    loggers_to_process = list(loggers) or [getLogger()]
    filter_with_context = FilterWithContextVar(__global_context_var)
    for logger in loggers_to_process:
        for handler in logger.handlers:
            handler.addFilter(filter_with_context)


def shutdown_global_context(*loggers: Logger):
    loggers_to_process = list(loggers) or [getLogger()]
    for logger in loggers_to_process:
        for handler in logger.handlers:
            for filter_ in handler.filters:
                if not isinstance(filter_, FilterWithContextVar):
                    continue
                handler.removeFilter(filter_)


@contextmanager
def add_global_context(context: dict[str, Any]) -> Generator[None, None, None]:
    token = __global_context_var.set(__global_context_var.get() | context)
    try:
        yield
    finally:
        __global_context_var.reset(token)
