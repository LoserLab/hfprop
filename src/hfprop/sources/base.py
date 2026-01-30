"""Abstract base class for data sources."""

from abc import ABC, abstractmethod
from typing import Any


class DataSource(ABC):
    @property
    @abstractmethod
    def name(self) -> str:
        ...

    @property
    @abstractmethod
    def cache_key(self) -> str:
        ...

    @property
    @abstractmethod
    def cache_ttl_seconds(self) -> int:
        ...

    @abstractmethod
    def fetch_raw(self) -> bytes:
        ...

    @abstractmethod
    def parse(self, raw_data: bytes) -> Any:
        ...
