/** Core game types and pure logic utilities */

export type Player = "X" | "O";
export type CellValue = Player | null;
export type Board = CellValue[];
export type GameMode = "pvp" | "pvc";
export type Difficulty = "easy" | "medium" | "hard";

/** All 8 winning combinations */
export const WIN_LINES = [
  [0, 1, 2], // top row
  [3, 4, 5], // middle row
  [6, 7, 8], // bottom row
  [0, 3, 6], // left col
  [1, 4, 7], // middle col
  [2, 5, 8], // right col
  [0, 4, 8], // main diagonal
  [2, 4, 6], // anti-diagonal
] as const;

/** Returns the winning player and line indices, or null if no winner yet */
export function checkWinner(
  board: Board
): { winner: Player; line: number[] } | null {
  for (const [a, b, c] of WIN_LINES) {
    if (board[a] && board[a] === board[b] && board[a] === board[c]) {
      return { winner: board[a] as Player, line: [a, b, c] };
    }
  }
  return null;
}

/** True when all cells are filled and there is no winner */
export function isDraw(board: Board): boolean {
  return board.every((c) => c !== null) && !checkWinner(board);
}

/** Indices of empty cells */
export function emptyCells(board: Board): number[] {
  return board.reduce<number[]>((acc, cell, i) => {
    if (cell === null) acc.push(i);
    return acc;
  }, []);
}

/** Return a fresh blank board */
export function createBoard(): Board {
  return Array(9).fill(null);
}
