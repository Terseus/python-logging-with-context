"""
Implementations of `logging.LoggerAdapter`.
"""

from contextlib import contextmanager
from logging import Logger, LoggerAdapter
from typing import Any, Generator, MutableMapping, Optional, Tuple


class ContextualAdapter(LoggerAdapter):
    """
    A `logging.LoggerAdapter` that can manage its own independent context.

    Use this if you want to add context only to a given logger.

    Example usage:

        Set up everything

        >>> import logging
        >>> from contextual_logging.adapters import ContextualAdapter
        >>> from contextual_logging.formatters import ExtraTextFormatter
        >>> logging.basicConfig(level=logging.INFO)
        >>> root = logging.getLogger()

        To be able to see the context in the interpreter.

        >>> root.handlers[0].setFormatter(
        ...     ExtraTextFormatter(parent=root.handlers[0].formatter)
        ... )

        Using the adapter

        >>> adapter = ContextualAdapter(root)
        >>> with adapter.context({"key": "value"}) as logger:
        ...     logger.info("This contains context")
        ...     root.info("This does not")
        INFO:root:This contains context |key="value"|
        INFO:root:This does not
    """

    # NOTE: Override the type because Mapping doesn't support union operator
    extra: dict[str, object]  # type: ignore[override]

    def __init__(
        self, logger: Logger, context: Optional[MutableMapping[str, object]] = None
    ) -> None:
        """
        Constructor:

        Parameters:
            logger: The logger to decorate with this adapter.
            context: The initial context; by default an empty context will be used.
        """
        super().__init__(logger, context or {})

    def process(
        self, msg: str, kwargs: MutableMapping[str, Any]
    ) -> Tuple[str, MutableMapping[str, Any]]:
        """
        Merges the message `extra` keys with the context, giving preference to the
        context.
        """
        kwargs["extra"] = self.extra | kwargs.get("extra", {})
        return (msg, kwargs)

    @contextmanager
    def context(
        self, context: dict[str, Any]
    ) -> Generator["ContextualAdapter", None, None]:
        """
        Creates a copy of itself with new context added, managed by a context manager.

        Parameters:
            context: The context to add.

        Returns:
            A context manager that yields an `ContextualAdapter` with the new context
                merged that will live as long as the context manager.
        """
        yield type(self)(logger=self.logger, context=self.extra | context)
