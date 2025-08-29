r"""Color each line from stdin based on its key identified by REGEX.

If REGEX contains one or more capturing groups, the last matching capturing
group will be used as the key. Otherwise, the entire match will be used.

Examples:
  * color journalctl output by PID:  '\S+\[(\d+)\]:'
  * color by values like "123 ms":  '(\d+) ms' --values 0:100
"""

from __future__ import annotations

import argparse
import itertools
import re
import sys
from typing import Callable, Iterator, NamedTuple, Self, TypeVar


def main() -> None:
    parser = argparse.ArgumentParser(
        prog="colorby",
        description=__doc__,
        formatter_class=argparse.RawDescriptionHelpFormatter,
        usage="%(prog)s [mode options] [other options] [REGEX]",
        allow_abbrev=False,
    )
    parser.add_argument(
        "pattern",
        help=r"what to match (default: ^[\w.-/]+)",
        type=_argparse_type(re.compile, "REGEX"),
        default=r"^[\w.-/]+",
        metavar="REGEX",
        nargs="?",
    )

    mode_group = parser.add_argument_group("mode options")
    modes = mode_group.add_mutually_exclusive_group()
    modes.add_argument(
        "--assign",
        help="assign colors to keys; reuse colors if needed (default)",
        action="store_true",
    )
    modes.add_argument(
        "--cycle",
        help="switch color whenever the key changes",
        action="store_true",
    )
    modes.add_argument(
        "--values",
        help="assign color based on key's numeric value",
        type=_argparse_type(LowHigh.parse, "LOW:HIGH"),
        metavar="LOW:HIGH",
    )

    color_group = parser.add_argument_group("color options")
    color_group.add_argument(
        "--key-only",
        action="store_true",
        help="color the key rather than the whole line",
    )
    color_group.add_argument(
        "--once",
        action="store_true",
        help="use each color only once; then stop coloring",
    )
    palettes = color_group.add_mutually_exclusive_group()
    palettes.add_argument(
        "--palette",
        help="which color palette to use (default: builtin)",
        choices=["builtin", "term16"],
        default="builtin",
        metavar="PALETTE",
    )
    palettes.add_argument(
        "-t",
        "--no-true-color",
        help="use the terminal's 16-color palette (shortcut for --palette term16)",
        action="store_const",
        const="term16",
        dest="palette",
    )

    args = parser.parse_args()
    if args.cycle:
        mode = "cycle"
    elif args.values:
        mode = "values"
    else:
        mode = "assign"

    if mode == "values" and args.once:
        parser.error("--once can't be used in --values mode")
    matcher = args.pattern.search

    def key(line: str) -> str | None:
        if match := matcher(line):
            if match.lastindex is not None:
                return match[match.lastindex]
            else:
                return match[0]
        return None

    line_groups_iter = itertools.groupby(sys.stdin, key=key)

    if mode == "values":
        if args.palette == "builtin":
            escapes = BUILTIN_VALUES_ESCAPES
            fallback = BUILTIN_FALLBACK_ESCAPE
        elif args.palette == "term16":
            escapes = TERM16_VALUES_ESCAPES
            fallback = TERM16_FALLBACK_ESCAPE
        colored_line_iter = values(line_groups_iter, escapes, fallback, args.values)
    else:
        if args.palette == "builtin":
            escapes = BUILTIN_ESCAPES
            fallback = BUILTIN_FALLBACK_ESCAPE
        elif args.palette == "term16":
            escapes = TERM16_ESCAPES
            fallback = TERM16_FALLBACK_ESCAPE

        if args.once:
            color_escapes_iter = itertools.chain(
                iter(escapes), itertools.repeat(fallback)
            )
        else:
            color_escapes_iter = itertools.cycle(escapes)

        if mode == "assign":
            colored_line_iter = assign(line_groups_iter, color_escapes_iter)
        elif mode == "cycle":
            colored_line_iter = cycle(line_groups_iter, color_escapes_iter)
        else:
            assert False, f"Mode not handled: {mode!r}"

    for cl in colored_line_iter:
        line = cl.line.rstrip("\n")
        if cl.escape:
            print(f"{cl.escape}{line}{RESET_FGCOLOR_ESCAPE}")
        else:
            print(f"{line}")


class ColoredLine(NamedTuple):
    escape: str | None
    key: str
    line: str


def assign(
    line_groups_iter: Iterator[tuple[str, list[str]]],
    color_escapes_iter: Iterator[str],
) -> Iterator[ColoredLine]:
    assignments: dict[str, str] = {}
    for key, line_group in line_groups_iter:
        if key:
            escape = assignments.get(key)
            if escape is None:
                escape = next(color_escapes_iter)
                assignments[key] = escape
        else:
            escape = None
        for line in line_group:
            yield ColoredLine(escape, key, line)


def cycle(
    line_groups_iter: Iterator[tuple[str, list[str]]],
    color_escapes_iter: Iterator[str],
) -> Iterator[ColoredLine]:
    for key, line_group in line_groups_iter:
        escape = next(color_escapes_iter) if key else None
        for line in line_group:
            yield ColoredLine(escape, key, line)


