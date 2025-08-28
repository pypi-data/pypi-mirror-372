import re
from typing import Any, ClassVar, Dict, List, Optional

from pyramid.config import Configurator

from pyramid_kvs2.typing import AnyValue

from . import kvs


class MockCache(kvs.KVS):
    cached_data: ClassVar[Dict[bytes, AnyValue]] = {}
    last_ttl: Optional[int] = None

    def _create_client(self, **kwargs: Any) -> Any:
        return self

    def delete(self, key: str) -> None:
        self.cached_data.pop(self._get_key(key), None)

    def raw_get(self, key: str, default: Optional[AnyValue] = None) -> AnyValue:
        return self.cached_data.get(self._get_key(key), default)

    def raw_set(self, key: str, value: AnyValue, ttl: int) -> None:
        self.cached_data[self._get_key(key)] = value
        MockCache.last_ttl = ttl

    def incr(self, key: str) -> int:
        value = int(self.cached_data[self._get_key(key)])
        value += 1
        self.cached_data[self._get_key(key)] = str(value)
        return value

    def get_keys(self, pattern: str = "*") -> List[str]:
        prefix = self.key_prefix.decode("utf-8")
        pattern = re.escape(self._get_key(pattern).decode("utf-8")).replace(r"\*", ".*")
        matching = re.compile(f"^{pattern}$")
        return [
            key.replace(prefix, "")
            for key in [encoded.decode("utf-8") for encoded in self.cached_data.keys()]
            if matching.match(key)
        ]


def includeme(config: Configurator) -> None:
    kvs.register("mock", MockCache)
    config.include("pyramid_kvs2")
