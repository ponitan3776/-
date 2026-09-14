"""まるばつゲームのコアロジック（Web フレームワークに依存しない）"""

from __future__ import annotations

import random
from typing import Optional

EMPTY = ""
X = "X"
O = "O"
MARKS = (X, O)

# 勝利パターン（盤面インデックス）
WIN_LINES = (
    (0, 1, 2), (3, 4, 5), (6, 7, 8),  # 横
    (0, 3, 6), (1, 4, 7), (2, 5, 8),  # 縦
    (0, 4, 8), (2, 4, 6),             # 斜め
)

DIFFICULTIES = ("easy", "normal", "hard")


def empty_board() -> list[str]:
    """空の盤面（長さ 9）を返す。"""
    return [EMPTY] * 9


def other(mark: str) -> str:
    """X なら O、O なら X を返す。"""
    return O if mark == X else X


def next_player(board: list[str]) -> str:
    """次に打つプレイヤー。X が先手。"""
    return X if board.count(X) == board.count(O) else O


def winner_of(board: list[str]) -> tuple[Optional[str], Optional[tuple[int, int, int]]]:
    """勝者と勝利ラインを返す。決着していなければ (None, None)。"""
    for a, b, c in WIN_LINES:
        if board[a] != EMPTY and board[a] == board[b] == board[c]:
            return board[a], (a, b, c)
    return None, None


def is_full(board: list[str]) -> bool:
    return EMPTY not in board


def legal_moves(board: list[str]) -> list[int]:
    return [i for i, cell in enumerate(board) if cell == EMPTY]


def is_valid_board(board) -> bool:
    """受け取った盤面がまるばつゲームとして妥当かチェックする。"""
    if not isinstance(board, list) or len(board) != 9:
        return False
    if any(cell not in (EMPTY, X, O) for cell in board):
        return False
    nx, no = board.count(X), board.count(O)
    # X が先手なので、X の数は O と同じか 1 つ多い
    return nx == no or nx == no + 1


def status_of(board: list[str]) -> str:
    """'playing' / 'won' / 'draw' を返す。"""
    win, _ = winner_of(board)
    if win is not None:
        return "won"
    if is_full(board):
        return "draw"
    return "playing"


# ---------------------------------------------------------------------------
# AI
# ---------------------------------------------------------------------------

def choose_ai_move(board: list[str], ai_mark: str, difficulty: str = "hard") -> Optional[int]:
    """AI の着手位置を返す。打てるマスがなければ None。"""
    moves = legal_moves(board)
    if not moves:
        return None

    if difficulty == "easy":
        return random.choice(moves)

    if difficulty == "normal" and random.random() < 0.4:
        return random.choice(moves)

    # 初手はランダムに散らして毎回同じ展開にならないようにする
    if len(moves) == 9:
        return random.choice([0, 2, 4, 6, 8])

    _, index = _search(list(board), ai_mark, ai_mark, 0)
    return index


def _search(board: list[str], turn: str, ai_mark: str, depth: int):
    """ミニマックス法（αβ探索なし・9マスなので十分高速）。"""
    win, _ = winner_of(board)
    if win == ai_mark:
        return 10 - depth, None
    if win is not None:
        return depth - 10, None

    moves = legal_moves(board)
    if not moves:
        return 0, None

    maximizing = turn == ai_mark
    best_score = float("-inf") if maximizing else float("inf")
    best_index = moves[0]

    for i in moves:
        board[i] = turn
        score, _ = _search(board, other(turn), ai_mark, depth + 1)
        board[i] = EMPTY

        if maximizing and score > best_score:
            best_score, best_index = score, i
        elif not maximizing and score < best_score:
            best_score, best_index = score, i

    return best_score, best_index
