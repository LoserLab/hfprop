"""hfprop history -- View logged condition history."""

import json as _json

from hfprop.display import c, dim, header, k_color, BOLD
from hfprop.history import HistoryDB


def run(args):
    days = getattr(args, "days", 7)
    db = HistoryDB()
    entries = db.query(days=days)

    if args.json:
        _print_json(entries, days)
        return

    if not entries:
        print(f"\nNo history data in the last {days} day(s).")
        print(dim("Run hfprop (with internet) to start logging.\n"))
        return

    print()
    print(header(f"Condition History -- Last {days} day(s)"))
    print(header("=" * 55))
    print()
    print(f"{'Timestamp':<22}{'SFI':>5}{'SSN':>5}{'K':>3}{'A':>4}  {'Geomag'}")
    print("-" * 55)
    for e in entries:
        ts = e["timestamp"][:16].replace("T", " ")
        k = e["k_index"]
        print(
            f"{ts:<22}{e['sfi']:>5}{e['ssn']:>5}"
            f"{c(k_color(k), str(k)):>3}{e['a_index']:>4}  {e['geomag']}"
        )
    print()
    print(dim(f"{len(entries)} record(s)"))
    print()


def _print_json(entries, days):
    data = {
        "days": days,
        "count": len(entries),
        "entries": entries,
    }
    print(_json.dumps(data, indent=2))
