"""Tests for display formatting."""

from hfprop.display import c, condition_str, grayline_banner, set_color, BOLD, GREEN, RED, YELLOW
from hfprop.models import BandCondition


def test_color_disabled():
    set_color(False)
    assert c(BOLD, "test") == "test"
    set_color(None)


def test_color_enabled():
    set_color(True)
    result = c(BOLD, "test")
    assert "\033[1m" in result
    assert "test" in result
    set_color(None)


def test_condition_good_has_text():
    set_color(False)
    result = condition_str(BandCondition.GOOD)
    assert "Good" in result
    set_color(None)


def test_condition_poor_has_text():
    set_color(False)
    result = condition_str(BandCondition.POOR)
    assert "Poor" in result
    set_color(None)


def test_grayline_banner_has_text():
    set_color(False)
    result = grayline_banner()
    assert "GRAYLINE" in result
    set_color(None)


def test_grayline_banner_with_color():
    set_color(True)
    result = grayline_banner()
    assert "GRAYLINE" in result
    assert "\033[" in result
    set_color(None)
