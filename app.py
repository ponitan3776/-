"""まるばつゲームの Web アプリ（Flask）。"""

from __future__ import annotations

from flask import Flask, jsonify, render_template, request

import game

app = Flask(__name__)
app.config["JSON_AS_ASCII"] = False  # 日本語をそのまま返す


@app.get("/")
def index():
    """ゲーム画面を返す。"""
    return render_template("index.html")


@app.get("/healthz")
def healthz():
    """Render のヘルスチェック用。"""
    return "ok", 200


@app.post("/api/move")
def api_move():
    """
    人間の一手（＋CPU モードなら AI の応手）を適用した盤面を返す。

    リクエスト JSON:
        {
            "board": ["", "", "", ...],   # 長さ 9、人間が打つ前の盤面
            "index": 4,                    # 人間が打つマス (0-8)
            "mode": "cpu" | "pvp",
            "difficulty": "easy" | "normal" | "hard"
        }
    """
    data = request.get_json(silent=True) or {}

    board = data.get("board")
    index = data.get("index")
    mode = data.get("mode", "cpu")
    difficulty = data.get("difficulty", "hard")

    # --- バリデーション -------------------------------------------------
    if not game.is_valid_board(board):
        return jsonify(error="盤面が不正です"), 400

    board = list(board)  # コピーしてからいじる

    if mode not in ("cpu", "pvp"):
        mode = "cpu"
    if difficulty not in game.DIFFICULTIES:
        difficulty = "hard"

    if game.status_of(board) != "playing":
        return jsonify(error="このゲームはすでに終了しています"), 400

    if not isinstance(index, int) or isinstance(index, bool) or not (0 <= index < 9):
        return jsonify(error="マスの指定が不正です"), 400

    if board[index] != game.EMPTY:
        return jsonify(error="そのマスにはすでに置かれています"), 400

    # --- 人間の手を適用 -------------------------------------------------
    human_mark = game.next_player(board)
    board[index] = human_mark

    ai_move = None

    # --- CPU の応手 -----------------------------------------------------
    if mode == "cpu" and game.status_of(board) == "playing":
        ai_mark = game.other(human_mark)
        ai_move = game.choose_ai_move(board, ai_mark, difficulty)
        if ai_move is not None:
            board[ai_move] = ai_mark

    # --- 結果をまとめて返す ---------------------------------------------
    status = game.status_of(board)
    winner, line = game.winner_of(board)

    return jsonify(
        board=board,
        status=status,                                   # playing / won / draw
        winner=winner,                                   # "X" / "O" / None
        line=list(line) if line else None,               # 勝利ライン
        aiMove=ai_move,                                  # AI が打ったマス
        nextPlayer=game.next_player(board) if status == "playing" else None,
    )


@app.errorhandler(404)
def not_found(_e):
    return jsonify(error="Not Found"), 404


@app.errorhandler(500)
def server_error(_e):
    return jsonify(error="サーバーエラーが発生しました"), 500


if __name__ == "__main__":
    # ローカル開発用: python app.py
    app.run(host="0.0.0.0", port=5000, debug=True)
