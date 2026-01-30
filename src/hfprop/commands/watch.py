"""hfprop watch -- Continuous monitoring with change detection."""

import os
import sys
import time
from datetime import datetime, timezone

from hfprop.display import c, condition_str, dim, grayline_banner, header, k_color, BOLD, CYAN, YELLOW, RED
from hfprop.fetch import get_report
from hfprop.models import PropagationReport


def _clear_screen():
    os.system("cls" if os.name == "nt" else "clear")


def _diff_reports(old, new):
    """Compare two reports and return list of change strings."""
    changes = []
    if old.solar.k_index != new.solar.k_index:
        changes.append(f"K-index: {old.solar.k_index} -> {new.solar.k_index}")
    if old.solar.solar_flux != new.solar.solar_flux:
        changes.append(f"SFI: {old.solar.solar_flux} -> {new.solar.solar_flux}")
    if old.solar.geomag_field != new.solar.geomag_field:
        changes.append(
            f"Geomag: {old.solar.geomag_field.value} -> {new.solar.geomag_field.value}"
        )

    old_bands = {b.band_name: b for b in old.bands}
    for band in new.bands:
        ob = old_bands.get(band.band_name)
        if ob is None:
            continue
        if ob.day != band.day:
            changes.append(f"{band.band_name} day: {ob.day.value} -> {band.day.value}")
        if ob.night != band.night:
            changes.append(
                f"{band.band_name} night: {ob.night.value} -> {band.night.value}"
            )

    return changes


def run(args):
    if args.json:
        print("Watch mode does not support --json output.", file=sys.stderr)
        sys.exit(1)

    interval = getattr(args, "interval", 3600)
    prev_report = None

    pos = None
    if getattr(args, "grid", None):
        from hfprop.geo import get_solar_position
        pos = get_solar_position(args.grid)

    try:
        while True:
            report = get_report(offline=args.offline)

            # Refresh solar position each cycle
            if getattr(args, "grid", None):
                from hfprop.geo import get_solar_position
                pos = get_solar_position(args.grid)

            _clear_screen()
            _print_watch(report, prev_report, pos, interval)
            prev_report = report
            time.sleep(interval)
    except KeyboardInterrupt:
        print("\nWatch stopped.")
        sys.exit(0)


def _print_watch(report, prev_report, pos, interval):
    solar = report.solar
    now = datetime.now(timezone.utc).strftime("%d %b %Y %H:%M UTC")

    print()
    print(header(f"HF Propagation -- {now}  [WATCH]"))
    print(header("=" * 46))

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

    if pos:
        print(f"Location: {pos.grid} -- {pos.status} (elev: {pos.elevation:.1f})")

    print()
    print(f"Assessment: {c(CYAN, solar.conditions_summary())}")

    if pos and pos.is_grayline:
        print(grayline_banner())

    print()

    if report.bands:
        if pos and not pos.is_grayline:
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

    # Change detection
    if prev_report is not None:
        changes = _diff_reports(prev_report, report)
        if changes:
            print(c(YELLOW, "Changes since last check:"))
            for change in changes:
                print(c(YELLOW, f"  {change}"))
            print()
        else:
            print(dim("No changes since last check."))
            print()

    cached_label = "Yes" if report.cached else "No"
    print(dim(f"Data: {report.source} | Cached: {cached_label}"))
    print(dim(f"Next refresh in {interval}s. Ctrl+C to stop."))
    print()
