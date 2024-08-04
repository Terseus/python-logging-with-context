from logging import LoggerAdapter
from typing import Any, MutableMapping, Tuple


class ContextualAdapter(LoggerAdapter):
    def process(
        self, msg: str, kwargs: MutableMapping[str, Any]
    ) -> Tuple[str, MutableMapping[str, Any]]:
        kwargs["extra"] = (self.extra or {}) | (kwargs.get("extra", {}))  # type: ignore
        return (msg, kwargs)
