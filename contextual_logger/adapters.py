from contextlib import contextmanager
from logging import Logger, LoggerAdapter
from typing import Any, Generator, Mapping, MutableMapping, Optional, Tuple


class ContextualAdapter(LoggerAdapter):
    def __init__(self, logger: Logger, context: Optional[MutableMapping[str, object]] = None):
        super().__init__(logger, context or {})

    def process(
        self, msg: str, kwargs: MutableMapping[str, Any]
    ) -> Tuple[str, MutableMapping[str, Any]]:
        kwargs["extra"] = self.extra | (kwargs.get("extra", {}))  # type: ignore
        return (msg, kwargs)

    @contextmanager
    def context(self, context: Mapping[str, Any]) -> Generator["ContextualAdapter", None, None]:
        yield type(self)(logger=self.logger, context=self.extra | context)  # type: ignore
