"""hfprop path -- Point-to-point path analysis."""

import json as _json
from datetime import datetime, timezone

from hfprop.config import FREEDV_MODES, HF_BANDS
from hfprop.display import c, condition_str, dim, header, BOLD, CYAN, YELLOW
from hfprop.fetch import get_report
from hfprop.geo import bearing_degrees, get_solar_position, grid_to_latlon, haversine_km
from hfprop.models import BandCondition

# Distance-to-band recommendations
DISTANCE_BANDS = [
    (400, ["80m-40m"], "NVIS"),
    (800, ["80m-40m", "30m-20m"], "NVIS / Short skip"),
    (3000, ["30m-20m", "17m-15m"], "Skip"),
    (float("inf"), ["17m-15m", "12m-10m"], "Long-haul DX"),
]


def _recommend_bands(distance_km):
    for max_dist, bands, prop_type in DISTANCE_BANDS:
        if distance_km < max_dist:
            return bands, prop_type
    return ["17m-15m", "12m-10m"], "Long-haul DX"


def _suggest_mode(condition):
    if condition == BandCondition.GOOD:
        return "DATAC1"
    elif condition == BandCondition.FAIR:
        return "DATAC3"
    else:
        return "DATAC4"


def _relevant_condition(band, pos1, pos2):
    """Pick the relevant condition based on endpoint solar status."""
    # If both day, use day. If both night, use night.
    # If mixed or grayline, use the worse of day/night as conservative estimate.
    if pos1.is_day and pos2.is_day:
        return band.day, "Day"
    elif pos1.is_night and pos2.is_night:
        return band.night, "Night"
    else:
        # Mixed or grayline — show both, pick worse for mode suggestion
        if band.day.value <= band.night.value:  # alphabetical: Fair < Good < Poor
            return band.day, "Day"
        return band.night, "Night"


def run(args):
    grid1 = args.grid1
    grid2 = args.grid2

    lat1, lon1 = grid_to_latlon(grid1)
    lat2, lon2 = grid_to_latlon(grid2)
    dist = haversine_km(lat1, lon1, lat2, lon2)
    brg = bearing_degrees(lat1, lon1, lat2, lon2)

    pos1 = get_solar_position(grid1)
    pos2 = get_solar_position(grid2)

    report = get_report(offline=args.offline)
    rec_bands, prop_type = _recommend_bands(dist)

    if args.json:
        _print_json(report, grid1, grid2, dist, brg, pos1, pos2, rec_bands, prop_type)
        return

    now = datetime.now(timezone.utc).strftime("%d %b %Y %H:%M UTC")

    print()
    print(header(f"Path Analysis: {grid1.upper()} -> {grid2.upper()}"))
    print(header("=" * 45))
    print()

    print(f"Route:    {dist:,.0f} km  |  Bearing: {brg:.0f}  |  Type: {prop_type}")
    print()

    print(f"{'Endpoint':<12}{'Grid':<8}{'Status':<12}{'Elev'}")
    print("-" * 42)
    print(f"{'Local':<12}{pos1.grid:<8}{pos1.status:<12}{pos1.elevation:+.1f}")
    print(f"{'Remote':<12}{pos2.grid:<8}{pos2.status:<12}{pos2.elevation:+.1f}")
    print()

    # Grayline notes
    if pos1.is_grayline:
        print(c(CYAN, f"  {pos1.grid} is in GRAYLINE. 80m-40m enhanced."))
    if pos2.is_grayline:
        print(c(CYAN, f"  {pos2.grid} is in GRAYLINE. 80m-40m enhanced."))
    if pos1.is_grayline or pos2.is_grayline:
        print()

    # Band recommendations
    band_map = {b.band_name: b for b in report.bands}
    print(header(f"Recommended Bands (for {dist:,.0f} km):"))
    for band_name in rec_bands:
        band = band_map.get(band_name)
        if band is None:
            continue
        cond, col = _relevant_condition(band, pos1, pos2)
        mode = _suggest_mode(cond)
        mode_info = FREEDV_MODES[mode]
        info = HF_BANDS.get(band_name, {})
        freq = info.get("freq_range", "")
        print(
            f"  {band_name:<12}"
            f"{col}: {condition_str(cond):<8}  "
            f"-> {mode} ({mode_info['bps']}bps)"
        )
    print()

    # Mixed path note
    if pos1.is_day != pos2.is_day and not pos1.is_grayline and not pos2.is_grayline:
        print(dim("Note: Mixed day/night path. Mid-range bands (20m) often best."))
        print()

    cached_label = "Yes" if report.cached else "No"
    print(dim(f"Data: {report.source} | Cached: {cached_label}"))
    print()


def _print_json(report, grid1, grid2, dist, brg, pos1, pos2, rec_bands, prop_type):
    band_map = {b.band_name: b for b in report.bands}
    recommendations = []
    for band_name in rec_bands:
        band = band_map.get(band_name)
        if band is None:
            continue
        cond, col = _relevant_condition(band, pos1, pos2)
        mode = _suggest_mode(cond)
        mode_info = FREEDV_MODES[mode]
        recommendations.append({
            "band": band_name,
            "condition": cond.value,
            "time": col,
            "suggested_mode": mode,
            "mode_bps": mode_info["bps"],
        })

    data = {
        "path": {
            "from": grid1.upper(),
            "to": grid2.upper(),
            "distance_km": round(dist, 1),
            "bearing": round(brg, 1),
            "type": prop_type,
        },
        "endpoints": [
            {
                "grid": pos1.grid,
                "lat": pos1.lat,
                "lon": pos1.lon,
                "status": pos1.status,
                "elevation": round(pos1.elevation, 1),
            },
            {
                "grid": pos2.grid,
                "lat": pos2.lat,
                "lon": pos2.lon,
                "status": pos2.status,
                "elevation": round(pos2.elevation, 1),
            },
        ],
        "recommendations": recommendations,
        "source": report.source,
        "cached": report.cached,
    }
    print(_json.dumps(data, indent=2))
