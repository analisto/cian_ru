"use client";
/**
 * A single Tic-Tac-Toe cell.
 * Shows a hover-preview of the current player's symbol when empty.
 * Animates the symbol in on placement.
 * Highlights winning cells with a gold glow.
 */

import { motion } from "framer-motion";
import { CellValue, Player } from "@/utils/gameLogic";

interface CellProps {
  value: CellValue;
  index: number;
  isWinning: boolean;
  disabled: boolean;
  currentPlayer: Player;
  onClick: () => void;
}

export function Cell({
  value,
  index,
  isWinning,
  disabled,
  currentPlayer,
  onClick,
}: CellProps) {
  const isEmpty = value === null;
  const canClick = isEmpty && !disabled;

  /* Derive border/bg classes based on state */
  let cellCls =
    "relative aspect-square flex items-center justify-center rounded-xl border transition-all duration-200 select-none ";

  if (isWinning) {
    cellCls +=
      "border-neon-yellow bg-dark-700 win-cell-glow cursor-default ";
  } else if (value === "X") {
    cellCls += "border-neon-cyan/35 bg-dark-700 cursor-default ";
  } else if (value === "O") {
    cellCls += "border-neon-purple/35 bg-dark-700 cursor-default ";
  } else if (canClick) {
    cellCls +=
      "border-dark-600 bg-dark-800 hover:border-neon-cyan/30 hover:bg-dark-700 cursor-pointer group ";
  } else {
    cellCls += "border-dark-600 bg-dark-800 cursor-not-allowed opacity-60 ";
  }

  return (
    <motion.button
      onClick={canClick ? onClick : undefined}
      whileTap={canClick ? { scale: 0.92 } : {}}
      className={cellCls}
      aria-label={`Cell ${index + 1}: ${value ?? "empty"}`}
      tabIndex={canClick ? 0 : -1}
    >
      {/* Ghost preview on hover */}
      {isEmpty && canClick && (
        <span
          className={`absolute inset-0 flex items-center justify-center text-3xl sm:text-4xl font-bold opacity-0 group-hover:opacity-20 transition-opacity pointer-events-none
            ${currentPlayer === "X" ? "text-neon-cyan" : "text-neon-purple"}`}
        >
          {currentPlayer}
        </span>
      )}

      {/* Placed symbol */}
      {value && (
        <motion.span
          initial={{ scale: 0, rotate: -18, opacity: 0 }}
          animate={{ scale: 1, rotate: 0, opacity: 1 }}
          transition={{ type: "spring", stiffness: 340, damping: 22 }}
          className={`text-3xl sm:text-4xl md:text-5xl font-bold leading-none
            ${
              isWinning
                ? value === "X"
                  ? "neon-text-cyan"
                  : "neon-text-purple"
                : value === "X"
                ? "text-neon-cyan drop-shadow-[0_0_8px_#00f5ff]"
                : "text-neon-purple drop-shadow-[0_0_8px_#bf00ff]"
            }`}
        >
          {value}
        </motion.span>
      )}
    </motion.button>
  );
}
