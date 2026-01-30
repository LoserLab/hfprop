"""hfprop now -- Current conditions at a glance."""

import json as _json
from datetime import datetime, timezone

from hfprop.display import c, condition_str, dim, grayline_banner, header, k_color, BOLD, CYAN
from hfprop.fetch import get_report


def run(args):
    report = get_report(offline=args.offline)

    # Resolve grid/solar position if provided
    pos = None
    if getattr(args, "grid", None):
        from hfprop.geo import get_solar_position
        pos = get_solar_position(args.grid)

    if args.json:
        _print_json(report, pos)
        return

    solar = report.solar
    now = datetime.now(timezone.utc).strftime("%d %b %Y %H:%M UTC")

    print()
    print(header(f"HF Propagation -- {now}"))
    print(header("=" * 42))

    print(
        f"SFI: {c(BOLD, str(solar.solar_flux))}  |  "
        f"SSN: {solar.sunspot_number}  |  "
        f"K: {c(k_color(solar.k_index), str(solar.k_index))}  |  "
        f"A: {solar.a_index}"
    )
    print(
        f"X-Ray: {solar.xray}  |  "
        f"Geomag: {solar.geomag_field.value}"
    )
    print(f"Noise Floor: {solar.signal_noise}")

    if pos:
        print(f"Location: {pos.grid} -- {pos.status} (elev: {pos.elevation:.1f})")

    print()
    print(f"Assessment: {c(CYAN, solar.conditions_summary())}")

    if pos and pos.is_grayline:
        print(grayline_banner())

    print()

    if report.bands:
        if pos and not pos.is_grayline:
            # Show only the relevant column
            col = "Day" if pos.is_day else "Night"
            print(f"{'Band':<12}{col:<8}")
            print("-" * 20)
            for band in report.bands:
                cond = band.day if pos.is_day else band.night
                print(f"{band.band_name:<12}{condition_str(cond):<8}")
        else:
            print(f"{'Band':<12}{'Day':<8}{'Night':<8}")
            print("-" * 28)
            for band in report.bands:
                print(
                    f"{band.band_name:<12}"
                    f"{condition_str(band.day):<8}"
                    f"{condition_str(band.night):<8}"
                )
        print()

    cached_label = "Yes" if report.cached else "No"
    print(dim(f"Data: {report.source} | Cached: {cached_label}"))
    print()


def _print_json(report, pos=None):
    data = {
        "solar": {
            "solar_flux": report.solar.solar_flux,
            "sunspot_number": report.solar.sunspot_number,
            "a_index": report.solar.a_index,
            "k_index": report.solar.k_index,
            "xray": report.solar.xray,
            "geomag_field": report.solar.geomag_field.value,
            "signal_noise": report.solar.signal_noise,
            "solar_wind": report.solar.solar_wind,
            "bz": report.solar.bz,
            "proton_flux": report.solar.proton_flux,
            "assessment": report.solar.conditions_summary(),
        },
        "bands": [
            {
                "name": b.band_name,
                "day": b.day.value,
                "night": b.night.value,
            }
            for b in report.bands
        ],
        "source": report.source,
        "cached": report.cached,
    }
    if pos:
        data["location"] = {
            "grid": pos.grid,
            "lat": pos.lat,
            "lon": pos.lon,
            "elevation": round(pos.elevation, 1),
            "status": pos.status,
        }
    print(_json.dumps(data, indent=2))
