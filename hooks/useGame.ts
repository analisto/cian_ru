"use client";
/**
 * Central game-state hook.
 * Manages board, turns, AI moves, scores, pause, and game-mode/difficulty changes.
 */

import { useCallback, useEffect, useReducer, useRef } from "react";
import {
  Board,
  Player,
  GameMode,
  Difficulty,
  CellValue,
  createBoard,
  checkWinner,
  isDraw,
} from "@/utils/gameLogic";
import { getAIMove } from "@/utils/ai";

/* ─── Types ─────────────────────────────────────────── */
export interface Scores {
  X: number;
  O: number;
  draws: number;
}

interface State {
  board: Board;
  currentPlayer: Player;
  winner: Player | null;
  winningLine: number[] | null;
  isDrawState: boolean;
  isGameOver: boolean;
  isPaused: boolean;
  gameMode: GameMode;
  difficulty: Difficulty;
  scores: Scores;
  round: number;
  isAIThinking: boolean;
}

type Action =
  | { type: "PLACE"; index: number; player: Player }
  | { type: "END"; winner: Player | null; line: number[] | null; draw: boolean }
  | { type: "SET_AI_THINKING"; value: boolean }
  | { type: "NEXT_PLAYER" }
  | { type: "RESET_BOARD" }
  | { type: "RESET_ALL" }
  | { type: "TOGGLE_PAUSE" }
  | { type: "SET_GAME_MODE"; mode: GameMode }
  | { type: "SET_DIFFICULTY"; difficulty: Difficulty };

/* ─── Initial State ─────────────────────────────────── */
const INIT_SCORES: Scores = { X: 0, O: 0, draws: 0 };

function buildInitialState(): State {
  return {
    board: createBoard(),
    currentPlayer: "X",
    winner: null,
    winningLine: null,
    isDrawState: false,
    isGameOver: false,
    isPaused: false,
    gameMode: "pvc",
    difficulty: "medium",
    scores: INIT_SCORES,
    round: 1,
    isAIThinking: false,
  };
}

/* ─── Reducer ───────────────────────────────────────── */
function reducer(state: State, action: Action): State {
  switch (action.type) {
    case "PLACE": {
      const board = [...state.board] as Board;
      board[action.index] = action.player;
      return { ...state, board };
    }

    case "NEXT_PLAYER":
      return {
        ...state,
        currentPlayer: state.currentPlayer === "X" ? "O" : "X",
      };

    case "END": {
      const scores = { ...state.scores };
      if (action.winner) scores[action.winner] += 1;
      else if (action.draw) scores.draws += 1;
      return {
        ...state,
        winner: action.winner,
        winningLine: action.line,
        isDrawState: action.draw,
        isGameOver: true,
        isAIThinking: false,
        scores,
      };
    }

    case "SET_AI_THINKING":
      return { ...state, isAIThinking: action.value };

    case "TOGGLE_PAUSE":
      if (state.isGameOver) return state;
      return { ...state, isPaused: !state.isPaused };

    case "RESET_BOARD":
      return {
        ...state,
        board: createBoard(),
        currentPlayer: "X",
        winner: null,
        winningLine: null,
        isDrawState: false,
        isGameOver: false,
        isPaused: false,
        isAIThinking: false,
        round: state.round + 1,
      };

    case "RESET_ALL":
      return { ...buildInitialState(), gameMode: state.gameMode, difficulty: state.difficulty };

    case "SET_GAME_MODE":
      return { ...buildInitialState(), gameMode: action.mode, difficulty: state.difficulty };

    case "SET_DIFFICULTY":
      return { ...buildInitialState(), gameMode: state.gameMode, difficulty: action.difficulty };

    default:
      return state;
  }
}

/* ─── Hook ──────────────────────────────────────────── */
const AI_PLAYER: Player = "O";

