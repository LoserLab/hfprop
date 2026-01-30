"""Tests for NOAA SWPC JSON parsers."""

from hfprop.sources.swpc import SWPCFluxSource, SWPCKIndexSource


def test_kindex_parse_latest(swpc_kindex_json):
    result = SWPCKIndexSource().parse(swpc_kindex_json)
    assert result["kp_index"] == 3
    assert result["time_tag"] == "2026-01-30T01:01:00"


def test_kindex_parse_empty():
    result = SWPCKIndexSource().parse(b"[]")
    assert result == {}


def test_flux_parse_latest(swpc_flux_json):
    result = SWPCFluxSource().parse(swpc_flux_json)
    assert result["flux"] == 129.0
    assert result["time_tag"] == "2026-01-29T20:00:00"


def test_flux_parse_empty():
    result = SWPCFluxSource().parse(b"[]")
    assert result == {}
