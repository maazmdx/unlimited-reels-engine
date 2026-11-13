#!/usr/bin/env python3
"""
Antigravity Unlimited Video Engine - Master Automation CLI
100% Free, Local, $0 Video Pipeline for Instagram & YouTube Shorts.
Supports: English, Hindi (हिंदी), Kannada (ಕನ್ನಡ)
Themes: Anime, Educational, Funny / Meme, Universal Explainer
Autonomous Quality Auditor: Powered by Google Antigravity SDK & FFmpeg
"""

import os
import sys
import argparse
import subprocess
import json
import time
from pathlib import Path

# Auto-detect project paths
SCRIPT_DIR = Path(__file__).resolve().parent
if (SCRIPT_DIR / "my-edu-reels").exists():
    PROJECT_ROOT = SCRIPT_DIR
    REMOTION_DIR = SCRIPT_DIR / "my-edu-reels"
else:
    PROJECT_ROOT = SCRIPT_DIR.parent
    REMOTION_DIR = SCRIPT_DIR

if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from engine.tts_engine import generate_speech, PRESET_VOICES, detect_language
from engine.content_generator import generate_content, VIRAL_PRESETS
from engine.video_auditor import VideoAuditor

BANNER = r"""
======================================================================
  🎬 ANTIGRAVITY UNLIMITED VIDEO ENGINE ($0 Local Auto-Reel)
  Languages : English | Hindi (हिंदी) | Kannada (ಕನ್ನಡ)
  Genres    : Anime Science | Meme / Funny | Astrophysics | Deep Explainer
  Auditor   : Antigravity SDK Autonomous Quality Watchdog
======================================================================
"""


def parse_args():
    parser = argparse.ArgumentParser(
        description="Antigravity Unlimited Video Engine for Instagram & YouTube Shorts",
        formatter_class=argparse.RawTextHelpFormatter,
    )
    parser.add_argument(
        "--topic",
        type=str,
        help="Topic for automatic viral script generation (e.g. 'Gojo Infinity', 'Quantum Tunneling')",
    )
    parser.add_argument(
        "--script",
        type=str,
        help="Custom speech script text in English, Hindi, or Kannada",
    )
    parser.add_argument(
        "--style",
        choices=["educational", "funny", "anime", "universal"],
        default="educational",
        help="Video visual and narrative style (default: educational)",
    )
    parser.add_argument(
        "--lang", "--language",
        choices=["en", "hi", "kn"],
        default=None,
        dest="language",
        help="Language: 'en' (English), 'hi' (Hindi), 'kn' (Kannada)",
    )
    parser.add_argument(
        "--comp",
        type=str,
        default=None,
        help="Remotion composition ID (EduReel, AnimeEduReel, FunnyReel, UniversalReel)",
    )
    parser.add_argument(
        "--preset",
        choices=list(VIRAL_PRESETS.keys()),
        default=None,
        help="Built-in viral script preset",
    )
    parser.add_argument(
        "--voice",
        type=str,
        default=None,
        help="Custom neural voice name (e.g., 'hi-IN-MadhurNeural', 'kn-IN-GaganNeural')",
    )
    parser.add_argument(
        "--rate",
        type=str,
        default="+0%",
        help="TTS speech rate (e.g. '+5%%', '+10%%')",
    )
    parser.add_argument(
        "--output", "-o",
        type=str,
        default="out/educational-reel.mp4",
        help="Output MP4 file path (default: out/educational-reel.mp4)",
    )
    parser.add_argument(
        "--no-audit",
        action="store_true",
        help="Skip autonomous video quality inspection",
    )
    parser.add_argument(
        "--list-presets",
        action="store_true",
        help="List all available built-in viral script presets",
    )
    parser.add_argument(
        "--preview",
        action="store_true",
        help="Launch Remotion interactive live studio preview instead of rendering MP4",
    )
    parser.add_argument(
        "--interactive", "-i",
        action="store_true",
        help="Prompt interactively for topic, language, and style selection",
    )
    return parser.parse_args()


