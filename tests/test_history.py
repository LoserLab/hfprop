"""Tests for SQLite condition history."""

from datetime import datetime, timezone
from pathlib import Path

import pytest

from hfprop.history import HistoryDB
from hfprop.models import (
    BandCondition,
    BandForecast,
    GeomagStatus,
    PropagationReport,
    SolarData,
)


def _make_report(**kwargs) -> PropagationReport:
    solar_defaults = dict(
        solar_flux=129,
        sunspot_number=99,
        a_index=22,
        k_index=2,
        xray="C1.0",
        geomag_field=GeomagStatus.QUIET,
        signal_noise="S1-S2",
    )
    solar_defaults.update(kwargs)
    return PropagationReport(
        solar=SolarData(**solar_defaults),
        bands=[
            BandForecast("80m-40m", BandCondition.FAIR, BandCondition.GOOD),
            BandForecast("30m-20m", BandCondition.GOOD, BandCondition.GOOD),
        ],
        source="test",
    )


def test_log_and_query(tmp_path):
    db = HistoryDB(db_path=tmp_path / "test.db")
    report = _make_report()
    db.log(report)
    entries = db.query(days=1)
    assert len(entries) == 1
    assert entries[0]["sfi"] == 129
    assert entries[0]["k_index"] == 2


def test_query_empty_db(tmp_path):
    db = HistoryDB(db_path=tmp_path / "empty.db")
    entries = db.query(days=7)
    assert entries == []


def test_multiple_logs(tmp_path):
    db = HistoryDB(db_path=tmp_path / "multi.db")
    db.log(_make_report(k_index=2))
    db.log(_make_report(k_index=4))
    entries = db.query(days=1)
    assert len(entries) == 2
    # Newest first
    assert entries[0]["k_index"] == 4


def test_schema_creation(tmp_path):
    db_path = tmp_path / "schema.db"
    db = HistoryDB(db_path=db_path)
    assert db_path.exists()


def test_bands_stored_as_json(tmp_path):
    import json
    db = HistoryDB(db_path=tmp_path / "bands.db")
    db.log(_make_report())
    entries = db.query(days=1)
    bands = json.loads(entries[0]["bands"])
    assert len(bands) == 2
    assert bands[0]["name"] == "80m-40m"
