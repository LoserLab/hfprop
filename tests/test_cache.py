"""Tests for file-based cache."""

import json
import time

from hfprop.cache import FileCache


def test_put_and_get(tmp_path):
    cache = FileCache(cache_dir=tmp_path)
    cache.put("test", b"hello")
    result = cache.get("test", max_age_seconds=60)
    assert result == b"hello"


def test_get_expired(tmp_path):
    cache = FileCache(cache_dir=tmp_path)
    cache.put("test", b"old data")
    # Backdate the cache entry
    path = tmp_path / "test.cache"
    entry = json.loads(path.read_text())
    entry["fetched_at"] = "2020-01-01T00:00:00+00:00"
    path.write_text(json.dumps(entry))
    result = cache.get("test", max_age_seconds=60)
    assert result is None


def test_get_stale_returns_old_data(tmp_path):
    cache = FileCache(cache_dir=tmp_path)
    cache.put("test", b"stale data")
    # Backdate
    path = tmp_path / "test.cache"
    entry = json.loads(path.read_text())
    entry["fetched_at"] = "2020-01-01T00:00:00+00:00"
    path.write_text(json.dumps(entry))
    result = cache.get_stale("test")
    assert result is not None
    data, fetched_at = result
    assert data == b"stale data"


def test_get_missing_key(tmp_path):
    cache = FileCache(cache_dir=tmp_path)
    assert cache.get("nonexistent", max_age_seconds=60) is None


def test_get_stale_missing_key(tmp_path):
    cache = FileCache(cache_dir=tmp_path)
    assert cache.get_stale("nonexistent") is None


def test_corrupted_cache_file(tmp_path):
    cache = FileCache(cache_dir=tmp_path)
    (tmp_path / "bad.cache").write_text("not json")
    assert cache.get("bad", max_age_seconds=60) is None
    assert cache.get_stale("bad") is None
