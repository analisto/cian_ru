# TicTacToe – Neon Edition

A polished, full-stack Tic-Tac-Toe browser game built with **Next.js 16**, **TypeScript**, and **Tailwind CSS v4**. Features an unbeatable AI, smooth animations, procedural sound effects, and a cyberpunk neon aesthetic.

---

## Features

| Feature | Detail |
|---|---|
| 🤖 AI Opponent | Easy (random) · Medium (heuristic) · Hard (unbeatable minimax + α-β pruning) |
| 👥 Two-Player Mode | Local PvP on the same device |
| 🎨 Neon Cyberpunk Theme | Glassmorphism panels, cyan/purple glow, dot-grid background |
| 🎞 Animations | framer-motion spring pop-ins, score counter flips, particle burst on end screen |
| 🔊 Sound Effects | Procedural Web Audio API tones – no external audio files |
| 💾 Persistent Scores | Win/draw/loss tallies saved to `localStorage` |
| ⏸ Pause / Resume | Freeze the game at any time with animated overlay |
| 📱 Mobile-First | Fully responsive; touch-friendly cells; no horizontal scroll |
| ♿ Accessible | ARIA labels on every cell and button; keyboard-navigable |
| 🚀 Vercel-Ready | Static export, zero extra configuration needed |

---

## Tech Stack

- **Framework** – [Next.js 16](https://nextjs.org/) (App Router)
- **Language** – TypeScript (strict mode)
- **Styling** – [Tailwind CSS v4](https://tailwindcss.com/) (CSS-first config via `@theme` / `@utility`)
- **Animations** – [framer-motion](https://www.framer.com/motion/)
- **Audio** – Web Audio API (no external files)
- **State** – `useReducer` + `useRef` (no external state library)

---

## Project Structure

```
├── app/
│   ├── icon.svg          # SVG favicon (auto-detected by Next.js App Router)
│   ├── globals.css       # Tailwind v4 tokens, custom utilities, keyframes
│   ├── layout.tsx        # Root layout + viewport meta
│   └── page.tsx          # Main game page ("use client")
│
├── components/
│   ├── Header.tsx        # Title, round counter, pause & sound toggles
│   ├── GameControls.tsx  # PvP / vs-AI tabs + difficulty selector
│   ├── ScoreBoard.tsx    # Live score cards with active-player pulse
│   ├── Board.tsx         # 3×3 grid + AI-thinking overlay
│   ├── Cell.tsx          # Single cell: hover ghost, spring animation, win glow
│   ├── StatusBar.tsx     # Turn / AI-thinking / paused status line
│   └── EndScreen.tsx     # Result modal: emoji, title, particle burst, buttons
│
├── hooks/
│   ├── useGame.ts        # useReducer state machine; AI fires via useEffect + boardRef
│   └── useSound.ts       # Procedural sound effects; preference persisted in localStorage
│
└── utils/
    ├── gameLogic.ts      # Types, WIN_LINES, checkWinner, isDraw, emptyCells
    └── ai.ts             # getAIMove – easy / medium / hard implementations
```

---

## Getting Started

```bash
# Install dependencies
npm install

# Start development server
npm run dev
# → http://localhost:3000

# Type-check only
npx tsc --noEmit

# Production build
npm run build
npm start
```

---

## AI Difficulty

| Level | Strategy |
|---|---|
| **Easy** | Picks a random empty cell |
| **Medium** | Wins if possible → blocks opponent → takes center → random corner |
| **Hard** | Full [Minimax](https://en.wikipedia.org/wiki/Minimax) with α-β pruning — unbeatable |

---

## Deployment

Push to GitHub and import the repo in [Vercel](https://vercel.com/). No environment variables or special build configuration required — it deploys out of the box.

---

## License

MIT
