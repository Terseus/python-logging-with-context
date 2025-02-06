"""
Module with routines to work with the global context.

This is the expected main entrypoint for users so let's try to keep it friendly to use
and as simple as possible, but not simpler.
"""

from contextlib import contextmanager
from contextvars import ContextVar
from logging import Logger, getLogger
from typing import Any, Generator, Optional, Sequence

from logging_with_context.filters import FilterWithContextVar

# NOTE: ContextVar should be created at the top module level.
__global_context_var: ContextVar[dict[str, Any]] = ContextVar(
    "global_context", default={}
)
__global_context_initialized: ContextVar[bool] = ContextVar(
    "global_context_initialized", default=False
)


def _get_loggers_to_process(loggers: Optional[Sequence[Logger]] = None) -> list[Logger]:
    return [getLogger()] if loggers is None else list(loggers)


def init_global_context(loggers: Optional[Sequence[Logger]] = None) -> None:
    """
    Initialize the application global context in the given loggers.

    Parameters:
        loggers: The loggers to attach the global context; if not loggers are specified
            it will use the root logger.
    """
    __global_context_initialized.set(True)
    filter_with_context = FilterWithContextVar(__global_context_var)
    for logger in _get_loggers_to_process(loggers):
        for handler in logger.handlers:
            handler.addFilter(filter_with_context)


def shutdown_global_context(loggers: Optional[Sequence[Logger]] = None) -> None:
    """
    Shutdown the application global context in the given loggers.

    Parameters:
        loggers: The loggers that were used when calling `init_global_context`; by
            default the root logger.
    """
    __global_context_initialized.set(False)
    for logger in _get_loggers_to_process(loggers):
        for handler in logger.handlers:
            for filter_ in handler.filters:
                if not isinstance(filter_, FilterWithContextVar):
                    continue
                handler.removeFilter(filter_)


@contextmanager
def global_context_initialized(
    loggers: Optional[Sequence[Logger]] = None,
) -> Generator[None, None, None]:
    """
    Initiliaze the global context and manages its shutdown.

    Parameters:
        loggers: The loggers to attach the global context; if not loggers are specified
            it will use the root logger.

    Returns:
        A context manager with the global context initialized.
    """
    init_global_context(loggers)
    try:
        yield
    finally:
        shutdown_global_context(loggers)


@contextmanager
def add_global_context(
    context: dict[str, Any], *, auto_init: bool = True
) -> Generator[None, None, None]:
    """
    Add values to the global context to be attached to all the log messages.

    The values will be removed from the global context once the context manager exists.

    Parameters:
        context: A key/value mapping with the values to add to the global context.
        auto_init: Indicate if the global context should be automatically initialized
            if it isn't.

            If `True`, the context will be also automatically shutdown before exiting.

            If the global context is already initialized it'll do nothing.

            Keyword-only argument.

    Returns:
        A context manager that manages the life of the values.
    """
    auto_initialized = False
    if not __global_context_initialized.get() and auto_init:
        init_global_context()
        auto_initialized = True
    token = __global_context_var.set(__global_context_var.get() | context)
    try:
        yield
    finally:
        __global_context_var.reset(token)
        if auto_initialized:
            shutdown_global_context()
