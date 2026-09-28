"""Command-line entry point for cli-othello."""

from __future__ import annotations

import argparse
import shutil
import curses

from . import __version__
from .ai import MAX_LEVEL, MIN_LEVEL
from .ui import init_colors, play_game, select_level
from .board import BLACK


def _run(stdscr: "curses._CursesWindow", level: int | None) -> None:
    init_colors()
    chosen_level = level if level is not None else select_level(stdscr)
    play_game(stdscr, human_player=BLACK, ai_level=chosen_level)


def _lapius_footer() -> str:
    """--help / --version の最後に出す作者表示と lapacks の案内"""
    tip = ("@lapius のツール: lapacks で一覧・インストール・更新" if shutil.which("lapacks")
           else "@lapius のツール: npm i -g @lapius/lapacks で一覧・インストール・更新を管理")
    return f"作者: Lapius (https://github.com/Lapius7)\n{tip}"


def main() -> None:
    parser = argparse.ArgumentParser(
        prog="othello",
        description="Play Othello (Reversi) in your terminal against a 5-level AI.",
        epilog=_lapius_footer(),
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument(
        "-l",
        "--level",
        type=int,
        choices=range(MIN_LEVEL, MAX_LEVEL + 1),
        help="AIの強さを指定して直接対局を開始する (1-5)。省略すると選択画面が表示されます。",
    )
    parser.add_argument(
        "-V", "--version", action="version",
        version=f"cli-othello {__version__}\n{_lapius_footer()}",
    )
    args = parser.parse_args()

    try:
        curses.wrapper(_run, args.level)
    except KeyboardInterrupt:
        pass


if __name__ == "__main__":
    main()
