"""Tests for watch mode change detection."""

from hfprop.commands.watch import _diff_reports
from hfprop.models import (
    BandCondition,
    BandForecast,
    GeomagStatus,
    PropagationReport,
    SolarData,
)


def _make_report(**kwargs) -> PropagationReport:
    defaults = dict(
        solar_flux=129,
        sunspot_number=99,
        a_index=22,
        k_index=2,
        xray="C1.0",
        geomag_field=GeomagStatus.QUIET,
        signal_noise="S1-S2",
    )
    defaults.update(kwargs)
    return PropagationReport(
        solar=SolarData(**defaults),
        bands=[
            BandForecast("80m-40m", BandCondition.FAIR, BandCondition.GOOD),
            BandForecast("30m-20m", BandCondition.GOOD, BandCondition.GOOD),
        ],
        source="test",
    )


def test_diff_no_changes():
    r = _make_report()
    changes = _diff_reports(r, r)
    assert changes == []


def test_diff_k_index_changed():
    old = _make_report(k_index=2)
    new = _make_report(k_index=4)
    changes = _diff_reports(old, new)
    assert any("K-index" in c for c in changes)


def test_diff_sfi_changed():
    old = _make_report(solar_flux=100)
    new = _make_report(solar_flux=150)
    changes = _diff_reports(old, new)
    assert any("SFI" in c for c in changes)


def test_diff_geomag_changed():
    old = _make_report(geomag_field=GeomagStatus.QUIET)
    new = _make_report(geomag_field=GeomagStatus.STORM)
    changes = _diff_reports(old, new)
    assert any("Geomag" in c for c in changes)


def test_diff_band_day_changed():
    old = _make_report()
    new = PropagationReport(
        solar=SolarData(
            solar_flux=129, sunspot_number=99, a_index=22, k_index=2,
            xray="C1.0", geomag_field=GeomagStatus.QUIET, signal_noise="S1-S2",
        ),
        bands=[
            BandForecast("80m-40m", BandCondition.POOR, BandCondition.GOOD),
            BandForecast("30m-20m", BandCondition.GOOD, BandCondition.GOOD),
        ],
        source="test",
    )
    changes = _diff_reports(old, new)
    assert any("80m-40m day" in c for c in changes)


def test_diff_multiple_changes():
    old = _make_report(k_index=2, solar_flux=100)
    new = _make_report(k_index=5, solar_flux=150)
    changes = _diff_reports(old, new)
    assert len(changes) >= 2
