"use client";
/**
 * 3×3 game board.
 * Renders Cell components and shows an "AI thinking" overlay while the AI calculates.
 */

import { motion } from "framer-motion";
import { Board as BoardType, Player } from "@/utils/gameLogic";
import { Cell } from "./Cell";

interface BoardProps {
  board: BoardType;
  winningLine: number[] | null;
  isGameOver: boolean;
  isAIThinking: boolean;
  isPaused: boolean;
  currentPlayer: Player;
  onCellClick: (index: number) => void;
}

export function Board({
  board,
  winningLine,
  isGameOver,
  isAIThinking,
  isPaused,
  currentPlayer,
  onCellClick,
}: BoardProps) {
  const disabled = isGameOver || isPaused || isAIThinking;

  return (
    <div className="relative w-full">
      {/* AI thinking indicator */}
      {isAIThinking && (
        <motion.div
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          exit={{ opacity: 0 }}
          className="absolute inset-0 z-10 flex flex-col items-center justify-center rounded-2xl bg-dark-900/70 backdrop-blur-sm pointer-events-none"
        >
          <p className="text-neon-purple text-xs font-mono mb-2 tracking-widest uppercase">
            AI thinking
          </p>
          <div className="flex gap-1.5">
            {[0, 1, 2].map((i) => (
              <motion.span
                key={i}
                className="w-2 h-2 rounded-full bg-neon-purple"
                animate={{ y: [0, -8, 0] }}
                transition={{
                  duration: 0.55,
                  delay: i * 0.14,
                  repeat: Infinity,
                  ease: "easeInOut",
                }}
              />
            ))}
          </div>
        </motion.div>
      )}

      {/* 3×3 grid */}
      <div className="grid grid-cols-3 gap-2 sm:gap-3">
        {board.map((cell, index) => (
          <Cell
            key={index}
            value={cell}
            index={index}
            isWinning={winningLine?.includes(index) ?? false}
            disabled={disabled}
            currentPlayer={currentPlayer}
            onClick={() => onCellClick(index)}
          />
        ))}
      </div>
    </div>
  );
}
