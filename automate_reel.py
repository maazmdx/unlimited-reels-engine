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

# Self-bootstrap virtualenv if running outside it
venv_python = PROJECT_ROOT / ".venv" / "bin" / "python3"
if venv_python.exists() and sys.prefix == getattr(sys, "base_prefix", sys.prefix):
    res = subprocess.call([str(venv_python)] + sys.argv)
    sys.exit(res)

if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from engine.tts_engine import generate_speech, generate_dialogue_speech, PRESET_VOICES, detect_language
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
        choices=["educational", "funny", "anime", "universal", "diner", "threeway"],
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
        "--no-sfx",
        action="store_false",
        dest="sfx",
        default=True,
        help="Skip automatic Real SFX sound design and audio mastering",
    )
    parser.add_argument(
        "--insta", "--recreate",
        type=str,
        default=None,
        help="Instagram Reel URL, video file, or topic to recreate and remix",
    )
    parser.add_argument(
        "--morning-batch",
        action="store_true",
        help="Run autonomous daily morning batch (generates 2-3 reels)",
    )
    parser.add_argument(
        "--count",
        type=int,
        default=3,
        help="Number of reels in morning batch (2 or 3)",
    )
    parser.add_argument(
        "--schedule-morning",
        action="store_true",
        help="Set up daily morning crontab schedule (08:30 AM)",
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

    # Route: Daily Morning Cron Scheduler
    if args.schedule_morning:
        from engine.morning_batch_runner import setup_cron_schedule
        setup_cron_schedule(hour=8, minute=30)
        sys.exit(0)

    # Route: Autonomous Morning Batch Generation (2-3 reels)
    if args.morning_batch:
        from engine.morning_batch_runner import run_morning_batch
        run_morning_batch(count=args.count)
        sys.exit(0)

    # Route: Instagram / Social Reel Ingestion & AI Recreation
    if args.insta:
        from engine.master_orchestrator import run_pipeline
        run_pipeline(insta_url=args.insta, output_filename=args.output if args.output != "out/educational-reel.mp4" else None)
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

    script_text = content.get("script") or " ".join([d["text"] for d in content.get("dialogue", [])])
    lang = content.get("language") or detect_language(script_text)
    print(f"📖 Reel Title : {content['title']}")
    print(f"🌐 Language   : {lang.upper()} ({'Kannada' if lang=='kn' else 'Hindi' if lang=='hi' else 'English'})")
    print(f"🎨 Visual Style: {content['style'].upper()}")
    print(f"📝 Script Preview: {script_text[:120]}...\n")

    # Select composition
    composition_id = args.comp
    if not composition_id:
        if content.get("comp"):
            composition_id = content["comp"]
        elif content["style"] == "diner":
            composition_id = "DinerAgentReel"
        elif content["style"] == "anime":
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
    if content.get("dialogue"):
        tts_result = generate_dialogue_speech(
            dialogue=content["dialogue"],
            human_voice=content.get("human_voice"),
            bot_voice=content.get("bot_voice"),
            rival_voice=content.get("rival_voice"),
            rate=args.rate,
            out_audio=str(voice_path),
            out_vtt=str(subs_vtt_path),
            out_json=str(subs_json_path),
            meta_json=str(meta_json_path),
            title=content["title"],
        )
    else:
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

    # 2b. Extract frame-accurate audio envelope for smooth lip-syncing
    envelope = []
    try:
        from engine.audio_analyzer import extract_frame_audio_envelope
        envelope = extract_frame_audio_envelope(
            str(voice_path),
            fps=30,
            out_json=str(public_dir / "audio_envelope.json")
        )
        print(f"📊 Extracted {len(envelope)} frame audio envelopes for organic lip-syncing.")
    except Exception as e:
        print(f"⚠️ Audio envelope extraction notice: {e}")

    # Copy fresh subs into src/data/defaultSubs.ts for 100% build resilience
    try:
        with open(subs_json_path, "r", encoding="utf-8") as f:
            subs_data = json.load(f)
        src_data_file = REMOTION_DIR / "src" / "data" / "defaultSubs.ts"
        src_data_file.parent.mkdir(parents=True, exist_ok=True)
        with open(src_data_file, "w", encoding="utf-8") as f:
            f.write("// Auto-generated by Antigravity Reel Engine\n")
            f.write("export const DEFAULT_SUBTITLES: any = ")
            json.dump(subs_data, f, indent=2, ensure_ascii=False)
            f.write(";\n")
    except Exception as e:
        print(f"Notice: defaultSubs update skipped: {e}")

    # Write dedicated reel_props.json for Remotion CLI
    props_file = public_dir / "reel_props.json"
    props_payload = {
        "subtitles": subs_data,
        "audioSrc": "voice.mp3",
        "title": content["title"],
        "audioEnvelope": envelope,
        "hookHeadline": content.get("hookHeadline", content.get("title", "")),
        "hookSubheadline": content.get("hookSubheadline", ""),
        "hookTag": content.get("hookTag", "⚠️ RELATABLE DEV MOMENT"),
        "cardType": content.get("cardType", "job_posting"),
        "cardUrl": content.get("cardUrl", "job-boards.greenhouse.io/anthropic/fellowship"),
        "cardData": content.get("cardData", {}),
        "badge": content.get("badge", "EVIDENCE"),
        "explainerTitle": content.get("explainerTitle", content["title"]),
        "bgImage": content.get("bgImage", "backgrounds/bg_cyber_diner.jpg"),
    }
    with open(props_file, "w", encoding="utf-8") as f:
        json.dump(props_payload, f, indent=2, ensure_ascii=False)

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
        f"--props=public/reel_props.json",
        "--gl=angle",
        "--angle=swiftshader",
        "--concurrency=2",
        "--codec=h264",
        "--pixel-format=yuv420p",
        "--jpeg-quality=90",
        "--timeout=120000",
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

    # 4b. Frame-Accurate Real SFX Mastering
    if args.sfx:
        print("\n--- STEP 2b: Real SFX Frame-Accurate Sound Design (Openverse + Earshot) ---")
        try:
            from engine.sfx_manager import SFXManager
            sfx_mgr = SFXManager(PROJECT_ROOT)
            cue_list = sfx_mgr.generate_cue_list(total_frames=duration_frames, fps=30.0)
            sfx_out = out_file.parent / f"{out_file.stem}_mastered.mp4"
            sfx_success = sfx_mgr.apply_sfx_to_video(
                video_path=str(out_file),
                cues=cue_list,
                output_path=str(sfx_out),
                voiceover_path=str(voice_path),
                target_lufs=-14.0
            )
            if sfx_success and sfx_out.exists():
                import shutil
                shutil.move(str(sfx_out), str(out_file))
                if root_out.exists():
                    shutil.copy2(out_file, root_out)
                print(f"✅ Real SFX mastered directly onto {out_file.name} (-14.0 LUFS)")
                sfx_mgr.audit_master(str(out_file), target_lufs=-14.0)
        except Exception as e:
            print(f"⚠️ Real SFX step notice: {e}")

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