def values(
    line_groups_iter: Iterator[tuple[str, list[str]]],
    escapes: list[str],
    fallback_escape: str,
    thresholds: LowHigh,
):
    for key, line_group in line_groups_iter:
        try:
            n = float(key)
        except (TypeError, ValueError):
            escape = fallback_escape
        else:
            i = bucket(n, thresholds.low, thresholds.high, len(escapes))
            escape = escapes[i]
        for line in line_group:
            yield ColoredLine(escape, key, line)


def bucket(n: float, low: float, high: float, buckets: int) -> int:
    """Return the index of the bucket n falls into.

    Values outside of the range defined by low and high are mapped to the
    nearest buckets.

    >>> bucket(1, 2, 5, 4)
    0
    >>> bucket(2, 2, 5, 4)
    0
    >>> bucket(3, 2, 5, 4)
    1
    >>> bucket(4, 2, 5, 4)
    2
    >>> bucket(5, 2, 5, 4)
    3
    >>> bucket(6, 2, 5, 4)
    3

    >>> bucket(1, 2.0, 3.0, 4)
    0
    >>> bucket(2, 2.0, 3.0, 4)
    0
    >>> bucket(2.01, 2.0, 3.0, 4)
    0
    >>> bucket(2.49, 2.0, 3.0, 4)
    1
    >>> bucket(2.50, 2.0, 3.0, 4)
    2
    >>> bucket(2.99, 2.0, 3.0, 4)
    3
    >>> bucket(3.0, 2.0, 3.0, 4)
    3
    """
    if n < low:
        return 0
    elif low <= n < high:
        return int((n - low) * buckets // int(high - low))
    else:
        return buckets - 1


def clamp(v: int, low: int, high: int) -> int:
    return min(high, max(low, v))


RESET_FGCOLOR_ESCAPE = "\x1b[39m"
BUILTIN_COLORS = [
    "#518921",  # green
    "#3982ce",  # blue
    "#a79026",  # yellow
    "#b44738",  # red
    "#806acc",  # violet
    "#008f89",  # cyan
    "#af6423",  # orange
    "#ae4fa3",  # magenta
    "#a0a0a0",  # dim white
    "#6ea63f",  # bright green
    "#5799e7",  # bright blue
    "#c9b047",  # bright yellow
    "#d2614f",  # bright red
    "#957fe3",  # bright violet
    "#00b2ab",  # bright cyan
    "#cd7e3c",  # bright orange
    "#c866bb",  # bright magenta
]
BUILTIN_ESCAPES = [
    f"\x1b[38;2;{int(color[1:3], 16)};{int(color[3:5], 16)};{int(color[5:7], 16)}m"
    for color in BUILTIN_COLORS
]
BUILTIN_FALLBACK_ESCAPE = "\x1b[38;2;128;128;128m"  # grey
TERM16_ESCAPES = [
    *(f"\x1b[3{i}m" for i in range(1, 7)),
    *(f"\x1b[9{i}m" for i in range(1, 8)),
]
TERM16_FALLBACK_ESCAPE = "\x1b[30m"

BUILTIN_VALUES_COLORS = [
    "#629846",  # green oklch(0.6217, 0.1268, 136)
    "#6d953d",
    "#779333",
    "#809029",
    "#898e1f",
    "#918b15",
    "#99870b",
    "#a08403",
    "#a68101",
    "#ac7e06",
    "#b27a0f",
    "#b77719",
    "#bb7423",
    "#be712d",
    "#c16e36",
    "#c46b3f",
    "#c66948",
    "#c76751",
    "#c8665a",  # red (hue=28)
]
BUILTIN_VALUES_ESCAPES = [
    f"\x1b[38;2;{int(color[1:3], 16)};{int(color[3:5], 16)};{int(color[5:7], 16)}m"
    for color in BUILTIN_VALUES_COLORS
]
TERM16_VALUES_ESCAPES = [f"\x1b[3{i}m" for i in [0, 5, 4, 6, 2, 3, 1]]

T = TypeVar("T")


def _argparse_type(
    type_func: Callable[[str], T], type_name: str | None = None
) -> Callable[[str], T]:
    """Wrap a type for use as the `type` parameter of an add_argument() call.

    If the type function raises ValueError, this wrapper produces an error
    message that includes the exception message.
    """
    if type_name is None:
        type_name = type_func.__name__

    def _argparse_type_wrapper(s: str) -> T:
        try:
            return type_func(s)
        except ValueError as e:
            raise argparse.ArgumentTypeError(f"invalid {type_name} value: {s!r} ({e})")

    _argparse_type_wrapper.__name__ += "_" + type_func.__name__
    return _argparse_type_wrapper


class LowHigh(NamedTuple):
    low: float
    high: float

    @classmethod
    def parse(cls, s: str) -> Self:
        try:
            low_str, high_str = s.split(":")
        except ValueError:
            raise ValueError("Expected exactly one ':'")
        return cls(float(low_str), float(high_str))
