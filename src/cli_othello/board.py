"""Othello board representation and rules."""

from __future__ import annotations

SIZE = 8
EMPTY = 0
BLACK = 1
WHITE = 2

DIRECTIONS = [
    (-1, -1), (-1, 0), (-1, 1),
    (0, -1), (0, 1),
    (1, -1), (1, 0), (1, 1),
]


def opponent(player: int) -> int:
    return WHITE if player == BLACK else BLACK


class Board:
    """8x8 Othello board. Cells are stored as a flat list of length 64."""

    def __init__(self) -> None:
        self.cells = [EMPTY] * (SIZE * SIZE)
        mid = SIZE // 2
        self.cells[(mid - 1) * SIZE + (mid - 1)] = WHITE
        self.cells[(mid - 1) * SIZE + mid] = BLACK
        self.cells[mid * SIZE + (mid - 1)] = BLACK
        self.cells[mid * SIZE + mid] = WHITE

    def clone(self) -> "Board":
        new = Board.__new__(Board)
        new.cells = list(self.cells)
        return new

    @staticmethod
    def in_bounds(row: int, col: int) -> bool:
        return 0 <= row < SIZE and 0 <= col < SIZE

    def get(self, row: int, col: int) -> int:
        return self.cells[row * SIZE + col]

    def set(self, row: int, col: int, value: int) -> None:
        self.cells[row * SIZE + col] = value

    def _flips_for_move(self, row: int, col: int, player: int) -> list[tuple[int, int]]:
        if self.get(row, col) != EMPTY:
            return []
        rival = opponent(player)
        flips: list[tuple[int, int]] = []
        for dr, dc in DIRECTIONS:
            line: list[tuple[int, int]] = []
            r, c = row + dr, col + dc
            while self.in_bounds(r, c) and self.get(r, c) == rival:
                line.append((r, c))
                r, c = r + dr, c + dc
            if line and self.in_bounds(r, c) and self.get(r, c) == player:
                flips.extend(line)
        return flips

    def legal_moves(self, player: int) -> list[tuple[int, int]]:
        moves = []
        for row in range(SIZE):
            for col in range(SIZE):
                if self._flips_for_move(row, col, player):
                    moves.append((row, col))
        return moves

    def has_legal_move(self, player: int) -> bool:
        for row in range(SIZE):
            for col in range(SIZE):
                if self._flips_for_move(row, col, player):
                    return True
        return False

    def play(self, row: int, col: int, player: int) -> bool:
        flips = self._flips_for_move(row, col, player)
        if not flips:
            return False
        self.set(row, col, player)
        for r, c in flips:
            self.set(r, c, player)
        return True

    def count(self, player: int) -> int:
        return self.cells.count(player)

    def is_full(self) -> bool:
        return EMPTY not in self.cells

    def is_game_over(self) -> bool:
        if self.is_full():
            return True
        return not self.has_legal_move(BLACK) and not self.has_legal_move(WHITE)

    def winner(self) -> int | None:
        black, white = self.count(BLACK), self.count(WHITE)
        if black > white:
            return BLACK
        if white > black:
            return WHITE
        return None
