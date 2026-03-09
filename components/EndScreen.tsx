"use client";
/**
 * Full-screen overlay shown when the game ends.
 * Displays winner / draw message with animated entrance, confetti-style particles,
 * and Play Again / Reset All buttons.
 */

import { motion } from "framer-motion";
import { Player, GameMode } from "@/utils/gameLogic";

interface EndScreenProps {
  winner: Player | null;
  isDraw: boolean;
  gameMode: GameMode;
  aiPlayer: Player;
  onRestart: () => void;
  onResetAll: () => void;
}

type ResultConfig = {
  title: string;
  subtitle: string;
  emoji: string;
  glowCls: string;
  symbolCls: string;
};

function getConfig(
  winner: Player | null,
  isDraw: boolean,
  gameMode: GameMode,
  aiPlayer: Player
): ResultConfig {
  if (isDraw) {
    return {
      title: "IT'S A DRAW",
      subtitle: "Nobody wins this round",
      emoji: "🤝",
      glowCls: "text-neon-yellow",
      symbolCls: "",
    };
  }
  if (gameMode === "pvp") {
    return {
      title: `PLAYER ${winner} WINS!`,
      subtitle: "Dominant performance!",
      emoji: "🏆",
      glowCls: winner === "X" ? "neon-text-cyan" : "neon-text-purple",
      symbolCls: winner === "X" ? "neon-text-cyan" : "neon-text-purple",
    };
  }
  // PvC
  if (winner !== aiPlayer) {
    return {
      title: "YOU WIN!",
      subtitle: "You outsmarted the AI!",
      emoji: "🎉",
      glowCls: "text-neon-green drop-shadow-[0_0_12px_#00ff88]",
      symbolCls: winner === "X" ? "neon-text-cyan" : "neon-text-purple",
    };
  }
  return {
    title: "AI WINS",
    subtitle: "Better luck next time…",
    emoji: "🤖",
    glowCls: "text-neon-pink drop-shadow-[0_0_12px_#ff0080]",
    symbolCls: winner === "X" ? "neon-text-cyan" : "neon-text-purple",
  };
}

/* Floating particle for visual flair */
function Particle({ i }: { i: number }) {
  const colors = ["#00f5ff", "#bf00ff", "#ff0080", "#00ff88", "#ffe600"];
  const color = colors[i % colors.length];
  const x = (((i * 137.5) % 100) - 50) * 2;
  const y = -80 - (i % 5) * 40;
  return (
    <motion.span
      className="absolute w-1.5 h-1.5 rounded-full pointer-events-none"
      style={{ background: color, top: "50%", left: "50%" }}
      initial={{ x: 0, y: 0, opacity: 1, scale: 1 }}
      animate={{ x, y, opacity: 0, scale: 0.3 }}
      transition={{ duration: 1.2 + (i % 3) * 0.3, delay: i * 0.05, ease: "easeOut" }}
    />
  );
}

export function EndScreen({
  winner,
  isDraw,
  gameMode,
  aiPlayer,
  onRestart,
  onResetAll,
}: EndScreenProps) {
  const cfg = getConfig(winner, isDraw, gameMode, aiPlayer);

  return (
    <motion.div
      initial={{ opacity: 0 }}
      animate={{ opacity: 1 }}
      exit={{ opacity: 0 }}
      className="fixed inset-0 z-50 flex items-center justify-center bg-dark-950/92 backdrop-blur-md p-4"
    >
      <motion.div
        initial={{ scale: 0.55, opacity: 0, y: 40 }}
        animate={{ scale: 1, opacity: 1, y: 0 }}
        exit={{ scale: 0.55, opacity: 0, y: 40 }}
        transition={{ type: "spring", stiffness: 280, damping: 22 }}
        className="glass rounded-2xl p-6 sm:p-8 text-center max-w-xs w-full border border-white/10 relative overflow-hidden"
      >
        {/* Particles */}
        <div className="absolute inset-0 pointer-events-none">
          {Array.from({ length: 16 }, (_, i) => (
            <Particle key={i} i={i} />
          ))}
        </div>

        {/* Emoji */}
        <motion.div
          animate={{ rotate: [0, -12, 12, -8, 8, 0], scale: [1, 1.25, 1] }}
          transition={{ delay: 0.3, duration: 0.9 }}
          className="text-5xl mb-3"
        >
          {cfg.emoji}
        </motion.div>

        {/* Title */}
        <motion.h2
          initial={{ opacity: 0, y: 14 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.15 }}
          className={`text-2xl sm:text-3xl font-bold font-mono mb-1 ${cfg.glowCls}`}
        >
          {cfg.title}
        </motion.h2>

        {/* Subtitle */}
        <motion.p
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ delay: 0.3 }}
          className="text-dark-300 text-xs font-mono mb-5"
        >
          {cfg.subtitle}
        </motion.p>

        {/* Winner symbol badge */}
        {winner && (
          <motion.div
            initial={{ scale: 0 }}
            animate={{ scale: 1 }}
            transition={{ delay: 0.25, type: "spring", stiffness: 260 }}
            className={`text-5xl font-bold mb-6 ${cfg.symbolCls}`}
          >
            {winner}
          </motion.div>
        )}

        {/* Action buttons */}
        <div className="flex gap-3">
          <motion.button
            whileHover={{ scale: 1.04 }}
            whileTap={{ scale: 0.96 }}
            onClick={onRestart}
            className="flex-1 py-3 rounded-xl border border-neon-cyan/50 bg-neon-cyan/12 text-neon-cyan font-mono text-sm font-bold hover:bg-neon-cyan/22 transition-all"
          >
            PLAY AGAIN
          </motion.button>
          <motion.button
            whileHover={{ scale: 1.04 }}
            whileTap={{ scale: 0.96 }}
            onClick={onResetAll}
            className="flex-1 py-3 rounded-xl border border-white/10 bg-white/[0.04] text-white/40 font-mono text-sm hover:bg-white/8 hover:text-white/60 transition-all"
          >
            RESET ALL
          </motion.button>
        </div>
      </motion.div>
    </motion.div>
  );
}