def interactive_wizard():
    print("\n🔮 Interactive Video Generator Wizard:")
    print("1. Select a Viral Preset:")
    preset_keys = list(VIRAL_PRESETS.keys())
    for idx, key in enumerate(preset_keys, 1):
        p = VIRAL_PRESETS[key]
        print(f"   [{idx:02d}] {p['title']} [{p['style'].upper()} - {p['language'].upper()}]")
    print(f"   [{len(preset_keys) + 1:02d}] Enter Custom Topic (English, Hindi, or Kannada)")
    print(f"   [{len(preset_keys) + 2:02d}] Paste Custom Script Directly")

    choice = input("\nEnter choice (default: 1): ").strip() or "1"
    try:
        c_idx = int(choice)
        if 1 <= c_idx <= len(preset_keys):
            return {"preset": preset_keys[c_idx - 1]}
        elif c_idx == len(preset_keys) + 1:
            t = input("Enter Topic: ").strip()
            st = input("Choose Style [anime/educational/funny] (default: anime): ").strip() or "anime"
            ln = input("Language [en/hi/kn] (default: en): ").strip() or "en"
            return {"topic": t, "style": st, "language": ln}
        elif c_idx == len(preset_keys) + 2:
            sc = input("Paste your script: ").strip()
            return {"script": sc}
    except Exception:
        pass

    return {"preset": "anime_gojo_infinity_en"}


