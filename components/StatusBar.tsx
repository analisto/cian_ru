"use client";
/**
 * One-line status bar below the board.
 * Shows whose turn it is, AI thinking state, paused state, or is hidden when game over.
 */

import { motion, AnimatePresence } from "framer-motion";
import { Player, GameMode } from "@/utils/gameLogic";

interface StatusBarProps {
  currentPlayer: Player;
  isGameOver: boolean;
  isPaused: boolean;
  isAIThinking: boolean;
  gameMode: GameMode;
  aiPlayer: Player;
}

export function StatusBar({
  currentPlayer,
  isGameOver,
  isPaused,
  isAIThinking,
  gameMode,
  aiPlayer,
}: StatusBarProps) {
  if (isGameOver) return null;

  let message = "";
  if (isPaused) {
    message = "⏸  PAUSED";
  } else if (isAIThinking) {
    message = "AI is calculating…";
  } else {
    const isAITurn = gameMode === "pvc" && currentPlayer === aiPlayer;
    const name = isAITurn
      ? "AI"
      : currentPlayer === "X"
      ? "Player X"
      : "Player O";
    message = `${name}'s turn`;
  }

  const colorCls =
    isPaused
      ? "text-neon-yellow"
      : isAIThinking
      ? "text-neon-purple/70"
      : currentPlayer === "X"
      ? "text-neon-cyan/70"
      : "text-neon-purple/70";

  return (
    <AnimatePresence mode="wait">
      <motion.p
        key={message}
        initial={{ opacity: 0, y: 4 }}
        animate={{ opacity: 1, y: 0 }}
        exit={{ opacity: 0, y: -4 }}
        transition={{ duration: 0.18 }}
        className={`text-center text-xs font-mono tracking-widest ${colorCls}`}
      >
        {message}
      </motion.p>
    </AnimatePresence>
  );
}
