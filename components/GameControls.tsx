"use client";
/**
 * Game controls panel: game mode selector (PvP / PvC) and difficulty selector.
 * Difficulty row is only shown in PvC mode.
 */

import { motion, AnimatePresence } from "framer-motion";
import { GameMode, Difficulty } from "@/utils/gameLogic";

interface GameControlsProps {
  gameMode: GameMode;
  difficulty: Difficulty;
  onGameModeChange: (mode: GameMode) => void;
  onDifficultyChange: (diff: Difficulty) => void;
}

const MODES: { value: GameMode; label: string; icon: string }[] = [
  { value: "pvc", label: "vs AI", icon: "🤖" },
  { value: "pvp", label: "2 Players", icon: "👥" },
];

const DIFFICULTIES: {
  value: Difficulty;
  label: string;
  activeClass: string;
}[] = [
  {
    value: "easy",
    label: "Easy",
    activeClass:
      "border-neon-green/55 bg-neon-green/10 text-neon-green",
  },
  {
    value: "medium",
    label: "Medium",
    activeClass:
      "border-neon-yellow/55 bg-neon-yellow/10 text-neon-yellow",
  },
  {
    value: "hard",
    label: "Hard",
    activeClass:
      "border-neon-pink/55 bg-neon-pink/10 text-neon-pink",
  },
];

export function GameControls({
  gameMode,
  difficulty,
  onGameModeChange,
  onDifficultyChange,
}: GameControlsProps) {
  return (
    <div className="glass rounded-xl p-2 sm:p-3 flex flex-col gap-2">
      {/* Mode Row */}
      <div className="flex gap-2">
        {MODES.map((m) => {
          const active = gameMode === m.value;
          const activeCls =
            m.value === "pvc"
              ? "border-neon-cyan/50 bg-neon-cyan/10 text-neon-cyan"
              : "border-neon-purple/50 bg-neon-purple/10 text-neon-purple";
          return (
            <button
              key={m.value}
              onClick={() => onGameModeChange(m.value)}
              className={`flex-1 py-2 rounded-lg border font-mono text-xs font-bold transition-all duration-200
                ${active ? activeCls : "border-white/8 bg-white/[0.03] text-white/35 hover:text-white/60 hover:border-white/15"}`}
            >
              <span className="mr-1">{m.icon}</span>
              {m.label}
            </button>
          );
        })}
      </div>

      {/* Difficulty Row – only in PvC mode */}
      <AnimatePresence>
        {gameMode === "pvc" && (
          <motion.div
            key="difficulty"
            initial={{ opacity: 0, height: 0 }}
            animate={{ opacity: 1, height: "auto" }}
            exit={{ opacity: 0, height: 0 }}
            transition={{ duration: 0.2 }}
            className="flex gap-2 overflow-hidden"
          >
            {DIFFICULTIES.map((d) => {
              const active = difficulty === d.value;
              return (
                <button
                  key={d.value}
                  onClick={() => onDifficultyChange(d.value)}
                  className={`flex-1 py-1.5 rounded-lg border font-mono text-xs transition-all duration-200 capitalize
                    ${active ? d.activeClass : "border-white/8 bg-white/[0.03] text-white/30 hover:text-white/55"}`}
                >
                  {d.label}
                </button>
              );
            })}
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  );
}
