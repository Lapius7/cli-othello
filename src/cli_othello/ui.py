"""curses-based terminal UI for cli-othello."""

from __future__ import annotations

import curses

from .ai import LEVEL_LABELS, MAX_LEVEL, MIN_LEVEL, OthelloAI
from .board import BLACK, EMPTY, SIZE, WHITE, Board, opponent

PLAYER_NAMES = {BLACK: "黒", WHITE: "白"}

# Each cell's interior is CELL_W columns x CELL_H rows, not counting the
# grid lines drawn around it, so it reads as roughly square in a terminal
# (chars are about twice as tall as wide). All glyphs used inside the grid
# are plain ASCII: full-width characters (e.g. "●", "○") have ambiguous
# display width and end up misaligned in many terminals/fonts, so discs
# are shown as a colored background plus a half-width letter instead.
CELL_W = 5
CELL_H = 2

DISC_BLACK = "@"
DISC_WHITE = "O"
HINT_MARK = "+"

# Box-drawing characters for the grid lines between cells.
_TL, _TR, _BL, _BR = "┌", "┐", "└", "┘"
_H, _V = "─", "│"
_T_DOWN, _T_UP, _T_RIGHT, _T_LEFT, _CROSS = "┬", "┴", "├", "┤", "┼"

COLOR_BOARD = 1
COLOR_BLACK = 2
COLOR_WHITE = 3
COLOR_CURSOR_EMPTY = 4
COLOR_CURSOR_BLACK = 5
COLOR_CURSOR_WHITE = 6
COLOR_HINT = 7
COLOR_HEADER = 8
COLOR_STATUS = 9
COLOR_PANEL = 10
COLOR_GRID = 11


def init_colors() -> None:
    curses.start_color()
    curses.use_default_colors()
    curses.init_pair(COLOR_BOARD, curses.COLOR_GREEN, curses.COLOR_GREEN)
    # Discs fill the whole cell with their own color for maximum visibility.
    curses.init_pair(COLOR_BLACK, curses.COLOR_WHITE, curses.COLOR_BLACK)
    curses.init_pair(COLOR_WHITE, curses.COLOR_BLACK, curses.COLOR_WHITE)
    curses.init_pair(COLOR_CURSOR_EMPTY, curses.COLOR_BLACK, curses.COLOR_YELLOW)
    curses.init_pair(COLOR_CURSOR_BLACK, curses.COLOR_YELLOW, curses.COLOR_BLACK)
    curses.init_pair(COLOR_CURSOR_WHITE, curses.COLOR_YELLOW, curses.COLOR_WHITE)
    curses.init_pair(COLOR_HINT, curses.COLOR_YELLOW, curses.COLOR_GREEN)
    curses.init_pair(COLOR_HEADER, curses.COLOR_CYAN, -1)
    curses.init_pair(COLOR_STATUS, curses.COLOR_YELLOW, -1)
    curses.init_pair(COLOR_PANEL, curses.COLOR_WHITE, -1)
    curses.init_pair(COLOR_GRID, curses.COLOR_GREEN, -1)


