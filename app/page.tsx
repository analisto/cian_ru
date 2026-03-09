"use client";
/**
 * Root page – orchestrates the full Tic-Tac-Toe game.
 * Composes hooks and components; wires up sound callbacks.
 */

import { useRef } from "react";
import { AnimatePresence, motion } from "framer-motion";
import { Player } from "@/utils/gameLogic";
import { useGame } from "@/hooks/useGame";
import { useSound } from "@/hooks/useSound";
import { Header } from "@/components/Header";
import { GameControls } from "@/components/GameControls";
import { ScoreBoard } from "@/components/ScoreBoard";
import { Board } from "@/components/Board";
import { StatusBar } from "@/components/StatusBar";
import { EndScreen } from "@/components/EndScreen";

export default function TicTacToePage() {
  const sound = useSound();

  /**
   * Use refs so the callbacks passed to useGame always read the latest
   * game state without triggering effect re-runs on every render.
   */
  const gameModeRef = useRef<"pvp" | "pvc">("pvc");
  const aiPlayerRef = useRef<Player>("O");

  const game = useGame(
    /* onMove */ () => sound.playMove(),
    /* onEnd  */ (winner: Player | null, draw: boolean) => {
      if (draw) {
        sound.playDraw();
      } else if (gameModeRef.current === "pvc" && winner === aiPlayerRef.current) {
        sound.playLose();
      } else {
        sound.playWin();
      }
    }
  );

  // Keep refs in sync with current game state every render
  gameModeRef.current = game.gameMode;
  aiPlayerRef.current = game.aiPlayer;

  const click = (fn: () => void) => () => {
    sound.playClick();
    fn();
  };

  return (
    <main className="min-h-screen bg-dark-900 flex flex-col items-center justify-start py-4 px-3 sm:py-6 sm:px-4 overflow-x-hidden">
      {/* Ambient radial glow */}
      <div
        aria-hidden
        className="fixed inset-0 pointer-events-none"
        style={{
          background:
            "radial-gradient(ellipse 80% 50% at 50% -5%, rgba(0,245,255,0.07) 0%, transparent 70%)",
        }}
      />
      {/* Subtle dot grid */}
      <div
        aria-hidden
        className="fixed inset-0 pointer-events-none"
        style={{
          backgroundImage:
            "radial-gradient(circle, rgba(255,255,255,0.07) 1px, transparent 1px)",
          backgroundSize: "30px 30px",
          opacity: 0.25,
        }}
      />

      {/* ── Game layout ── */}
      <div className="relative z-10 w-full max-w-sm flex flex-col gap-3 sm:gap-4">
        <Header
          round={game.round}
          isPaused={game.isPaused}
          isGameOver={game.isGameOver}
          soundEnabled={sound.enabled}
          onTogglePause={click(game.togglePause)}
          onToggleSound={click(sound.toggle)}
        />

        <GameControls
          gameMode={game.gameMode}
          difficulty={game.difficulty}
          onGameModeChange={(mode) => { sound.playClick(); game.changeGameMode(mode); }}
          onDifficultyChange={(diff) => { sound.playClick(); game.changeDifficulty(diff); }}
        />

        <ScoreBoard
          scores={game.scores}
          gameMode={game.gameMode}
          currentPlayer={game.currentPlayer}
          isGameOver={game.isGameOver}
          isAIThinking={game.isAIThinking}
        />

        <Board
          board={game.board}
          winningLine={game.winningLine}
          isGameOver={game.isGameOver}
          isAIThinking={game.isAIThinking}
          isPaused={game.isPaused}
          currentPlayer={game.currentPlayer}
          onCellClick={(i) => { sound.playClick(); game.makeMove(i); }}
        />

        <StatusBar
          currentPlayer={game.currentPlayer}
          isGameOver={game.isGameOver}
          isPaused={game.isPaused}
          isAIThinking={game.isAIThinking}
          gameMode={game.gameMode}
          aiPlayer={game.aiPlayer}
        />

        <motion.button
          whileHover={{ opacity: 0.75 }}
          onClick={click(game.resetAll)}
          className="text-[10px] font-mono text-dark-400 hover:text-dark-300 transition-colors underline decoration-dashed text-center"
        >
          Reset all scores
        </motion.button>
      </div>

      {/* ── End Screen ── */}
      <AnimatePresence>
        {game.isGameOver && (
          <EndScreen
            winner={game.winner}
            isDraw={game.isDrawState}
            gameMode={game.gameMode}
            aiPlayer={game.aiPlayer}
            onRestart={click(game.resetGame)}
            onResetAll={click(game.resetAll)}
          />
        )}
      </AnimatePresence>

      {/* ── Pause Overlay ── */}
      <AnimatePresence>
        {game.isPaused && !game.isGameOver && (
          <motion.div
            key="pause-overlay"
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            className="fixed inset-0 z-40 flex items-center justify-center bg-dark-950/88 backdrop-blur-sm"
            onClick={click(game.togglePause)}
          >
            <motion.div
              initial={{ scale: 0.82, opacity: 0 }}
              animate={{ scale: 1, opacity: 1 }}
              exit={{ scale: 0.82, opacity: 0 }}
              transition={{ type: "spring", stiffness: 290, damping: 24 }}
              className="glass rounded-2xl px-10 py-8 text-center border border-white/10"
              onClick={(e) => e.stopPropagation()}
            >
              <div className="text-5xl mb-4">⏸</div>
              <h2 className="text-2xl font-bold font-mono text-white tracking-[0.18em] mb-1">
                PAUSED
              </h2>
              <p className="text-dark-400 text-xs font-mono mb-6">
                Tap anywhere or click Resume to continue
              </p>
              <motion.button
                whileHover={{ scale: 1.04 }}
                whileTap={{ scale: 0.96 }}
                onClick={click(game.togglePause)}
                className="px-8 py-3 rounded-xl border border-neon-green/50 bg-neon-green/10 text-neon-green font-mono text-sm font-bold hover:bg-neon-green/20 transition-all"
              >
                RESUME
              </motion.button>
            </motion.div>
          </motion.div>
        )}
      </AnimatePresence>
    </main>
  );
}
