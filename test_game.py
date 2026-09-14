"""ゲームロジックのユニットテスト: pytest test_game.py"""

import game


def test_empty_board():
    board = game.empty_board()
    assert len(board) == 9
    assert board.count("") == 9


def test_next_player():
    board = game.empty_board()
    assert game.next_player(board) == "X"
    board[0] = "X"
    assert game.next_player(board) == "O"


def test_winner_row():
    board = ["X", "X", "X", "", "O", "", "O", "", ""]
    win, line = game.winner_of(board)
    assert win == "X"
    assert line == (0, 1, 2)


def test_winner_diagonal():
    board = ["O", "X", "X", "", "O", "", "", "", "O"]
    win, line = game.winner_of(board)
    assert win == "O"
    assert line == (0, 4, 8)


def test_draw():
    board = ["X", "O", "X", "X", "O", "O", "O", "X", "X"]
    assert game.winner_of(board)[0] is None
    assert game.status_of(board) == "draw"


def test_valid_board():
    assert game.is_valid_board(game.empty_board())
    assert game.is_valid_board(["X", "", "", "", "", "", "", "", ""])
    assert not game.is_valid_board(["O", "", "", "", "", "", "", "", ""])
    assert not game.is_valid_board(["X"] * 9)
    assert not game.is_valid_board(["Z"] + [""] * 8)
    assert not game.is_valid_board("not a board")


def test_ai_blocks_win():
    """AI が相手のリーチを止めること。"""
    board = ["X", "X", "", "", "O", "", "", "", ""]
    move = game.choose_ai_move(board, "O", "hard")
    assert move == 2


def test_ai_takes_win():
    """AI が勝てる手を選ぶこと。"""
    board = ["O", "O", "", "X", "X", "", "", "", ""]
    move = game.choose_ai_move(board, "O", "hard")
    assert move == 2


def test_ai_never_loses_as_first_player():
    """AI 先手（X）で、後手のランダムプレイに絶対に負けないこと。"""
    import random

    random.seed(0)
    for _ in range(50):
        board = game.empty_board()
        while game.status_of(board) == "playing":
            turn = game.next_player(board)
            if turn == "X":
                idx = game.choose_ai_move(board, "X", "hard")
            else:
                idx = random.choice(game.legal_moves(board))
            board[idx] = turn
        assert game.winner_of(board)[0] != "O"
