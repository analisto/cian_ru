"use client";
/**
 * Scoreboard showing X wins, draws, and O/AI wins.
 * Active player's card pulses to indicate whose turn it is.
 */

import { motion, AnimatePresence } from "framer-motion";
import { Player, GameMode } from "@/utils/gameLogic";
import { Scores } from "@/hooks/useGame";

interface ScoreBoardProps {
  scores: Scores;
  gameMode: GameMode;
  currentPlayer: Player;
  isGameOver: boolean;
  isAIThinking: boolean;
}

export function ScoreBoard({
  scores,
  gameMode,
  currentPlayer,
  isGameOver,
  isAIThinking,
}: ScoreBoardProps) {
  const xLabel = "Player X";
  const oLabel = gameMode === "pvc" ? "AI (O)" : "Player O";

  const xActive = !isGameOver && !isAIThinking && currentPlayer === "X";
  const oActive = !isGameOver && (isAIThinking || (!isGameOver && currentPlayer === "O"));

  return (
    <div className="glass rounded-xl p-2 sm:p-3">
      <div className="flex items-stretch gap-2">
        <ScoreCard
          label={xLabel}
          symbol="X"
          score={scores.X}
          color="cyan"
          isActive={xActive}
        />
        <div className="flex flex-col items-center justify-center px-2 py-1 rounded-lg bg-white/[0.03] border border-white/5 min-w-[52px]">
          <AnimatedScore value={scores.draws} className="text-lg font-bold font-mono text-white/35" />
          <span className="text-[9px] font-mono text-white/20 uppercase tracking-[0.15em] mt-0.5">
            Draw
          </span>
        </div>
        <ScoreCard
          label={oLabel}
          symbol="O"
          score={scores.O}
          color="purple"
          isActive={oActive}
        />
      </div>
    </div>
  );
}

/* ── Sub-components ────────────────────────────────── */

function ScoreCard({
  label,
  symbol,
  score,
  color,
  isActive,
}: {
  label: string;
  symbol: Player;
  score: number;
  color: "cyan" | "purple";
  isActive: boolean;
}) {
  const cyan = color === "cyan";
  const borderCls = isActive
    ? cyan
      ? "border-neon-cyan/50 bg-neon-cyan/8 glow-cyan"
      : "border-neon-purple/50 bg-neon-purple/8 glow-purple"
    : "border-white/5 bg-white/[0.03]";
  const textCls = cyan ? "text-neon-cyan" : "text-neon-purple";
  const labelCls = cyan ? "text-neon-cyan/55" : "text-neon-purple/55";

  return (
    <div
      className={`flex-1 flex flex-col items-center justify-center py-2 rounded-lg border transition-all duration-300 ${borderCls}`}
    >
      <AnimatedScore value={score} className={`text-xl font-bold font-mono ${textCls}`} />
      <span className={`text-[9px] font-mono uppercase tracking-[0.15em] mt-0.5 ${labelCls}`}>
        {label}
      </span>
      {/* Active dot pulse */}
      {isActive && (
        <motion.span
          animate={{ opacity: [1, 0.2, 1] }}
          transition={{ duration: 1.2, repeat: Infinity }}
          className={`w-1.5 h-1.5 rounded-full mt-1.5 ${cyan ? "bg-neon-cyan" : "bg-neon-purple"}`}
        />
      )}
    </div>
  );
}

function AnimatedScore({ value, className }: { value: number; className: string }) {
  return (
    <AnimatePresence mode="wait">
      <motion.span
        key={value}
        initial={{ y: -10, opacity: 0 }}
        animate={{ y: 0, opacity: 1 }}
        exit={{ y: 10, opacity: 0 }}
        transition={{ duration: 0.2 }}
        className={className}
      >
        {value}
      </motion.span>
    </AnimatePresence>
  );
}
