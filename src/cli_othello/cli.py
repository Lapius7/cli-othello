"""Command-line entry point for cli-othello."""

from __future__ import annotations

import argparse
import curses

from . import __version__
from .ai import MAX_LEVEL, MIN_LEVEL
from .ui import init_colors, play_game, select_level
from .board import BLACK


def _run(stdscr: "curses._CursesWindow", level: int | None) -> None:
    init_colors()
    chosen_level = level if level is not None else select_level(stdscr)
    play_game(stdscr, human_player=BLACK, ai_level=chosen_level)


def main() -> None:
    parser = argparse.ArgumentParser(
        prog="othello",
        description="Play Othello (Reversi) in your terminal against a 5-level AI.",
    )
    parser.add_argument(
        "-l",
        "--level",
        type=int,
        choices=range(MIN_LEVEL, MAX_LEVEL + 1),
        help="AIの強さを指定して直接対局を開始する (1-5)。省略すると選択画面が表示されます。",
    )
    parser.add_argument(
        "-V", "--version", action="version", version=f"cli-othello {__version__}"
    )
    args = parser.parse_args()

    try:
        curses.wrapper(_run, args.level)
    except KeyboardInterrupt:
        pass


if __name__ == "__main__":
    main()
