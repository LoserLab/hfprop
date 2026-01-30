"""Tests for data models."""

from hfprop.models import GeomagStatus, SolarData


def _make_solar(**kwargs) -> SolarData:
    defaults = dict(
        solar_flux=100,
        sunspot_number=80,
        a_index=10,
        k_index=2,
        xray="B1.0",
        geomag_field=GeomagStatus.QUIET,
        signal_noise="S1",
    )
    defaults.update(kwargs)
    return SolarData(**defaults)


def test_conditions_disturbed():
    s = _make_solar(k_index=5)
    assert "DISTURBED" in s.conditions_summary()


def test_conditions_unsettled():
    s = _make_solar(k_index=4)
    assert "UNSETTLED" in s.conditions_summary()


def test_conditions_excellent():
    s = _make_solar(solar_flux=160, k_index=1)
    assert "EXCELLENT" in s.conditions_summary()


def test_conditions_good():
    s = _make_solar(solar_flux=120, k_index=2)
    assert "GOOD" in s.conditions_summary()


def test_conditions_fair():
    s = _make_solar(solar_flux=60, k_index=2)
    assert "FAIR" in s.conditions_summary()


def test_sfi_label_low():
    assert _make_solar(solar_flux=50).sfi_label() == "Low"


def test_sfi_label_moderate():
    assert _make_solar(solar_flux=100).sfi_label() == "Moderate"


def test_sfi_label_high():
    assert _make_solar(solar_flux=150).sfi_label() == "High"


def test_k_label_quiet():
    assert _make_solar(k_index=0).k_label() == "Quiet"


def test_k_label_unsettled():
    assert _make_solar(k_index=3).k_label() == "Unsettled"


def test_k_label_storm():
    assert _make_solar(k_index=5).k_label() == "Minor Storm"
