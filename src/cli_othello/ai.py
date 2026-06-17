"""5-level Othello AI using minimax with alpha-beta pruning.

Each level scales both the search depth and the sophistication of the
position evaluation, so higher levels look further ahead and judge
positions more accurately (corners, edges, mobility, stability).
"""

from __future__ import annotations

import random

from .board import BLACK, EMPTY, SIZE, WHITE, Board, opponent

# Static positional weights, used by the higher levels.
_POSITION_WEIGHTS = [
    120, -20, 20, 5, 5, 20, -20, 120,
    -20, -40, -5, -5, -5, -5, -40, -20,
    20, -5, 15, 3, 3, 15, -5, 20,
    5, -5, 3, 3, 3, 3, -5, 5,
    5, -5, 3, 3, 3, 3, -5, 5,
    20, -5, 15, 3, 3, 15, -5, 20,
    -20, -40, -5, -5, -5, -5, -40, -20,
    120, -20, 20, 5, 5, 20, -20, 120,
]

_CORNERS = [(0, 0), (0, SIZE - 1), (SIZE - 1, 0), (SIZE - 1, SIZE - 1)]

# level -> (search depth, randomness, use_positional_weights, use_mobility)
_LEVEL_CONFIG = {
    1: dict(depth=1, randomness=0.35, weights=False, mobility=False),
    2: dict(depth=2, randomness=0.15, weights=True, mobility=False),
    3: dict(depth=2, randomness=0.0, weights=True, mobility=True),
    4: dict(depth=3, randomness=0.0, weights=True, mobility=True),
    5: dict(depth=4, randomness=0.0, weights=True, mobility=True),
}

# Endgame solver: once few enough empty cells remain, search exhaustively
# to the end of the game instead of stopping at the configured depth.
_ENDGAME_EMPTY_THRESHOLD = {3: 8, 4: 9, 5: 10}

def _order_moves(moves: list[tuple[int, int]]) -> list[tuple[int, int]]:
    """Sort moves by static positional weight (best-first) to help alpha-beta
    pruning cut off more branches earlier."""
    return sorted(
        moves, key=lambda m: _POSITION_WEIGHTS[m[0] * SIZE + m[1]], reverse=True
    )


MIN_LEVEL = 1
MAX_LEVEL = 5


class OthelloAI:
    """Picks moves for `player` at the given difficulty level (1-5)."""

    def __init__(self, player: int, level: int) -> None:
        if level not in _LEVEL_CONFIG:
            raise ValueError(f"level must be between {MIN_LEVEL} and {MAX_LEVEL}")
        self.player = player
        self.level = level
        self.config = _LEVEL_CONFIG[level]

    def choose_move(self, board: Board) -> tuple[int, int] | None:
        moves = board.legal_moves(self.player)
        if not moves:
            return None

        if random.random() < self.config["randomness"]:
            return random.choice(moves)

        depth = self.config["depth"]
        empty_cells = board.cells.count(EMPTY)
        endgame_threshold = _ENDGAME_EMPTY_THRESHOLD.get(self.level)
        if endgame_threshold is not None and empty_cells <= endgame_threshold:
            depth = empty_cells

        moves = _order_moves(moves)
        best_score = None
        best_moves: list[tuple[int, int]] = []
        for move in moves:
            child = board.clone()
            child.play(*move, self.player)
            score = self._minimax(
                child, depth - 1, opponent(self.player), -float("inf"), float("inf")
            )
            if best_score is None or score > best_score:
                best_score = score
                best_moves = [move]
            elif score == best_score:
                best_moves.append(move)
        return random.choice(best_moves)

    def _minimax(
        self, board: Board, depth: int, turn: int, alpha: float, beta: float
    ) -> float:
        if depth <= 0 or board.is_game_over():
            return self._evaluate(board)

        moves = board.legal_moves(turn)
        if not moves:
            return self._minimax(board, depth - 1, opponent(turn), alpha, beta)

        moves = _order_moves(moves)
        maximizing = turn == self.player
        best = -float("inf") if maximizing else float("inf")
        for move in moves:
            child = board.clone()
            child.play(*move, turn)
            score = self._minimax(child, depth - 1, opponent(turn), alpha, beta)
            if maximizing:
                best = max(best, score)
                alpha = max(alpha, best)
            else:
                best = min(best, score)
                beta = min(beta, best)
            if alpha >= beta:
                break
        return best

    def _evaluate(self, board: Board) -> float:
        me, foe = self.player, opponent(self.player)

        if board.is_game_over():
            diff = board.count(me) - board.count(foe)
            return diff * 10000

        if not self.config["weights"]:
            return board.count(me) - board.count(foe)

        score = 0.0
        for row in range(SIZE):
            for col in range(SIZE):
                cell = board.get(row, col)
                if cell == me:
                    score += _POSITION_WEIGHTS[row * SIZE + col]
                elif cell == foe:
                    score -= _POSITION_WEIGHTS[row * SIZE + col]

        if self.config["mobility"]:
            my_moves = len(board.legal_moves(me))
            foe_moves = len(board.legal_moves(foe))
            score += (my_moves - foe_moves) * 8

            my_corners = sum(1 for r, c in _CORNERS if board.get(r, c) == me)
            foe_corners = sum(1 for r, c in _CORNERS if board.get(r, c) == foe)
            score += (my_corners - foe_corners) * 25

        return score


LEVEL_LABELS = {
    1: "Lv.1 入門",
    2: "Lv.2 初級",
    3: "Lv.3 中級",
    4: "Lv.4 上級",
    5: "Lv.5 最強",
}
