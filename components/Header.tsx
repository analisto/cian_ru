"use client";
/**
 * Page header: game title, round counter, pause button, and sound toggle.
 */

import { motion } from "framer-motion";

interface HeaderProps {
  round: number;
  isPaused: boolean;
  isGameOver: boolean;
  soundEnabled: boolean;
  onTogglePause: () => void;
  onToggleSound: () => void;
}

export function Header({
  round,
  isPaused,
  isGameOver,
  soundEnabled,
  onTogglePause,
  onToggleSound,
}: HeaderProps) {
  return (
    <header className="flex items-center justify-between">
      {/* Title */}
      <div>
        <h1 className="text-xl sm:text-2xl font-bold font-mono tracking-[0.18em] text-white leading-none">
          TIC
          <span className="neon-text-cyan">TAC</span>
          TOE
        </h1>
        <p className="text-[10px] font-mono text-dark-400 tracking-widest mt-0.5">
          ROUND {round}
        </p>
      </div>

      {/* Controls */}
      <div className="flex items-center gap-2">
        <IconButton
          label={soundEnabled ? "Mute sound" : "Unmute sound"}
          active={soundEnabled}
          activeColor="cyan"
          onClick={onToggleSound}
        >
          {soundEnabled ? "🔊" : "🔇"}
        </IconButton>

        {!isGameOver && (
          <IconButton
            label={isPaused ? "Resume game" : "Pause game"}
            active={isPaused}
            activeColor="green"
            onClick={onTogglePause}
          >
            {isPaused ? "▶" : "⏸"}
          </IconButton>
        )}
      </div>
    </header>
  );
}

function IconButton({
  children,
  label,
  active,
  activeColor,
  onClick,
}: {
  children: React.ReactNode;
  label: string;
  active: boolean;
  activeColor: "cyan" | "green";
  onClick: () => void;
}) {
  const colors = {
    cyan: "border-neon-cyan/45 bg-neon-cyan/10 text-neon-cyan",
    green: "border-neon-green/45 bg-neon-green/10 text-neon-green",
  };

  return (
    <motion.button
      whileHover={{ scale: 1.08 }}
      whileTap={{ scale: 0.92 }}
      onClick={onClick}
      aria-label={label}
      title={label}
      className={`w-9 h-9 rounded-lg border flex items-center justify-center text-base transition-all duration-200
        ${active ? colors[activeColor] : "border-white/8 bg-white/[0.03] text-white/35 hover:border-white/20 hover:text-white/60"}`}
    >
      {children}
    </motion.button>
  );
}
