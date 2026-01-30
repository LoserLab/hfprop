"""Terminal display formatting for hfprop.

Uses ANSI escape codes directly. Respects --no-color and NO_COLOR env var.
"""

import os
import sys

from hfprop.models import BandCondition

# ANSI codes
RED = "\033[91m"
GREEN = "\033[92m"
YELLOW = "\033[93m"
BLUE = "\033[94m"
CYAN = "\033[96m"
MAGENTA = "\033[95m"
BOLD = "\033[1m"
DIM = "\033[2m"
RESET = "\033[0m"

_color_enabled = None


def set_color(enabled: bool):
    global _color_enabled
    _color_enabled = enabled


def _use_color() -> bool:
    if _color_enabled is not None:
        return _color_enabled
    if os.environ.get("NO_COLOR") is not None:
        return False
    return hasattr(sys.stdout, "isatty") and sys.stdout.isatty()


def c(code: str, text: str) -> str:
    """Wrap text in color code if color is enabled."""
    if not _use_color():
        return text
    return f"{code}{text}{RESET}"


def condition_str(cond: BandCondition) -> str:
    colors = {
        BandCondition.GOOD: GREEN,
        BandCondition.FAIR: YELLOW,
        BandCondition.POOR: RED,
        BandCondition.UNKNOWN: DIM,
    }
    return c(colors.get(cond, ""), cond.value.ljust(7))


def k_color(k: int) -> str:
    if k <= 1:
        code = GREEN
    elif k <= 3:
        code = YELLOW
    elif k == 4:
        code = YELLOW
    else:
        code = RED
    return code


def header(text: str) -> str:
    return c(BOLD, text)


def dim(text: str) -> str:
    return c(DIM, text)


def grayline_banner() -> str:
    return c(MAGENTA + BOLD, ">>> GRAYLINE <<<  Enhanced 80m-40m propagation")
