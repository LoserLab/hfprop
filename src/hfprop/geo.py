"""Geographic and solar position calculations for Maidenhead grid locators.

All calculations use only the math and datetime stdlib modules.
"""

import math
from datetime import datetime, timezone
from typing import Tuple


class SolarPosition:
    """Result of solar elevation calculation."""

    def __init__(self, elevation: float, lat: float, lon: float, grid: str = ""):
        self.elevation = elevation
        self.lat = lat
        self.lon = lon
        self.grid = grid

    @property
    def is_day(self) -> bool:
        return self.elevation > 0.0

    @property
    def is_night(self) -> bool:
        return self.elevation < -6.0

    @property
    def is_grayline(self) -> bool:
        return -6.0 <= self.elevation <= 0.0

    @property
    def status(self) -> str:
        if self.is_grayline:
            return "GRAYLINE"
        return "DAY" if self.is_day else "NIGHT"


def grid_to_latlon(grid: str) -> Tuple[float, float]:
    """Convert Maidenhead grid locator (4 or 6 char) to (lat, lon).

    Returns the center of the grid square.
    """
    grid = grid.strip()
    if len(grid) < 4 or len(grid) % 2 != 0 or len(grid) > 8:
        raise ValueError(f"Invalid grid locator: {grid!r}")

    g = grid.upper()

    # Field (A-R)
    if not ('A' <= g[0] <= 'R' and 'A' <= g[1] <= 'R'):
        raise ValueError(f"Invalid grid locator field: {grid!r}")
    lon = (ord(g[0]) - ord('A')) * 20 - 180
    lat = (ord(g[1]) - ord('A')) * 10 - 90

    # Square (0-9)
    if not (g[2].isdigit() and g[3].isdigit()):
        raise ValueError(f"Invalid grid locator square: {grid!r}")
    lon += int(g[2]) * 2
    lat += int(g[3]) * 1

    if len(grid) >= 6:
        # Subsquare (A-X)
        if not ('A' <= g[4] <= 'X' and 'A' <= g[5] <= 'X'):
            raise ValueError(f"Invalid grid locator subsquare: {grid!r}")
        lon += (ord(g[4]) - ord('A')) * (5.0 / 60.0)
        lat += (ord(g[5]) - ord('A')) * (2.5 / 60.0)
        # Center of subsquare
        lon += 2.5 / 60.0
        lat += 1.25 / 60.0
    else:
        # Center of square
        lon += 1.0
        lat += 0.5

    return (lat, lon)


def solar_elevation(lat: float, lon: float, utc_time: datetime = None) -> float:
    """Calculate solar elevation angle in degrees.

    Uses simplified solar position formula:
    - Declination: d = 0.4093 * sin(2*pi/365 * doy - 1.405)
    - Hour angle: H = (utc_hour + lon/15 - 12) * 15 degrees
    - Elevation: arcsin(sin(lat)*sin(d) + cos(lat)*cos(d)*cos(H))
    """
    if utc_time is None:
        utc_time = datetime.now(timezone.utc)

    doy = utc_time.timetuple().tm_yday
    hour = utc_time.hour + utc_time.minute / 60.0 + utc_time.second / 3600.0

    lat_r = math.radians(lat)
    decl = 0.4093 * math.sin(2.0 * math.pi / 365.0 * doy - 1.405)
    ha = math.radians((hour + lon / 15.0 - 12.0) * 15.0)

    sin_elev = (
        math.sin(lat_r) * math.sin(decl)
        + math.cos(lat_r) * math.cos(decl) * math.cos(ha)
    )
    # Clamp for asin safety
    sin_elev = max(-1.0, min(1.0, sin_elev))
    return math.degrees(math.asin(sin_elev))


def get_solar_position(grid: str, utc_time: datetime = None) -> SolarPosition:
    """Convert grid locator to solar position."""
    lat, lon = grid_to_latlon(grid)
    elev = solar_elevation(lat, lon, utc_time)
    return SolarPosition(elev, lat, lon, grid=grid.strip().upper())


def haversine_km(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """Great-circle distance in km between two lat/lon points."""
    R = 6371.0
    dlat = math.radians(lat2 - lat1)
    dlon = math.radians(lon2 - lon1)
    a = (
        math.sin(dlat / 2.0) ** 2
        + math.cos(math.radians(lat1))
        * math.cos(math.radians(lat2))
        * math.sin(dlon / 2.0) ** 2
    )
    return R * 2.0 * math.atan2(math.sqrt(a), math.sqrt(1.0 - a))


def bearing_degrees(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """Initial bearing from point 1 to point 2, in degrees 0-360."""
    lat1_r = math.radians(lat1)
    lat2_r = math.radians(lat2)
    dlon_r = math.radians(lon2 - lon1)
    x = math.sin(dlon_r) * math.cos(lat2_r)
    y = math.cos(lat1_r) * math.sin(lat2_r) - math.sin(lat1_r) * math.cos(
        lat2_r
    ) * math.cos(dlon_r)
    return (math.degrees(math.atan2(x, y)) + 360.0) % 360.0
