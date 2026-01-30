"""hfprop query -- Query a remote hfprop serve node."""

import json as _json
import sys

from hfprop.display import c, dim, header, k_color, BOLD, CYAN


def run(args):
    from hfprop.reticulum import check_rns_available, HFPropClient
    check_rns_available()

    dest_hash = args.destination
    print(f"Querying {dest_hash}...", file=sys.stderr)

    client = HFPropClient()
    data = client.query(dest_hash)

    if data is None:
        print("Error: Could not reach remote node.", file=sys.stderr)
        sys.exit(1)

    if "error" in data:
        print(f"Remote error: {data['error']}", file=sys.stderr)
        sys.exit(1)

    if args.json:
        print(_json.dumps(data, indent=2))
        return

    solar = data.get("solar", {})
    print()
    print(header("Remote HF Conditions"))
    print(header("=" * 42))
    print(
        f"SFI: {c(BOLD, str(solar.get('solar_flux', '?')))}  |  "
        f"K: {solar.get('k_index', '?')}  |  "
        f"A: {solar.get('a_index', '?')}"
    )
    print(f"Assessment: {c(CYAN, solar.get('assessment', 'Unknown'))}")
    print()
    for b in data.get("bands", []):
        print(f"  {b['name']:<12}Day: {b['day']:<8}Night: {b['night']}")
    print()
    print(dim(f"Source: {data.get('source', 'Remote node')}"))
    print()
