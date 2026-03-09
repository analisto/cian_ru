/**
 * AI move selection.
 * Easy   – random empty cell.
 * Medium – wins if it can, blocks if opponent can win, then heuristic.
 * Hard   – unbeatable minimax with alpha-beta pruning.
 */

import {
  Board,
  Player,
  Difficulty,
  checkWinner,
  isDraw,
  emptyCells,
} from "./gameLogic";

/* ─── Easy ──────────────────────────────────────────── */
function randomMove(board: Board): number {
  const cells = emptyCells(board);
  return cells[Math.floor(Math.random() * cells.length)];
}

/* ─── Medium ────────────────────────────────────────── */
function mediumMove(board: Board, ai: Player): number {
  const opp: Player = ai === "O" ? "X" : "O";
  const cells = emptyCells(board);

  // 1. Winning move
  for (const i of cells) {
    const b = [...board];
    b[i] = ai;
    if (checkWinner(b)) return i;
  }
  // 2. Block opponent's winning move
  for (const i of cells) {
    const b = [...board];
    b[i] = opp;
    if (checkWinner(b)) return i;
  }
  // 3. Center
  if (board[4] === null) return 4;
  // 4. Random corner
  const corners = [0, 2, 6, 8].filter((i) => board[i] === null);
  if (corners.length) return corners[Math.floor(Math.random() * corners.length)];
  // 5. Any remaining
  return randomMove(board);
}

/* ─── Hard (Minimax + α-β pruning) ─────────────────── */
function minimax(
  board: Board,
  depth: number,
  isMax: boolean,
  ai: Player,
  alpha: number,
  beta: number
): number {
  const opp: Player = ai === "O" ? "X" : "O";
  const result = checkWinner(board);
  if (result) return result.winner === ai ? 10 - depth : depth - 10;
  if (isDraw(board)) return 0;

  const cells = emptyCells(board);
  if (isMax) {
    let best = -Infinity;
    for (const i of cells) {
      board[i] = ai;
      best = Math.max(best, minimax(board, depth + 1, false, ai, alpha, beta));
      board[i] = null;
      alpha = Math.max(alpha, best);
      if (beta <= alpha) break;
    }
    return best;
  } else {
    let best = Infinity;
    for (const i of cells) {
      board[i] = opp;
      best = Math.min(best, minimax(board, depth + 1, true, ai, alpha, beta));
      board[i] = null;
      beta = Math.min(beta, best);
      if (beta <= alpha) break;
    }
    return best;
  }
}

function hardMove(board: Board, ai: Player): number {
  const cells = emptyCells(board);
  let bestScore = -Infinity;
  let bestMove = cells[0];
  for (const i of cells) {
    board[i] = ai;
    const score = minimax(board, 0, false, ai, -Infinity, Infinity);
    board[i] = null;
    if (score > bestScore) {
      bestScore = score;
      bestMove = i;
    }
  }
  return bestMove;
}

/* ─── Public API ────────────────────────────────────── */
export function getAIMove(
  board: Board,
  ai: Player,
  difficulty: Difficulty
): number {
  const copy = [...board]; // protect original from minimax mutation
  switch (difficulty) {
    case "easy":   return randomMove(copy);
    case "medium": return mediumMove(copy, ai);
    case "hard":   return hardMove(copy, ai);
  }
}
