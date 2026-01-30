"""CLI entry point for hfprop."""

import argparse
import sys

from hfprop import __version__


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="hfprop",
        description="HF propagation conditions for field operators",
        epilog="Solar data courtesy N0NBH (hamqsl.com). "
        "Geomagnetic data from NOAA SWPC.",
    )
    parser.add_argument(
        "--offline",
        action="store_true",
        help="Use cached data only (no network requests)",
    )
    parser.add_argument(
        "--no-color",
        action="store_true",
        help="Disable colored terminal output",
    )
    parser.add_argument(
        "--json",
        action="store_true",
        help="Output as JSON (for scripting/integration)",
    )
    parser.add_argument(
        "--grid",
        metavar="GRID",
        help="Maidenhead grid locator (e.g., EM73) for location-aware output",
    )
    parser.add_argument(
        "--version",
        action="version",
        version=f"%(prog)s {__version__}",
    )

    subparsers = parser.add_subparsers(dest="command")
    subparsers.add_parser("now", help="Current conditions overview")
    subparsers.add_parser("bands", help="Band-by-band breakdown")
    subparsers.add_parser("solar", help="Solar/geomagnetic indices")

    path_parser = subparsers.add_parser("path", help="Point-to-point path analysis")
    path_parser.add_argument("grid1", help="Your grid locator (e.g., EM73)")
    path_parser.add_argument("grid2", help="Remote grid locator (e.g., JN48)")

    watch_parser = subparsers.add_parser("watch", help="Continuous monitoring")
    watch_parser.add_argument(
        "--interval",
        type=int,
        default=3600,
        metavar="SECS",
        help="Refresh interval in seconds (default: 3600)",
    )

    history_parser = subparsers.add_parser("history", help="View condition history")
    history_parser.add_argument(
        "--days",
        type=int,
        default=7,
        metavar="N",
        help="Show entries from the last N days (default: 7)",
    )

    serve_parser = subparsers.add_parser(
        "serve", help="Run as Reticulum propagation service"
    )
    serve_parser.add_argument(
        "--announce-interval",
        type=int,
        default=600,
        metavar="SECS",
        help="Announce interval in seconds (default: 600)",
    )

    query_parser = subparsers.add_parser("query", help="Query remote hfprop node")
    query_parser.add_argument(
        "destination", help="Destination hash of remote hfprop serve node"
    )

    return parser


def main():
    parser = build_parser()
    args = parser.parse_args()

    if args.command is None:
        args.command = "now"

    if args.no_color or args.json:
        from hfprop.display import set_color
        set_color(False)

    from hfprop.commands import now, bands, solar, path, watch, history, serve, query

    commands = {
        "now": now.run,
        "bands": bands.run,
        "solar": solar.run,
        "path": path.run,
        "watch": watch.run,
        "history": history.run,
        "serve": serve.run,
        "query": query.run,
    }

    cmd = commands.get(args.command)
    if cmd is None:
        parser.print_help()
        sys.exit(1)

    try:
        cmd(args)
    except KeyboardInterrupt:
        sys.exit(130)
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)
