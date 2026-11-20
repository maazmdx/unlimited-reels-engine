# 🎬 Antigravity Unlimited Video Engine ($0 AI Reels Engine)

> **Autonomous 100% Free, Local 9:16 Video Generation & Recreation Engine** for Instagram Reels, YouTube Shorts, and TikTok. Powered by **Gemini Multimodal AI**, **Edge-TTS Neural Acoustics**, and **Remotion (React + TypeScript)**.

---

## 🌟 The Core Capabilities

### 1. 📥 Instagram & Social Video Recreation
Picks any AI video from Instagram (via URL, local file, or inbox queue), deconstructs its viral anatomy with Gemini Multimodal AI, and recreates it in a fresh manner with slightly remixed narrative twists, our animated character rosters, and our neural voices!

### 2. 🌅 Morning Batch Mode (2–3 Videos Every Morning)
Runs autonomously every morning via local system cron (`08:30 AM`). Automatically ingests queued Instagram links from `inbox/insta_queue.txt` or draws from our high-retention viral daily matrix, producing 2–3 distinct reels in dated folders (`out/morning_YYYY_MM_DD/`) with algorithm-optimized Instagram captions and hashtags.

### 3. 🔍 5-Stage Multi-Check Quality Watchdog
Autonomous quality auditor (`QualityAuditorAgent`) rigorously inspects every rendered video:
1. **Dimensions & Codec**: 1080x1920 (9:16 vertical), 30 FPS, H.264/AAC.
2. **Audio Levels & Loudness**: Broadcast target (-14dB LUFS), zero digital clipping, no silence.
3. **Voice/Visual Sync**: Safe-tail padding (+0.5s) to guarantee zero speech cutoff.
4. **Keyframe Animation Integrity**: Audits 4 critical keyframes (Hook, Card Reveal, Climax, Punchline) to guarantee non-blank, rich-contrast visual rendering.
5. **Safe Zone Conformance**: Strictly enforces `1080x1420` safe area so UI overlays on Instagram never block text.
*Includes automatic remediation and auto-healing!*

---

## 🚀 Quick Commands

### 1. Recreate an Instagram Reel or Topic
```bash
# Recreate from an Instagram URL
python3 engine/master_orchestrator.py --insta "https://www.instagram.com/reel/C7XYZ123/"

# Or recreate from a topic/debate
python3 engine/master_orchestrator.py --insta "Why you should never pay $200 for Claude when Google Antigravity is free"
```

### 2. Run Daily Morning Batch (2–3 Reels)
```bash
# Execute morning batch right now (produces 2-3 reels into out/morning_YYYY_MM_DD/)
python3 engine/morning_batch_runner.py --count 3

# Schedule morning batch to run every day at 08:30 AM via system cron
python3 engine/morning_batch_runner.py --schedule --hour 8 --minute 30
```

### 3. Interactive Automation Wizard
```bash
./setup_automation.sh
```

---

## 📁 Project Architecture

```
unlimited-reels-engine/
├── automate_reel.py                 # Master CLI entrypoint
├── setup_automation.sh              # One-click interactive setup & scheduler
├── inbox/
│   └── insta_queue.txt              # Drop Instagram / social URLs here to auto-process
├── engine/
│   ├── morning_batch_runner.py      # Daily batch orchestrator (2-3 reels every morning)
│   ├── master_orchestrator.py       # Multi-agent feedback loop orchestrator
│   ├── tts_engine.py                # Edge-TTS neural multi-voice + studio DSP mastering
│   ├── video_auditor.py             # Video inspection & frame analysis
│   └── agents/
│       ├── insta_analyzer.py        # Social reel download & Gemini multimodal deconstruction
│       ├── recreation_director.py   # AI viral remixer (adapts into our animated styles)
│       ├── script_director.py       # Multi-character screenwriter
│       ├── audio_director.py        # Neural acoustics, Hz pitch tuning & subtitle alignment
│       ├── scene_director.py        # Remotion visual compiler & headless MP4 renderer
│       ├── quality_auditor.py       # 5-stage broadcast quality watchdog
│       └── drive_dispatcher.py      # Google Drive cloud sync & local exporter
├── my-edu-reels/                    # Remotion React 19 + TypeScript Video Engine
│   ├── src/
│   │   ├── MasterAutonomousReel.tsx # 2.5D Animated character stage & dynamic cards
│   │   ├── ThreeWayComparisonReel.tsx # 3D Diner with Three.js camera & floating browser
│   │   ├── AnimeEduReel.tsx         # Shonen manga speedlines, glowing aura & formulas
│   │   ├── EduReel.tsx              # Astrophysics & science explainer
│   │   └── FunnyReel.tsx            # Relatable developer comedy & memes
│   └── public/                      # Render assets, voices & subtitles
└── out/
    └── morning_YYYY_MM_DD/          # Daily morning batch outputs, captions & audit frames
```
