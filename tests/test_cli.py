"""Tests for CLI argument parsing."""

from hfprop.cli import build_parser


def test_default_command():
    parser = build_parser()
    args = parser.parse_args([])
    assert args.command is None  # main() defaults to "now"


def test_now_command():
    parser = build_parser()
    args = parser.parse_args(["now"])
    assert args.command == "now"


def test_bands_command():
    parser = build_parser()
    args = parser.parse_args(["bands"])
    assert args.command == "bands"


def test_solar_command():
    parser = build_parser()
    args = parser.parse_args(["solar"])
    assert args.command == "solar"


def test_offline_flag():
    parser = build_parser()
    args = parser.parse_args(["--offline", "solar"])
    assert args.offline is True
    assert args.command == "solar"


def test_no_color_flag():
    parser = build_parser()
    args = parser.parse_args(["--no-color", "now"])
    assert args.no_color is True


def test_json_flag():
    parser = build_parser()
    args = parser.parse_args(["--json", "now"])
    assert args.json is True


def test_combined_flags():
    parser = build_parser()
    args = parser.parse_args(["--offline", "--no-color", "--json", "bands"])
    assert args.offline is True
    assert args.no_color is True
    assert args.json is True
    assert args.command == "bands"


# --- New feature CLI tests ---

def test_grid_flag():
    parser = build_parser()
    args = parser.parse_args(["--grid", "EM73", "now"])
    assert args.grid == "EM73"
    assert args.command == "now"


def test_grid_flag_default_none():
    parser = build_parser()
    args = parser.parse_args(["now"])
    assert args.grid is None


def test_path_command():
    parser = build_parser()
    args = parser.parse_args(["path", "EM73", "JN48"])
    assert args.command == "path"
    assert args.grid1 == "EM73"
    assert args.grid2 == "JN48"


def test_watch_command():
    parser = build_parser()
    args = parser.parse_args(["watch"])
    assert args.command == "watch"
    assert args.interval == 3600


def test_watch_interval():
    parser = build_parser()
    args = parser.parse_args(["watch", "--interval", "1800"])
    assert args.interval == 1800


def test_history_command():
    parser = build_parser()
    args = parser.parse_args(["history"])
    assert args.command == "history"
    assert args.days == 7


def test_history_days():
    parser = build_parser()
    args = parser.parse_args(["history", "--days", "14"])
    assert args.days == 14


def test_serve_command():
    parser = build_parser()
    args = parser.parse_args(["serve"])
    assert args.command == "serve"
    assert args.announce_interval == 600


def test_query_command():
    parser = build_parser()
    args = parser.parse_args(["query", "abcdef1234567890"])
    assert args.command == "query"
    assert args.destination == "abcdef1234567890"