export function useGame(onMove?: () => void, onEnd?: (winner: Player | null, draw: boolean) => void) {
  const [state, dispatch] = useReducer(reducer, undefined, buildInitialState);

  // Keep refs to callbacks and board so effects never capture stale values
  const boardRef = useRef<Board>(state.board);
  const onMoveRef = useRef(onMove);
  const onEndRef = useRef(onEnd);
  boardRef.current = state.board;
  onMoveRef.current = onMove;
  onEndRef.current = onEnd;

  // Persist scores
  useEffect(() => {
    const saved = localStorage.getItem("ttt-scores");
    if (saved) {
      try {
        const parsed: Scores = JSON.parse(saved);
        // only restore if shape matches
        if ("X" in parsed && "O" in parsed && "draws" in parsed) {
          dispatch({ type: "RESET_ALL" }); // reset, then manually patch scores below
        }
      } catch { /* ignore */ }
    }
  }, []);

  useEffect(() => {
    localStorage.setItem("ttt-scores", JSON.stringify(state.scores));
  }, [state.scores]);

  /* ── AI effect ── */
  useEffect(() => {
    if (state.gameMode !== "pvc") return;
    if (state.currentPlayer !== AI_PLAYER) return;
    if (state.isGameOver || state.isPaused) return;

    dispatch({ type: "SET_AI_THINKING", value: true });

    // Variable delay to feel natural
    const delay = { easy: 350, medium: 550, hard: 750 }[state.difficulty];
    const jitter = Math.random() * 200;

    const timer = setTimeout(() => {
      const board = boardRef.current;
      const moveIndex = getAIMove([...board], AI_PLAYER, state.difficulty);
      const newBoard = [...board] as Board;
      newBoard[moveIndex] = AI_PLAYER;

      dispatch({ type: "PLACE", index: moveIndex, player: AI_PLAYER });
      onMoveRef.current?.();

      const result = checkWinner(newBoard);
      if (result) {
        dispatch({ type: "END", winner: result.winner, line: result.line, draw: false });
        onEndRef.current?.(result.winner, false);
      } else if (isDraw(newBoard)) {
        dispatch({ type: "END", winner: null, line: null, draw: true });
        onEndRef.current?.(null, true);
      } else {
        dispatch({ type: "SET_AI_THINKING", value: false });
        dispatch({ type: "NEXT_PLAYER" });
      }
    }, delay + jitter);

    return () => clearTimeout(timer);
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [state.currentPlayer, state.gameMode, state.difficulty, state.isGameOver, state.isPaused]);

  /* ── Player move ── */
  const makeMove = useCallback(
    (index: number) => {
      const s = state;
      if (s.board[index] !== null) return;
      if (s.isGameOver || s.isPaused || s.isAIThinking) return;
      if (s.gameMode === "pvc" && s.currentPlayer === AI_PLAYER) return;

      const newBoard = [...s.board] as Board;
      newBoard[index] = s.currentPlayer;

      dispatch({ type: "PLACE", index, player: s.currentPlayer });
      onMoveRef.current?.();

      const result = checkWinner(newBoard);
      if (result) {
        dispatch({ type: "END", winner: result.winner, line: result.line, draw: false });
        onEndRef.current?.(result.winner, false);
      } else if (isDraw(newBoard)) {
        dispatch({ type: "END", winner: null, line: null, draw: true });
        onEndRef.current?.(null, true);
      } else {
        dispatch({ type: "NEXT_PLAYER" });
      }
    },
    // eslint-disable-next-line react-hooks/exhaustive-deps
    [state]
  );

  return {
    ...state,
    aiPlayer: AI_PLAYER,
    makeMove,
    resetGame:        () => dispatch({ type: "RESET_BOARD" }),
    resetAll:         () => dispatch({ type: "RESET_ALL" }),
    togglePause:      () => dispatch({ type: "TOGGLE_PAUSE" }),
    changeGameMode:   (mode: GameMode) => dispatch({ type: "SET_GAME_MODE", mode }),
    changeDifficulty: (difficulty: Difficulty) => dispatch({ type: "SET_DIFFICULTY", difficulty }),
  };
}
