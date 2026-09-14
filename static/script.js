"use strict";

const API_URL = "/api/move";

const boardEl = document.getElementById("board");
const statusEl = document.getElementById("status");
const resetBtn = document.getElementById("reset");
const modeEl = document.getElementById("mode");
const difficultyEl = document.getElementById("difficulty");
const difficultyField = document.getElementById("difficulty-field");

/** クライアント側の状態 */
const state = {
  board: Array(9).fill(""),
  status: "playing", // playing | won | draw
  winner: null,
  line: [],
  mode: "cpu",
  difficulty: "hard",
  busy: false,
  error: null,
};

/* ------------------------------------------------------------------ */
/* ヘルパー                                                            */
/* ------------------------------------------------------------------ */

function nextPlayer(board) {
  const x = board.filter((c) => c === "X").length;
  const o = board.filter((c) => c === "O").length;
  return x === o ? "X" : "O";
}

function label(mark) {
  return mark === "X" ? "✕" : "◯";
}

/* ------------------------------------------------------------------ */
/* 描画                                                                */
/* ------------------------------------------------------------------ */

function render() {
  const cells = boardEl.children;

  for (let i = 0; i < 9; i += 1) {
    const cell = cells[i];
    const value = state.board[i];

    cell.textContent = value === "X" ? "✕" : value === "O" ? "◯" : "";
    cell.classList.toggle("x", value === "X");
    cell.classList.toggle("o", value === "O");
    cell.classList.toggle("win", state.line.includes(i));
    cell.disabled = state.busy || value !== "" || state.status !== "playing";
  }

  statusEl.classList.toggle("status--win", state.status === "won");

  if (state.error) {
    statusEl.textContent = state.error;
    return;
  }
  if (state.status === "won") {
    statusEl.textContent = `${label(state.winner)} の勝ち！`;
    return;
  }
  if (state.status === "draw") {
    statusEl.textContent = "引き分けです";
    return;
  }
  if (state.busy) {
    statusEl.textContent = "考え中…";
    return;
  }
  statusEl.textContent = `次は ${label(nextPlayer(state.board))} の番です`;
}

/* ------------------------------------------------------------------ */
/* ゲーム操作                                                          */
/* ------------------------------------------------------------------ */

async function play(index) {
  if (state.busy || state.status !== "playing" || state.board[index] !== "") {
    return;
  }

  const boardBefore = [...state.board];

  // 人間の手は先に反映してサクサク動かす
  state.board = boardBefore.map((cell, i) =>
    i === index ? nextPlayer(boardBefore) : cell
  );
  state.busy = true;
  state.error = null;
  render();

  try {
    const res = await fetch(API_URL, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        board: boardBefore,
        index,
        mode: state.mode,
        difficulty: state.difficulty,
      }),
    });

    const data = await res.json().catch(() => ({}));

    if (!res.ok) {
      throw new Error(data.error || "通信に失敗しました");
    }

    state.board = data.board;
    state.status = data.status;
    state.winner = data.winner;
    state.line = data.line || [];
  } catch (err) {
    // 失敗したら盤面を巻き戻す
    state.board = boardBefore;
    state.error = err.message || "エラーが発生しました";
  } finally {
    state.busy = false;
    render();
  }
}

function reset() {
  state.board = Array(9).fill("");
  state.status = "playing";
  state.winner = null;
  state.line = [];
  state.busy = false;
  state.error = null;
  render();
}

/* ------------------------------------------------------------------ */
/* イベント登録                                                        */
/* ------------------------------------------------------------------ */

boardEl.addEventListener("click", (event) => {
  const cell = event.target.closest(".cell");
  if (!cell) return;
  play(Number(cell.dataset.index));
});

resetBtn.addEventListener("click", reset);

modeEl.addEventListener("change", () => {
  state.mode = modeEl.value;
  difficultyField.hidden = state.mode !== "cpu";
  reset();
});

difficultyEl.addEventListener("change", () => {
  state.difficulty = difficultyEl.value;
  reset();
});

// 初期化
state.mode = modeEl.value;
state.difficulty = difficultyEl.value;
difficultyField.hidden = state.mode !== "cpu";
render();
