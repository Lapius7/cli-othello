"""curses-based terminal UI for cli-othello."""

from __future__ import annotations

import curses

from .ai import LEVEL_LABELS, MAX_LEVEL, MIN_LEVEL, OthelloAI
from .board import BLACK, EMPTY, SIZE, WHITE, Board, opponent

DISC_CHARS = {EMPTY: " ", BLACK: "●", WHITE: "○"}
PLAYER_NAMES = {BLACK: "黒", WHITE: "白"}

COLOR_BOARD = 1
COLOR_BLACK = 2
COLOR_WHITE = 3
COLOR_CURSOR = 4
COLOR_HINT = 5
COLOR_HEADER = 6
COLOR_STATUS = 7


def init_colors() -> None:
    curses.start_color()
    curses.use_default_colors()
    curses.init_pair(COLOR_BOARD, curses.COLOR_WHITE, curses.COLOR_GREEN)
    curses.init_pair(COLOR_BLACK, curses.COLOR_BLACK, curses.COLOR_GREEN)
    curses.init_pair(COLOR_WHITE, curses.COLOR_WHITE, curses.COLOR_GREEN)
    curses.init_pair(COLOR_CURSOR, curses.COLOR_BLACK, curses.COLOR_YELLOW)
    curses.init_pair(COLOR_HINT, curses.COLOR_GREEN, curses.COLOR_BLACK)
    curses.init_pair(COLOR_HEADER, curses.COLOR_CYAN, -1)
    curses.init_pair(COLOR_STATUS, curses.COLOR_YELLOW, -1)


def select_level(stdscr: "curses._CursesWindow") -> int:
    """Let the user pick an AI difficulty level (1-5) with arrow keys."""
    level = 3
    curses.curs_set(0)
    while True:
        stdscr.erase()
        stdscr.addstr(1, 2, "CLI OTHELLO", curses.color_pair(COLOR_HEADER) | curses.A_BOLD)
        stdscr.addstr(3, 2, "対戦するAIの強さを選んでください", curses.color_pair(COLOR_HEADER))
        for i in range(MIN_LEVEL, MAX_LEVEL + 1):
            label = LEVEL_LABELS[i]
            attr = curses.A_REVERSE | curses.A_BOLD if i == level else curses.A_NORMAL
            stdscr.addstr(5 + i, 4, f"{label}", attr)
        stdscr.addstr(
            5 + MAX_LEVEL + 2,
            2,
            "↑/↓ で選択、Enter で決定、q で終了",
            curses.color_pair(COLOR_STATUS),
        )
        stdscr.refresh()

        key = stdscr.getch()
        if key in (curses.KEY_UP, ord("k")):
            level = MIN_LEVEL if level <= MIN_LEVEL else level - 1
        elif key in (curses.KEY_DOWN, ord("j")):
            level = MAX_LEVEL if level >= MAX_LEVEL else level + 1
        elif key in (curses.KEY_ENTER, 10, 13):
            return level
        elif key in (ord("q"), ord("Q")):
            raise SystemExit(0)


def _draw_board(
    stdscr: "curses._CursesWindow",
    board: Board,
    cursor: tuple[int, int],
    legal: set[tuple[int, int]],
    human_player: int,
    ai_level: int,
    message: str,
    top: int = 0,
) -> None:
    stdscr.erase()
    stdscr.addstr(top, 2, "CLI OTHELLO", curses.color_pair(COLOR_HEADER) | curses.A_BOLD)
    stdscr.addstr(
        top,
        16,
        f"AI: {LEVEL_LABELS[ai_level]}  あなた: {DISC_CHARS[human_player]}{PLAYER_NAMES[human_player]}",
        curses.color_pair(COLOR_STATUS),
    )

    board_top = top + 2
    board_left = 4

    stdscr.addstr(board_top, board_left + 2, "  ".join("ABCDEFGH"))
    for row in range(SIZE):
        stdscr.addstr(board_top + 1 + row, board_left, f"{row + 1} ")
        for col in range(SIZE):
            cell = board.get(row, col)
            char = DISC_CHARS[cell]
            x = board_left + 2 + col * 3
            y = board_top + 1 + row

            if (row, col) == cursor:
                attr = curses.color_pair(COLOR_CURSOR) | curses.A_BOLD
            elif cell == BLACK:
                attr = curses.color_pair(COLOR_BLACK) | curses.A_BOLD
            elif cell == WHITE:
                attr = curses.color_pair(COLOR_WHITE) | curses.A_BOLD
            else:
                attr = curses.color_pair(COLOR_BOARD)

            display = char
            if cell == EMPTY and (row, col) in legal:
                display = "·"
                if (row, col) != cursor:
                    attr = curses.color_pair(COLOR_HINT)

            stdscr.addstr(y, x, f" {display} ", attr)

    score_y = board_top + SIZE + 2
    stdscr.addstr(
        score_y,
        board_left,
        f"● 黒: {board.count(BLACK)}    ○ 白: {board.count(WHITE)}",
        curses.A_BOLD,
    )
    stdscr.addstr(score_y + 2, board_left, message, curses.color_pair(COLOR_STATUS))
    stdscr.addstr(
        score_y + 3,
        board_left,
        "矢印キー: 移動  Enter/Space: 着手  q: 終了",
        curses.color_pair(COLOR_STATUS),
    )
    stdscr.refresh()


def play_game(stdscr: "curses._CursesWindow", human_player: int, ai_level: int) -> None:
    curses.curs_set(0)
    board = Board()
    ai_player = opponent(human_player)
    ai = OthelloAI(ai_player, ai_level)
    cursor = [3, 3]
    turn = BLACK
    message = ""

    while True:
        if board.is_game_over():
            break

        legal = set(board.legal_moves(turn))
        if not legal:
            message = f"{PLAYER_NAMES[turn]}はパスしました"
            turn = opponent(turn)
            continue

        if turn == human_player:
            message = "あなたの番です"
            _draw_board(stdscr, board, tuple(cursor), legal, human_player, ai_level, message)
            key = stdscr.getch()
            if key in (curses.KEY_UP, ord("k")):
                cursor[0] = (cursor[0] - 1) % SIZE
            elif key in (curses.KEY_DOWN, ord("j")):
                cursor[0] = (cursor[0] + 1) % SIZE
            elif key in (curses.KEY_LEFT, ord("h")):
                cursor[1] = (cursor[1] - 1) % SIZE
            elif key in (curses.KEY_RIGHT, ord("l")):
                cursor[1] = (cursor[1] + 1) % SIZE
            elif key in (curses.KEY_ENTER, 10, 13, ord(" ")):
                if tuple(cursor) in legal:
                    board.play(cursor[0], cursor[1], turn)
                    turn = opponent(turn)
                else:
                    message = "そこには置けません"
            elif key in (ord("q"), ord("Q")):
                return
        else:
            message = "AIが考えています…"
            _draw_board(stdscr, board, tuple(cursor), legal, human_player, ai_level, message)
            move = ai.choose_move(board)
            if move is not None:
                board.play(*move, turn)
            turn = opponent(turn)

    winner = board.winner()
    if winner is None:
        result = "引き分けです"
    elif winner == human_player:
        result = "あなたの勝ちです！"
    else:
        result = "AIの勝ちです"
    _draw_board(stdscr, board, tuple(cursor), set(), human_player, ai_level, result)
    stdscr.addstr(
        SIZE + 8,
        4,
        "何かキーを押すと終了します",
        curses.color_pair(COLOR_STATUS),
    )
    stdscr.refresh()
    stdscr.getch()


