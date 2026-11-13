# 🎬 Antigravity Unlimited Video Engine ($0 Local Reel Automation)

> **Autonomous 100% Free, Local 9:16 Video Engineering Pipeline** for Instagram Reels, YouTube Shorts, and TikTok. Powered by **Python (Edge-TTS)** and **Remotion (React + TypeScript)**.

---

## ⚡ Key Highlights & Architecture

- **$0 Total Cost**: No paid APIs, no OpenAI subscriptions, no ElevenLabs bills.
- **Neural Voice Synthesis**: Powered by Microsoft Edge Neural TTS (`edge-tts`) with 100+ natural voices (Christopher, Jenny, Andrew, Ryan, Guy, Ava).
- **Karaoke Bouncing Captions**: Word-level boundary synchronization with active bouncing word highlight (`#FFE600` neon yellow) and glassmorphic pill background.
- **Instagram Reels Safe Zone**: Engineered for vertical 9:16 (`1080x1920`), strictly observing a `1080x1420` safe container (`paddingTop: 220`, `paddingBottom: 280`, `paddingLeft: 64`, `paddingRight: 64`) so titles and captions are never obscured by platform buttons or audio tags.
- **Multi-Genre Compositions**:
  1. `EduReel` - Sleek dark space theme (`#0B0F19`), glowing black hole accretion disk SVG, dual clock time dilation comparison, Einstein field equations.
  2. `FunnyReel` - High-energy meme theme, spring physics emoji pops, relatable daily humor, default mode network science punchline.
  3. `UniversalReel` - Dynamic multi-phase scene engine that automatically adapts to any custom topic or script.
- **Retention Retention Mechanics**: Top glowing progress bar (`ProgressBar`) and dynamic scene transitions keep watch-time high.

---

## 🚀 Quick Start (Single Command)

### 1. Generate & Render a Video with One Command
From either `unlimited-reels-engine/` or `my-edu-reels/`:

```bash
# Render default Educational Reel (Black Hole Time Dilation)
python3 automate_reel.py

# Render custom Educational Reel with automatic script synthesis
python3 automate_reel.py --topic "Quantum Tunneling" --style educational

# Render a Funny / Meme Reel
python3 automate_reel.py --topic "Why your brain remembers cringe at 3 AM" --style funny

# Render a custom raw script
python3 automate_reel.py --script "Here is why your GPS requires Einstein's relativity..." --style educational
```

### 2. Launch Interactive Live Studio Preview
```bash
cd my-edu-reels
npm run dev
```
Open [http://localhost:3000](http://localhost:3000) to preview animations, scrub frames, and test different compositions interactively!

---

## 📁 Project Structure

```
unlimited-reels-engine/
├── .venv/                         # Isolated Python virtual environment
├── automate_reel.py               # Root CLI launcher
├── engine/                        # Python Core Engine
│   ├── tts_engine.py              # Edge-TTS synthesizer + word timing parser
│   └── content_generator.py       # Algorithmic viral script generator & presets
└── my-edu-reels/                  # Remotion Project Workspace
    ├── automate_reel.py           # In-project automation CLI
    ├── package.json
    ├── remotion.config.ts
    ├── public/                    # Render assets
    │   ├── voice.mp3              # Generated neural voiceover
    │   ├── subs.vtt               # WebVTT subtitle cues
    │   ├── subs.json              # Karaoke word-level timestamps
    │   └── video-meta.json        # Audio length & frame calculation
    └── src/
        ├── Root.tsx               # Remotion root with composition registry
        ├── EduReel.tsx            # 9:16 Educational Master Composition
        ├── FunnyReel.tsx          # 9:16 Funny / Meme Master Composition
        ├── UniversalReel.tsx      # Dynamic multi-scene script explainer
        ├── components/
        │   ├── BackgroundGrid.tsx # Pulsing spacetime grid & particles
        │   ├── BlackHoleVisual.tsx# Scene 1: Accretion disk & photon sphere
        │   ├── ClockComparison.tsx# Scene 2: 1.0x vs 0.3x twin clock paradox
        │   ├── RelativityCard.tsx # Scene 3: Einstein field equations
        │   ├── KaraokeCaptions.tsx# Hormozi/MrBeast style bouncing captions
        │   └── ProgressBar.tsx    # Retention progress bar
        └── data/
            └── defaultSubs.ts     # Pre-compiled fallback timing data
```

---

## 🎙️ Curated Voice Library

| Preset ID | Voice Identifier | Style / Tone |
| :--- | :--- | :--- |
| `educational_male` | `en-US-ChristopherNeural` | Deep, authoritative, documentary (Default) |
| `educational_female` | `en-US-JennyNeural` | Crisp, engaging, informative |
| `british_documentary`| `en-GB-RyanNeural` | BBC nature / cosmos narration |
| `energetic_male` | `en-US-AndrewMultilingualNeural` | Upbeat YouTube creator / meme tone |
| `punchy_female` | `en-US-AvaNeural` | Energetic, punchy, modern |
| `quirky_expressive` | `en-US-GuyNeural` | Relatable humor & conversation |

Specify any voice using `--voice`:
```bash
python3 automate_reel.py --topic "Gravitational Waves" --voice en-GB-RyanNeural
```

---

## 🛠️ CLI Options Reference

```
usage: automate_reel.py [-h] [--topic TOPIC] [--script SCRIPT]
                        [--style {educational,funny,universal}]
                        [--comp COMP] [--preset PRESET]
                        [--voice VOICE] [--rate RATE]
                        [--output OUTPUT] [--list-presets]
                        [--preview] [--interactive]

Options:
  --topic TOPIC         Topic for automatic viral script generation
  --script SCRIPT       Custom speech script text
  --style STYLE         Video style: educational (default), funny, universal
  --comp COMP           Remotion composition ID (EduReel, FunnyReel, UniversalReel)
  --preset PRESET       Use a built-in viral preset (e.g. black_hole_time, quantum_tunneling, brain_at_3am)
  --voice VOICE         Neural voice name
  --rate RATE           TTS speech rate (e.g., '+5%', '+10%')
  --output, -o OUTPUT   Output MP4 destination (default: out/educational-reel.mp4)
  --preview             Launch interactive Remotion Studio in browser
  --list-presets        List all available built-in viral presets
  --interactive, -i     Interactive terminal wizard
```
