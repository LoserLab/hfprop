"""hfprop bands -- Detailed band-by-band breakdown."""

import json as _json
from datetime import datetime, timezone

from hfprop.config import FREEDV_MODES, HF_BANDS
from hfprop.display import c, condition_str, dim, grayline_banner, header, BOLD, CYAN, DIM
from hfprop.fetch import get_report
from hfprop.models import BandCondition


def _suggest_mode(condition: BandCondition) -> str:
    if condition == BandCondition.GOOD:
        return "DATAC1"
    elif condition == BandCondition.FAIR:
        return "DATAC3"
    else:
        return "DATAC4"


def run(args):
    report = get_report(offline=args.offline)

    pos = None
    if getattr(args, "grid", None):
        from hfprop.geo import get_solar_position
        pos = get_solar_position(args.grid)

    if args.json:
        _print_json(report, pos)
        return

    now = datetime.now(timezone.utc).strftime("%d %b %Y %H:%M UTC")

    print()
    print(header(f"Band Conditions -- {now}"))
    print(header("=" * 42))

    if pos:
        print(f"Location: {pos.grid} -- {pos.status} (elev: {pos.elevation:.1f})")
        if pos.is_grayline:
            print(grayline_banner())

    print()

    for band in report.bands:
        info = HF_BANDS.get(band.band_name, {})
        freq = info.get("freq_range", "")
        character = info.get("character", "")
        note = info.get("note", "")

        label = f"{band.band_name}"
        if freq:
            label += f" ({freq})"
        if character:
            label += f" -- {character}"

        print(header(label))

        if pos and not pos.is_grayline:
            # Show only the relevant condition
            cond = band.day if pos.is_day else band.night
            col = "Day" if pos.is_day else "Night"
            print(f"  {col}:   {condition_str(cond)}")
        else:
            print(
                f"  Day:   {condition_str(band.day)}   "
                f"Night:  {condition_str(band.night)}"
            )

        if note:
            print(dim(f"  Note:  {note}"))

        # Grayline enhancement note for lower bands
        if pos and pos.is_grayline and band.band_name == "80m-40m":
            print(c(CYAN, "  GRAYLINE ACTIVE -- Enhanced propagation on this band"))

        # Suggest FreeDV mode based on relevant condition
        if pos and not pos.is_grayline:
            relevant = band.day if pos.is_day else band.night
        else:
            relevant = band.day if band.day != BandCondition.UNKNOWN else band.night
        mode = _suggest_mode(relevant)
        mode_info = FREEDV_MODES[mode]
        print(
            dim(f"  Mode:  {mode} recommended "
                f"({mode_info['bps']}bps at {mode_info['min_snr_db']}dB SNR)")
        )
        print()

    cached_label = "Yes" if report.cached else "No"
    print(dim(f"Data: {report.source} | Cached: {cached_label}"))
    print()


def _print_json(report, pos=None):
    data = {
        "bands": [],
        "source": report.source,
        "cached": report.cached,
    }
    for band in report.bands:
        info = HF_BANDS.get(band.band_name, {})
        if pos and not pos.is_grayline:
            relevant = band.day if pos.is_day else band.night
        else:
            relevant = band.day if band.day != BandCondition.UNKNOWN else band.night
        mode = _suggest_mode(relevant)
        mode_info = FREEDV_MODES[mode]
        data["bands"].append({
            "name": band.band_name,
            "freq_range": info.get("freq_range", ""),
            "character": info.get("character", ""),
            "day": band.day.value,
            "night": band.night.value,
            "suggested_mode": mode,
            "mode_bps": mode_info["bps"],
            "mode_min_snr_db": mode_info["min_snr_db"],
        })
    if pos:
        data["location"] = {
            "grid": pos.grid,
            "status": pos.status,
            "elevation": round(pos.elevation, 1),
        }
    print(_json.dumps(data, indent=2))
