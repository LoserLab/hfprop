"""hfprop solar -- Full solar/geomagnetic data."""

import json as _json
from datetime import datetime, timezone

from hfprop.display import c, dim, header, k_color, BOLD, CYAN, DIM, YELLOW
from hfprop.fetch import get_report


def run(args):
    report = get_report(offline=args.offline)

    if args.json:
        _print_json(report)
        return

    solar = report.solar
    now = datetime.now(timezone.utc).strftime("%d %b %Y %H:%M UTC")

    print()
    print(header(f"Solar & Geomagnetic Indices -- {now}"))
    print(header("=" * 50))
    print()

    print(header("Solar Activity"))
    print(f"  Solar Flux Index (SFI):  {c(BOLD, str(solar.solar_flux)):>8}  [{solar.sfi_label()}]")
    print(f"  Sunspot Number (SSN):    {solar.sunspot_number:>8}")
    print(f"  X-Ray Background:        {solar.xray:>8}")
    print()

    print(header("Geomagnetic Activity"))
    print(f"  K-Index:                 {c(k_color(solar.k_index), str(solar.k_index)):>8}  [{solar.k_label()}]")
    print(f"  A-Index:                 {solar.a_index:>8}")
    print(f"  Geomagnetic Field:       {solar.geomag_field.value:>8}")
    print()

    print(header("Space Weather"))
    sw = f"{solar.solar_wind:.1f} km/s" if solar.solar_wind else "N/A"
    bz = f"{solar.bz:.1f} nT" if solar.bz is not None else "N/A"
    pf = f"{solar.proton_flux:.0f} pfu" if solar.proton_flux is not None else "N/A"
    print(f"  Solar Wind:              {sw:>12}")
    print(f"  Bz (IMF):               {bz:>12}")
    print(f"  Proton Flux:             {pf:>12}")
    print()

    print(header("HF Impact"))
    print(f"  Noise Floor:             {solar.signal_noise}")
    print(f"  Assessment:              {c(CYAN, solar.conditions_summary())}")
    print()

    print(dim("Scales:"))
    print(dim("  SFI: <70 Low | 70-120 Moderate | 120-200 High | >200 Very High"))
    print(dim("  K:   0-1 Quiet | 2-3 Unsettled | 4 Active | 5+ Storm"))
    print()

    cached_label = "Yes" if report.cached else "No"
    print(dim(f"Data: {report.source} | Cached: {cached_label}"))
    print()


def _print_json(report):
    solar = report.solar
    data = {
        "solar_activity": {
            "solar_flux": solar.solar_flux,
            "sfi_label": solar.sfi_label(),
            "sunspot_number": solar.sunspot_number,
            "xray": solar.xray,
        },
        "geomagnetic": {
            "k_index": solar.k_index,
            "k_label": solar.k_label(),
            "a_index": solar.a_index,
            "geomag_field": solar.geomag_field.value,
        },
        "space_weather": {
            "solar_wind_kms": solar.solar_wind,
            "bz_nt": solar.bz,
            "proton_flux_pfu": solar.proton_flux,
        },
        "hf_impact": {
            "noise_floor": solar.signal_noise,
            "assessment": solar.conditions_summary(),
        },
        "source": report.source,
        "cached": report.cached,
    }
    print(_json.dumps(data, indent=2))
