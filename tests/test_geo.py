"""Tests for geographic and solar calculations."""

import math
from datetime import datetime, timezone

import pytest

from hfprop.geo import (
    SolarPosition,
    bearing_degrees,
    grid_to_latlon,
    haversine_km,
    solar_elevation,
    get_solar_position,
)


# --- grid_to_latlon ---

def test_grid_4char_em73():
    lat, lon = grid_to_latlon("EM73")
    # EM73: E=4,M=12 -> lon=-100+14+1=-85, lat=30+3+0.5=33.5
    assert 33.0 < lat < 34.0
    assert -86.0 < lon < -84.0


def test_grid_6char_jn48dk():
    lat, lon = grid_to_latlon("JN48dk")
    # JN48 is central Europe (around 48N, 6E area)
    assert 47.0 < lat < 49.0
    assert 5.0 < lon < 9.0


def test_grid_case_insensitive():
    lat1, lon1 = grid_to_latlon("em73")
    lat2, lon2 = grid_to_latlon("EM73")
    assert lat1 == lat2
    assert lon1 == lon2


def test_grid_invalid_too_short():
    with pytest.raises(ValueError):
        grid_to_latlon("EM")


def test_grid_invalid_odd_length():
    with pytest.raises(ValueError):
        grid_to_latlon("EM7")


def test_grid_invalid_field_char():
    with pytest.raises(ValueError):
        grid_to_latlon("ZZ00")


def test_grid_fn31():
    lat, lon = grid_to_latlon("FN31")
    # FN31: F=5,N=13 -> lon=-80+6+1=-73, lat=40+1+0.5=41.5
    assert 41.0 < lat < 42.0
    assert -74.0 < lon <= -72.0


# --- solar_elevation ---

def test_solar_elevation_equator_equinox_noon():
    # March 21 at noon UTC at (0, 0) should be near 90 degrees
    equinox = datetime(2026, 3, 21, 12, 0, 0, tzinfo=timezone.utc)
    elev = solar_elevation(0.0, 0.0, equinox)
    assert elev > 70.0  # Should be high, near zenith


def test_solar_elevation_night():
    # Midnight UTC at lon=0 should be negative elevation
    midnight = datetime(2026, 6, 15, 0, 0, 0, tzinfo=timezone.utc)
    elev = solar_elevation(45.0, 0.0, midnight)
    assert elev < 0.0


def test_solar_elevation_returns_float():
    t = datetime(2026, 6, 15, 12, 0, 0, tzinfo=timezone.utc)
    elev = solar_elevation(40.0, -80.0, t)
    assert isinstance(elev, float)


# --- SolarPosition ---

def test_solar_position_day():
    pos = SolarPosition(42.0, 37.5, -83.0)
    assert pos.is_day is True
    assert pos.is_night is False
    assert pos.is_grayline is False
    assert pos.status == "DAY"


def test_solar_position_night():
    pos = SolarPosition(-15.0, 37.5, -83.0)
    assert pos.is_day is False
    assert pos.is_night is True
    assert pos.is_grayline is False
    assert pos.status == "NIGHT"


def test_solar_position_grayline():
    pos = SolarPosition(-3.0, 37.5, -83.0)
    assert pos.is_day is False
    assert pos.is_night is False
    assert pos.is_grayline is True
    assert pos.status == "GRAYLINE"


def test_solar_position_grayline_boundary_lower():
    pos = SolarPosition(-6.0, 0.0, 0.0)
    assert pos.is_grayline is True


def test_solar_position_grayline_boundary_upper():
    pos = SolarPosition(0.0, 0.0, 0.0)
    assert pos.is_grayline is True


# --- get_solar_position ---

def test_get_solar_position():
    t = datetime(2026, 6, 15, 18, 0, 0, tzinfo=timezone.utc)
    pos = get_solar_position("EM73", t)
    assert pos.grid == "EM73"
    assert isinstance(pos.elevation, float)
    assert pos.lat != 0.0


# --- haversine_km ---

def test_haversine_same_point():
    d = haversine_km(40.0, -74.0, 40.0, -74.0)
    assert d < 0.01


def test_haversine_ny_london():
    # NYC (40.7, -74.0) to London (51.5, -0.1) ~ 5570 km
    d = haversine_km(40.7, -74.0, 51.5, -0.1)
    assert 5400.0 < d < 5700.0


def test_haversine_antipodal():
    # Opposite sides of Earth ~ 20000 km
    d = haversine_km(0.0, 0.0, 0.0, 180.0)
    assert 19900.0 < d < 20100.0


# --- bearing_degrees ---

def test_bearing_due_north():
    # Same longitude, higher latitude -> ~0 degrees
    b = bearing_degrees(40.0, -74.0, 50.0, -74.0)
    assert b < 1.0 or b > 359.0


def test_bearing_due_south():
    b = bearing_degrees(50.0, -74.0, 40.0, -74.0)
    assert 179.0 < b < 181.0


def test_bearing_due_east():
    # Equator, same lat, east -> 90 degrees
    b = bearing_degrees(0.0, 0.0, 0.0, 10.0)
    assert 89.0 < b < 91.0


def test_bearing_range():
    b = bearing_degrees(40.0, -74.0, 51.5, -0.1)
    assert 0.0 <= b < 360.0
