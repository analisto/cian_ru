"use client";
/**
 * Procedurally-generated sound effects via Web Audio API.
 * No external audio files required.
 * All sounds respect the user's sound-enabled preference (persisted in localStorage).
 */

import { useCallback, useEffect, useRef, useState } from "react";

export function useSound() {
  const [enabled, setEnabled] = useState(true);
  const ctxRef = useRef<AudioContext | null>(null);

  // Hydrate from localStorage
  useEffect(() => {
    const stored = localStorage.getItem("ttt-sound");
    if (stored !== null) setEnabled(stored === "true");
  }, []);

  /** Lazily create AudioContext on first user interaction */
  const ctx = useCallback((): AudioContext | null => {
    if (typeof window === "undefined") return null;
    if (!ctxRef.current) {
      try {
        ctxRef.current = new AudioContext();
      } catch {
        return null;
      }
    }
    return ctxRef.current;
  }, []);

  /** Low-level tone helper */
  const tone = useCallback(
    (
      freq: number,
      type: OscillatorType,
      duration: number,
      gainVal = 0.25,
      delay = 0
    ) => {
      if (!enabled) return;
      const c = ctx();
      if (!c) return;
      try {
        const osc = c.createOscillator();
        const g = c.createGain();
        osc.connect(g);
        g.connect(c.destination);
        osc.type = type;
        osc.frequency.setValueAtTime(freq, c.currentTime + delay);
        g.gain.setValueAtTime(gainVal, c.currentTime + delay);
        g.gain.exponentialRampToValueAtTime(
          0.0001,
          c.currentTime + delay + duration
        );
        osc.start(c.currentTime + delay);
        osc.stop(c.currentTime + delay + duration + 0.01);
      } catch {
        // silently ignore if audio is unavailable
      }
    },
    [enabled, ctx]
  );

  const playClick = useCallback(() => tone(900, "square", 0.06, 0.12), [tone]);

  const playMove = useCallback(() => tone(440, "sine", 0.12, 0.2), [tone]);

  const playWin = useCallback(() => {
    // Rising fanfare
    tone(523, "sine", 0.18, 0.3, 0);
    tone(659, "sine", 0.18, 0.3, 0.15);
    tone(784, "sine", 0.25, 0.3, 0.3);
    tone(1047, "sine", 0.3, 0.3, 0.48);
  }, [tone]);

  const playLose = useCallback(() => {
    tone(330, "sawtooth", 0.22, 0.25, 0);
    tone(277, "sawtooth", 0.22, 0.25, 0.2);
    tone(220, "sawtooth", 0.3, 0.25, 0.42);
  }, [tone]);

  const playDraw = useCallback(() => {
    tone(392, "triangle", 0.2, 0.2, 0);
    tone(392, "triangle", 0.2, 0.2, 0.22);
  }, [tone]);

  const toggle = useCallback(() => {
    setEnabled((prev) => {
      const next = !prev;
      localStorage.setItem("ttt-sound", String(next));
      return next;
    });
  }, []);

  return { enabled, toggle, playClick, playMove, playWin, playLose, playDraw };
}
