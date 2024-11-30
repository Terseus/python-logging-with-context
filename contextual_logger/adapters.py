from contextlib import contextmanager
from logging import Logger, LoggerAdapter
from typing import Any, Dict, Generator, MutableMapping, Optional, Tuple


class ContextualAdapter(LoggerAdapter):
    # NOTE: Override the type because Mapping doesn't support union operator
    extra: Dict[str, object]  # type: ignore[override]

    def __init__(
        self, logger: Logger, context: Optional[MutableMapping[str, object]] = None
    ) -> None:
        super().__init__(logger, context or {})

    def process(
        self, msg: str, kwargs: MutableMapping[str, Any]
    ) -> Tuple[str, MutableMapping[str, Any]]:
        kwargs["extra"] = self.extra | kwargs.get("extra", {})
        return (msg, kwargs)

    @contextmanager
    def context(self, context: Dict[str, Any]) -> Generator["ContextualAdapter", None, None]:
        yield type(self)(logger=self.logger, context=self.extra | context)
