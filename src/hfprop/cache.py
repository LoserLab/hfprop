"""File-based cache with TTL for API responses.

Cache directory: ~/.cache/hfprop/ (XDG_CACHE_HOME compliant)
Files are JSON: {"fetched_at": ISO timestamp, "data": base64-encoded bytes}
"""

import base64
import json
import os
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional, Tuple


def get_cache_dir() -> Path:
    xdg = os.environ.get("XDG_CACHE_HOME")
    base = Path(xdg) if xdg else Path.home() / ".cache"
    cache_dir = base / "hfprop"
    cache_dir.mkdir(parents=True, exist_ok=True)
    return cache_dir


class FileCache:
    def __init__(self, cache_dir: Optional[Path] = None):
        self.cache_dir = cache_dir or get_cache_dir()

    def _path(self, key: str) -> Path:
        return self.cache_dir / f"{key}.cache"

    def get(self, key: str, max_age_seconds: int) -> Optional[bytes]:
        """Return cached data if fresh enough, None otherwise."""
        entry = self._read_entry(key)
        if entry is None:
            return None
        fetched_at, data = entry
        age = (datetime.now(timezone.utc) - fetched_at).total_seconds()
        if age > max_age_seconds:
            return None
        return data

    def get_stale(self, key: str) -> Optional[Tuple[bytes, datetime]]:
        """Return cached data regardless of age. For offline mode."""
        entry = self._read_entry(key)
        if entry is None:
            return None
        return entry[1], entry[0]

    def put(self, key: str, data: bytes) -> None:
        """Store data with current timestamp."""
        entry = {
            "fetched_at": datetime.now(timezone.utc).isoformat(),
            "data": base64.b64encode(data).decode("ascii"),
        }
        self._path(key).write_text(json.dumps(entry))

    def _read_entry(self, key: str) -> Optional[Tuple[datetime, bytes]]:
        path = self._path(key)
        if not path.exists():
            return None
        try:
            entry = json.loads(path.read_text())
            fetched_at = datetime.fromisoformat(entry["fetched_at"])
            if fetched_at.tzinfo is None:
                fetched_at = fetched_at.replace(tzinfo=timezone.utc)
            data = base64.b64decode(entry["data"])
            return fetched_at, data
        except (json.JSONDecodeError, KeyError, ValueError):
            return None