def main():
    print(BANNER)
    args = parse_args()

    if args.list_presets:
        print("Available Viral Script Presets:")
        for k, v in VIRAL_PRESETS.items():
            print(f"  • {k:<25} : {v['title']} [{v['style'].upper()} | {v['language'].upper()}]")
        sys.exit(0)

    # Interactive trigger if no args
    if args.interactive or (not args.topic and not args.script and not args.preset and len(sys.argv) == 1):
        wizard_data = interactive_wizard()
        for k, v in wizard_data.items():
            setattr(args, k, v)

    # 1. Resolve Content (Script, Scenes, Voice, Style, Language)
    content = generate_content(
        topic=args.topic,
        script=args.script,
        style=args.style,
        preset=args.preset,
        language=args.language,
    )

    lang = content.get("language") or detect_language(content["script"])
    print(f"📖 Reel Title : {content['title']}")
    print(f"🌐 Language   : {lang.upper()} ({'Kannada' if lang=='kn' else 'Hindi' if lang=='hi' else 'English'})")
    print(f"🎨 Visual Style: {content['style'].upper()}")
    print(f"📝 Script Preview: {content['script'][:120]}...\n")

    # Select composition
    composition_id = args.comp
    if not composition_id:
        if content["style"] == "anime":
            composition_id = "AnimeEduReel"
        elif content["style"] == "funny":
            composition_id = "FunnyReel"
        elif args.topic or args.script:
            composition_id = "AnimeEduReel" if "anime" in content["style"] else "EduReel"
        else:
            composition_id = "EduReel"

    voice = args.voice or content.get("voice")

    # 2. Synthesize Audio and Subtitles in public/
    public_dir = REMOTION_DIR / "public"
    public_dir.mkdir(parents=True, exist_ok=True)

    voice_path = public_dir / "voice.mp3"
    subs_vtt_path = public_dir / "subs.vtt"
    subs_json_path = public_dir / "subs.json"
    meta_json_path = public_dir / "video-meta.json"

    print("--- STEP 1: Multilingual Neural Voiceover & Subtitles ---")
    tts_result = generate_speech(
        text=content["script"],
        voice=voice,
        rate=args.rate,
        style=content["style"],
        out_audio=str(voice_path),
        out_vtt=str(subs_vtt_path),
        out_json=str(subs_json_path),
        meta_json=str(meta_json_path),
        title=content["title"],
    )

    duration_sec = tts_result["duration"]
    duration_frames = tts_result["frames"]

    # Copy fresh subs into src/data/defaultSubs.ts for 100% build resilience
    try:
        with open(subs_json_path, "r", encoding="utf-8") as f:
            subs_data = json.load(f)
        src_data_file = REMOTION_DIR / "src" / "data" / "defaultSubs.ts"
        src_data_file.parent.mkdir(parents=True, exist_ok=True)
        with open(src_data_file, "w", encoding="utf-8") as f:
            f.write("import { SubtitleData } from '../components/KaraokeCaptions';\n\n")
            f.write("export const DEFAULT_SUBTITLES: SubtitleData = ")
            json.dump(subs_data, f, indent=2, ensure_ascii=False)
            f.write(";\n")
    except Exception as e:
        print(f"Notice: defaultSubs update skipped: {e}")

    # 3. Handle Live Studio Preview
    if args.preview:
        print("\n🚀 Launching Remotion Studio Live Preview...")
        print(f"👉 Opening: npx remotion studio (Press Ctrl+C to stop)\n")
        subprocess.run(["npx", "remotion", "studio"], cwd=str(REMOTION_DIR))
        return

    # 4. Render Final Video
    out_file = Path(args.output)
    if not out_file.is_absolute():
        out_file = REMOTION_DIR / out_file
    out_file.parent.mkdir(parents=True, exist_ok=True)

    print(f"\n--- STEP 2: Rendering MP4 Locally ($0 Remotion Free License) ---")
    print(f"🎯 Composition : {composition_id}")
    print(f"⏱️ Duration    : {duration_sec:.2f}s ({duration_frames} frames @ 30fps)")
    print(f"💾 Output File : {out_file}")

    start_time = time.time()
    cmd = [
        "npx",
        "remotion",
        "render",
        composition_id,
        str(out_file),
    ]

    print(f"⚡ Running: {' '.join(cmd)}\n")
    render_process = subprocess.run(cmd, cwd=str(REMOTION_DIR))

    if render_process.returncode != 0:
        print(f"\n❌ Render failed with exit code {render_process.returncode}")
        sys.exit(render_process.returncode)

    elapsed = time.time() - start_time
    file_size_mb = out_file.stat().st_size / (1024 * 1024)

    # Copy output to root out/ as well
    root_out = PROJECT_ROOT / "out" / out_file.name
    root_out.parent.mkdir(parents=True, exist_ok=True)
    try:
        import shutil
        shutil.copy2(out_file, root_out)
    except Exception:
        pass

    print("\n" + "=" * 70)
    print("  🎉 VIDEO RENDER COMPLETE - 100% SUCCESS")
    print("=" * 70)
    print(f"📁 Video Path : {out_file.resolve()}")
    print(f"📊 File Size  : {file_size_mb:.2f} MB")
    print(f"⏱️ Render Time: {elapsed:.1f}s")
    print(f"📐 Resolution : 1080x1920 (9:16 Vertical Instagram Reel / YouTube Shorts)")
    print(f"🎙️ Audio Track: Neural Voiceover ({tts_result.get('voice', voice)})")

    # 5. Autonomous Video Quality Auditor
    if not args.no_audit:
        print("\n--- STEP 3: Antigravity Autonomous Video Quality Audit ---")
        auditor = VideoAuditor(PROJECT_ROOT)
        audit_res = auditor.audit_video(str(out_file))

        status_emoji = "✅ PASS" if audit_res["status"] == "PASS" else "⚠️ ISSUES FLAGGED"
        print(f"Audit Status  : {status_emoji}")
        print(f"Frames Checked: {len(audit_res['extracted_keyframes'])} keyframes")
        if audit_res["flags"]:
            for fl in audit_res["flags"]:
                print(f"  • [{fl['severity']}] {fl['category']}: {fl['issue']}")
        else:
            print("  • 100% Safe Zone, Audio Sync, and Subtitle compliance verified!")

        if audit_res.get("fixes_applied"):
            print("  • Auto-fixes applied:")
            for fix in audit_res["fixes_applied"]:
                print(f"    ✔ {fix}")

    print("\nNext Action Shortcuts:")
    print("  • Watch in browser : npm run dev (inside my-edu-reels)")
    print("  • Hindi Anime Reel : python automate_reel.py --preset anime_gojo_infinity_hi")
    print("  • Kannada Anime    : python automate_reel.py --preset anime_gojo_infinity_kn")
    print("  • Funny Reel       : python automate_reel.py --preset anime_time_stop_hi")
    print("=" * 70)


if __name__ == "__main__":
    main()
