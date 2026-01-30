"""Tests for Reticulum integration (serialization only — no RNS required)."""

import json

from hfprop.models import (
    BandCondition,
    BandForecast,
    GeomagStatus,
    PropagationReport,
    SolarData,
)
from hfprop.reticulum import report_to_json


def _make_report() -> PropagationReport:
    return PropagationReport(
        solar=SolarData(
            solar_flux=129,
            sunspot_number=99,
            a_index=22,
            k_index=2,
            xray="C1.0",
            geomag_field=GeomagStatus.QUIET,
            signal_noise="S1-S2",
        ),
        bands=[
            BandForecast("80m-40m", BandCondition.FAIR, BandCondition.GOOD),
            BandForecast("30m-20m", BandCondition.GOOD, BandCondition.GOOD),
        ],
        source="test",
    )


def test_report_to_json_returns_bytes():
    result = report_to_json(_make_report())
    assert isinstance(result, bytes)


def test_report_to_json_valid_json():
    result = report_to_json(_make_report())
    data = json.loads(result)
    assert "solar" in data
    assert "bands" in data


def test_report_to_json_solar_fields():
    data = json.loads(report_to_json(_make_report()))
    solar = data["solar"]
    assert solar["solar_flux"] == 129
    assert solar["k_index"] == 2
    assert "assessment" in solar


def test_report_to_json_bands():
    data = json.loads(report_to_json(_make_report()))
    assert len(data["bands"]) == 2
    assert data["bands"][0]["name"] == "80m-40m"
    assert data["bands"][0]["day"] == "Fair"
