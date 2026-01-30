"""Fetch propagation data with caching and offline support."""

import sys
from datetime import datetime, timezone

from hfprop.cache import FileCache
from hfprop.models import PropagationReport
from hfprop.sources.hamqsl import HamQSLSource


def get_report(offline: bool = False) -> PropagationReport:
    """Fetch a PropagationReport, using cache as appropriate.

    Args:
        offline: If True, only use cached data.

    Returns:
        PropagationReport with .cached set accordingly.

    Raises:
        SystemExit: If no data is available.
    """
    cache = FileCache()
    source = HamQSLSource()

    if offline:
        stale = cache.get_stale(source.cache_key)
        if stale is None:
            print(
                "No cached data available. Run once with internet to populate cache.",
                file=sys.stderr,
            )
            sys.exit(1)
        data, fetched_at = stale
        report = source.parse(data)
        report.cached = True
        report.fetched_at = fetched_at
        return report

    # Try fresh cache first
    cached_data = cache.get(source.cache_key, source.cache_ttl_seconds)
    if cached_data is not None:
        report = source.parse(cached_data)
        report.cached = True
        report.fetched_at = datetime.now(timezone.utc)
        return report

    # Fetch live
    try:
        raw = source.fetch_raw()
    except Exception as e:
        # Fall back to stale cache
        stale = cache.get_stale(source.cache_key)
        if stale is not None:
            data, fetched_at = stale
            report = source.parse(data)
            report.cached = True
            report.fetched_at = fetched_at
            print(
                f"Warning: fetch failed ({e}), using cached data.",
                file=sys.stderr,
            )
            return report
        print(f"Error: could not fetch data: {e}", file=sys.stderr)
        sys.exit(1)

    cache.put(source.cache_key, raw)
    report = source.parse(raw)
    report.cached = False
    report.fetched_at = datetime.now(timezone.utc)

    try:
        from hfprop.history import HistoryDB
        HistoryDB().log(report)
    except Exception:
        pass  # Logging failure should never break the CLI

    return report
