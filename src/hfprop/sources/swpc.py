"""NOAA Space Weather Prediction Center JSON APIs.

Provides more frequent K-index and solar flux updates.
No documented rate limits. Public domain US government data.
"""

import json as _json
from urllib.request import Request, urlopen

from hfprop.config import (
    HTTP_TIMEOUT,
    SWPC_CACHE_TTL,
    SWPC_FLUX_URL,
    SWPC_KINDEX_URL,
    USER_AGENT,
)
from hfprop.sources.base import DataSource


class SWPCKIndexSource(DataSource):
    name = "NOAA SWPC Planetary K-Index"
    cache_key = "swpc_kindex"
    cache_ttl_seconds = SWPC_CACHE_TTL

    def fetch_raw(self) -> bytes:
        req = Request(SWPC_KINDEX_URL, headers={"User-Agent": USER_AGENT})
        with urlopen(req, timeout=HTTP_TIMEOUT) as resp:
            return resp.read()

    def parse(self, raw_data: bytes) -> dict:
        """Returns the most recent K-index entry."""
        entries = _json.loads(raw_data)
        if not entries:
            return {}
        latest = entries[-1]
        return {
            "time_tag": latest.get("time_tag", ""),
            "kp_index": latest.get("kp_index", 0),
            "estimated_kp": latest.get("estimated_kp", 0.0),
        }


class SWPCFluxSource(DataSource):
    name = "NOAA SWPC Solar Flux"
    cache_key = "swpc_flux"
    cache_ttl_seconds = SWPC_CACHE_TTL

    def fetch_raw(self) -> bytes:
        req = Request(SWPC_FLUX_URL, headers={"User-Agent": USER_AGENT})
        with urlopen(req, timeout=HTTP_TIMEOUT) as resp:
            return resp.read()

    def parse(self, raw_data: bytes) -> dict:
        """Returns the most recent solar flux entry."""
        entries = _json.loads(raw_data)
        if not entries:
            return {}
        latest = entries[-1]
        return {
            "time_tag": latest.get("time_tag", ""),
            "flux": latest.get("flux", 0.0),
        }
