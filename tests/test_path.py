"""Tests for path command logic."""

from hfprop.commands.path import _recommend_bands, _suggest_mode
from hfprop.models import BandCondition


def test_recommend_nvis_short():
    bands, ptype = _recommend_bands(200)
    assert "80m-40m" in bands
    assert "NVIS" in ptype


def test_recommend_nvis_border():
    bands, ptype = _recommend_bands(399)
    assert "80m-40m" in bands


def test_recommend_short_skip():
    bands, ptype = _recommend_bands(600)
    assert "30m-20m" in bands


def test_recommend_skip():
    bands, ptype = _recommend_bands(1500)
    assert "30m-20m" in bands or "17m-15m" in bands


def test_recommend_dx():
    bands, ptype = _recommend_bands(5000)
    assert "12m-10m" in bands or "17m-15m" in bands
    assert "DX" in ptype


def test_suggest_mode_good():
    assert _suggest_mode(BandCondition.GOOD) == "DATAC1"


def test_suggest_mode_fair():
    assert _suggest_mode(BandCondition.FAIR) == "DATAC3"


def test_suggest_mode_poor():
    assert _suggest_mode(BandCondition.POOR) == "DATAC4"