def select_level(stdscr: "curses._CursesWindow") -> int:
    """Let the user pick an AI difficulty level (1-5) with arrow keys."""
    level = 3
    curses.curs_set(0)
    required_rows = 5 + MAX_LEVEL + 3
    required_cols = 36
    while True:
        stdscr.erase()
        max_y, max_x = stdscr.getmaxyx()
        if max_y < required_rows or max_x < required_cols:
            _draw_too_small(stdscr)
            continue
        stdscr.addstr(1, 2, "CLI OTHELLO", curses.color_pair(COLOR_HEADER) | curses.A_BOLD)
        stdscr.addstr(3, 2, "対戦するAIの強さを選んでください", curses.A_BOLD)
        for i in range(MIN_LEVEL, MAX_LEVEL + 1):
            label = LEVEL_LABELS[i]
            if i == level:
                stdscr.addstr(5 + i, 2, "> ", curses.A_BOLD)
                stdscr.addstr(5 + i, 4, label, curses.A_REVERSE | curses.A_BOLD)
            else:
                stdscr.addstr(5 + i, 4, label, curses.A_NORMAL)
        stdscr.addstr(
            5 + MAX_LEVEL + 2,
            2,
            "↑/↓ で選択   Enter で決定   q で終了",
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


def _cell_fill_attr(cell: int, is_cursor: bool) -> int:
    """Background attribute that fills the whole cell (all CELL_H rows)."""
    if cell == BLACK:
        return curses.color_pair(COLOR_CURSOR_BLACK if is_cursor else COLOR_BLACK) | curses.A_BOLD
    if cell == WHITE:
        return curses.color_pair(COLOR_CURSOR_WHITE if is_cursor else COLOR_WHITE) | curses.A_BOLD
    if is_cursor:
        return curses.color_pair(COLOR_CURSOR_EMPTY) | curses.A_BOLD
    return curses.color_pair(COLOR_BOARD)


def _cell_center_attr(cell: int, is_cursor: bool, is_hint: bool) -> tuple[int, str]:
    """Return (attribute, character) for the center row of a cell."""
    fill = _cell_fill_attr(cell, is_cursor)
    if cell == BLACK:
        return fill, DISC_BLACK
    if cell == WHITE:
        return fill, DISC_WHITE
    if is_hint:
        attr = curses.color_pair(COLOR_CURSOR_EMPTY if is_cursor else COLOR_HINT) | curses.A_BOLD
        return attr, HINT_MARK
    return fill, " "


def _required_size() -> tuple[int, int]:
    """Return (rows, cols) needed to draw the board and panel, plus a
    1-line/1-column margin (curses can refuse writes to the very last
    row/column of the screen)."""
    grid_rows = 1 + SIZE * (CELL_H + 1)
    grid_cols = 1 + SIZE * (CELL_W + 1)
    row_label_w = 3
    rows = 3 + 1 + grid_rows + 6 + 1
    cols = 4 + row_label_w + grid_cols + 1
    return rows, cols


def _draw_too_small(stdscr: "curses._CursesWindow") -> None:
    rows, cols = _required_size()
    stdscr.erase()
    try:
        stdscr.addstr(0, 0, "ターミナルが小さすぎます。")
        stdscr.addstr(1, 0, f"必要サイズ: {cols}列 x {rows}行 以上")
        stdscr.addstr(2, 0, "ウィンドウを大きくしてください。何かキーを押すと終了します。")
    except curses.error:
        pass
    stdscr.refresh()
    stdscr.getch()


def _draw_board(
    stdscr: "curses._CursesWindow",
    board: Board,
    cursor: tuple[int, int],
    legal: set[tuple[int, int]],
    human_player: int,
    ai_level: int,
    message: str,
    top: int = 0,
) -> bool:
    """Draw the board. Returns False (and shows a hint) if the terminal is
    too small to fit it."""
    required_rows, required_cols = _required_size()
    max_y, max_x = stdscr.getmaxyx()
    if max_y < required_rows or max_x < required_cols:
        _draw_too_small(stdscr)
        return False

    stdscr.erase()
    stdscr.addstr(top, 2, "CLI OTHELLO", curses.color_pair(COLOR_HEADER) | curses.A_BOLD)
    stdscr.addstr(
        top + 1,
        2,
        f"AI: {LEVEL_LABELS[ai_level]}    あなた: {DISC_BLACK if human_player == BLACK else DISC_WHITE} {PLAYER_NAMES[human_player]}",
        curses.color_pair(COLOR_PANEL),
    )

    board_top = top + 3
    board_left = 4
    grid_attr = curses.color_pair(COLOR_GRID)
    row_label_w = 3

    # Column labels (A-H), centered above each cell (account for the
    # leading grid line and the row-label gutter).
    header = " " * row_label_w + " "
    for col in range(SIZE):
        header += "ABCDEFGH"[col].center(CELL_W) + " "
    stdscr.addstr(board_top, board_left, header, curses.A_BOLD)

    grid_top = board_top + 1
    grid_left = board_left + row_label_w
    grid_cols = 1 + SIZE * (CELL_W + 1)
    grid_rows = 1 + SIZE * (CELL_H + 1)
    board_width = row_label_w + grid_cols

    # Draw the grid lines (the lattice of cell borders) first.
    for r in range(SIZE + 1):
        y = grid_top + r * (CELL_H + 1)
        if r == 0:
            left, mid, right = _TL, _T_DOWN, _TR
        elif r == SIZE:
            left, mid, right = _BL, _T_UP, _BR
        else:
            left, mid, right = _T_RIGHT, _CROSS, _T_LEFT
        line = left + (_H * CELL_W + mid) * SIZE
        line = line[:-1] + right
        stdscr.addstr(y, grid_left, line, grid_attr)
        if r < SIZE:
            for line_offset in range(1, CELL_H + 1):
                y2 = y + line_offset
                stdscr.addstr(y2, grid_left, _V, grid_attr)
                stdscr.addstr(y2, grid_left + grid_cols - 1, _V, grid_attr)
                for c in range(1, SIZE):
                    x = grid_left + c * (CELL_W + 1)
                    stdscr.addstr(y2, x, _V, grid_attr)

    # Row labels (1-8), centered next to each cell.
    for row in range(SIZE):
        y = grid_top + 1 + row * (CELL_H + 1) + (CELL_H - 1) // 2
        stdscr.addstr(y, board_left, f"{row + 1:>2} ", curses.A_BOLD)

    # Fill each cell's interior (background + disc/hint glyph).
    for row in range(SIZE):
        cell_top = grid_top + 1 + row * (CELL_H + 1)
        for col in range(SIZE):
            cell = board.get(row, col)
            is_cursor = (row, col) == cursor
            is_hint = cell == EMPTY and (row, col) in legal
            x = grid_left + 1 + col * (CELL_W + 1)
            for line in range(CELL_H):
                y = cell_top + line
                if line == (CELL_H - 1) // 2:
                    attr, ch = _cell_center_attr(cell, is_cursor, is_hint)
                    text = ch.center(CELL_W)
                else:
                    attr = _cell_fill_attr(cell, is_cursor)
                    text = " " * CELL_W
                stdscr.addstr(y, x, text, attr)

    board_bottom = grid_top + grid_rows - 1
    panel_left = board_left
    panel_width = board_width

    you_mark = DISC_BLACK if human_player == BLACK else DISC_WHITE
    ai_mark = DISC_BLACK if human_player == WHITE else DISC_WHITE

    stdscr.addstr(board_bottom + 1, panel_left, "─" * panel_width, grid_attr)
    stdscr.addstr(
        board_bottom + 2,
        panel_left,
        f"{DISC_BLACK} 黒 {board.count(BLACK):>2}   {DISC_WHITE} 白 {board.count(WHITE):>2}"
        f"    あなた:{you_mark}  AI:{ai_mark}",
        curses.A_BOLD,
    )
    stdscr.addstr(board_bottom + 3, panel_left, "─" * panel_width, grid_attr)
    stdscr.addstr(
        board_bottom + 4, panel_left, message, curses.color_pair(COLOR_STATUS) | curses.A_BOLD
    )
    stdscr.addstr(
        board_bottom + 5,
        panel_left,
        "矢印キー/hjkl: 移動   Enter/Space: 着手   q: 終了",
        curses.color_pair(COLOR_STATUS),
    )
    stdscr.refresh()
    return True


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
            if not _draw_board(
                stdscr, board, tuple(cursor), legal, human_player, ai_level, message
            ):
                continue
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
            # If the terminal is too small, _draw_too_small() already
            # blocked on a keypress above; proceed with the AI move
            # regardless so the game keeps progressing once resized.
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

    while not _draw_board(
        stdscr, board, tuple(cursor), set(), human_player, ai_level, result
    ):
        pass

    max_y, max_x = stdscr.getmaxyx()
    footer_y = min(SIZE + 8, max_y - 1)
    try:
        stdscr.addstr(footer_y, 4, "何かキーを押すと終了します", curses.color_pair(COLOR_STATUS))
    except curses.error:
        pass
    stdscr.refresh()
    stdscr.getch()


