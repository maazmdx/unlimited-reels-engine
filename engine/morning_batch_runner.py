"""
Antigravity Morning Video Batch Engine
Generates 2 to 3 recreated AI reels every morning:
1. Picks queued Instagram / social URLs from inbox/insta_queue.txt
2. If queue has < 3 links, automatically supplements with top-tier viral categories:
   - Reel 1: 3D Diner AI Career / Developer Satire
   - Reel 2: AI vs Dad Comedic Tech Clash (WiFi / GPU Bill / Bargaining)
   - Reel 3: Anime Science Explainer or 3-Way AI Benchmark Arena
3. Recreates each reel with slightly changed narrative twists, custom animations, and neural voices
4. Executes 5-stage Multi-Check Quality Audit on all renders
5. Packages outputs into out/morning_YYYY_MM_DD/ with ready-to-post captions, hashtags, and audit frames
"""

import os
import sys
import os
import subprocess
import json
import time
import shutil
import argparse
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Any, Optional

PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from engine.agents.insta_analyzer import InstaAnalyzerAgent
from engine.agents.recreation_director import RecreationDirectorAgent
from engine.agents.audio_director import AudioDirectorAgent
from engine.agents.scene_director import SceneDirectorAgent
from engine.agents.quality_auditor import QualityAuditorAgent
from engine.agents.drive_dispatcher import DriveDispatcherAgent

BANNER = r"""
======================================================================
  🌅 ANTIGRAVITY MORNING BATCH VIDEO ENGINE (2-3 DAILY REELS)
  Pipeline  : Instagram Ingestion -> AI Viral Remix -> 3D Remotion -> Multi-Check
  Auditor   : 5-Stage Autonomous Broadcast Quality Watchdog
  Delivery  : out/morning_YYYY_MM_DD/ + Captions + Drive Sync
======================================================================
"""

CURATED_MORNING_POOL = [
    {
        "style": "diner_ai",
        "topic": "Anthropic Fellow $3,850/Week (No Experience Required)",
        "hook": "When a $3,850/week AI job says 'no experience required' but you only know Python.",
        "core_topic": "Absurd AI Job Salaries & Credentials",
        "format_type": "ai_vs_dev",
        "core_conflict": "Human CV submission vs AI proof of automated experiments",
        "punchline": "One fellow taught an AI to love owls with numbers. Now he works there."
    },
    {
        "style": "ai_vs_dad",
        "topic": "Dad vs The 5G Wi-Fi Router",
        "hook": "Why does every Dad believe slapping the router fixes the internet?",
        "core_topic": "Generational Tech Clash",
        "format_type": "ai_vs_dad",
        "core_conflict": "Fiber optic TCP/IP packet routing vs Dad's right hand slap",
        "punchline": "Thirty years of Indian engineering beats artificial intelligence every day of the week."
    },
    {
        "style": "diner_ai",
        "topic": "The 101st Rejection: Bypassing HR at 2 AM",
        "hook": "Rejected after 4 rounds while the guy hired never even applied.",
        "core_topic": "Broken HR Automation",
        "format_type": "ai_vs_dev",
        "core_conflict": "Traditional ATS black hole vs DMing founders before job posts",
        "punchline": "Founders post 'we are hiring' on X at 2 AM. The job board comes with 100 people days later."
    },
    {
        "style": "ai_vs_dad",
        "topic": "Dad Catches Son Running 4 GPUs Overnight",
        "hook": "Are you running a steel factory in your bedroom?!",
        "core_topic": "AI Hardware Electricity Trauma",
        "format_type": "ai_vs_dad",
        "core_conflict": "Local LLM training watts vs Dad's electric meter trauma",
        "punchline": "Back in my day we calculated square roots with pencil and shut off the fan to save power."
    },
    {
        "style": "ai_arena",
        "topic": "Claude vs Gemini vs Grok: The Benchmark Smackdown",
        "hook": "Which AI actually writes production code without hallucinating?",
        "core_topic": "AI Model Wars",
        "format_type": "ai_arena",
        "core_conflict": "Academic philosophy vs unhinged roasts vs practical terminal agents",
        "punchline": "Antigravity ran the entire unit test suite while Claude and Grok were arguing."
    }
]


def load_inbox_queue(queue_file: Path) -> List[str]:
    """Reads URLs from inbox queue file."""
    if not queue_file.exists():
        return []
    urls = []
    with open(queue_file, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith("#"):
                urls.append(line)
    return urls


def archive_processed_urls(queue_file: Path, processed: List[str]):
    """Removes processed URLs from queue and logs to processed archive."""
    if not processed or not queue_file.exists():
        return
    remaining = []
    with open(queue_file, "r", encoding="utf-8") as f:
        for line in f:
            stripped = line.strip()
            if stripped not in processed:
                remaining.append(line)

    with open(queue_file, "w", encoding="utf-8") as f:
        f.writelines(remaining)

    archive_file = queue_file.parent / "processed_urls.txt"
    with open(archive_file, "a", encoding="utf-8") as f:
        for u in processed:
            f.write(f"{datetime.now().isoformat()} - {u}\n")


def generate_social_caption(script_data: Dict[str, Any]) -> str:
    """Generates an engaging, algorithm-optimized Instagram Reel caption."""
    title = script_data.get("title", "AI vs Humans")
    hook_tag = script_data.get("hook", {}).get("tag", "⚠️ REAL TALK")
    hook_headline = script_data.get("hook", {}).get("headline", title)

    caption = (
        f"{hook_tag} {hook_headline}\n\n"
        f"{script_data.get('hook', {}).get('subheadline', '')}\n\n"
        f"Drop your thoughts below 👇 Is AI taking over or are humans still winning the argument?\n\n"
        f"Follow for daily AI breakdowns, developer humor & zero-dollar tools!\n\n"
        f"#AI #TechHumor #Developer #Coding #SoftwareEngineering #ProgrammerLife #Claude #Gemini #TechReels #AITools"
    )
    return caption


def run_morning_batch(
    count: int = 2,
    drive_sync: bool = False,
    drive_folder_id: Optional[str] = None,
    insta_url: Optional[str] = None,
    scene_preset: str = "diner"
) -> Dict[str, Any]:
    """Executes the complete morning batch generation."""
    print(BANNER)
    start_time = time.time()
    today_str = datetime.now().strftime("%Y_%m_%d")
    batch_dir = PROJECT_ROOT / "out" / f"morning_{today_str}"
    batch_dir.mkdir(parents=True, exist_ok=True)
    thumbs_dir = batch_dir / "audit_thumbnails"
    thumbs_dir.mkdir(parents=True, exist_ok=True)

    inbox_file = PROJECT_ROOT / "inbox" / "insta_queue.txt"
    queued_urls = load_inbox_queue(inbox_file)

    print(f"🌅 Starting Morning Batch: Target {count} Recreated Videos")
    if queued_urls:
        print(f"📥 Found {len(queued_urls)} URLs queued in inbox/insta_queue.txt")
    else:
        print("ℹ️ Inbox queue empty. Drawing from curated high-retention viral daily pool.")

    # Initialize subagents
    insta_analyzer = InstaAnalyzerAgent(project_root=PROJECT_ROOT)
    recreation_director = RecreationDirectorAgent(project_root=PROJECT_ROOT)
    audio_director = AudioDirectorAgent(project_root=PROJECT_ROOT)
    scene_director = SceneDirectorAgent(project_root=PROJECT_ROOT)
    quality_auditor = QualityAuditorAgent(project_root=PROJECT_ROOT)
    drive_dispatcher = DriveDispatcherAgent() if drive_sync else None

    processed_urls = []
    generated_reels = []

    # Select candidate items
    items_to_process = []
    if insta_url and insta_url.strip():
        print(f"🎯 Target URL Override: {insta_url.strip()}")
        items_to_process.append({"type": "url", "data": insta_url.strip()})
    else:
        for u in queued_urls[:count]:
            items_to_process.append({"type": "url", "data": u})
            processed_urls.append(u)

    # Supplement from curated pool if less than count
    pool_index = datetime.now().timetuple().tm_yday
    while len(items_to_process) < count:
        candidate = CURATED_MORNING_POOL[pool_index % len(CURATED_MORNING_POOL)]
        if candidate not in [it["data"] for it in items_to_process if it["type"] == "pool"]:
            items_to_process.append({"type": "pool", "data": candidate})
        pool_index += 1

    # Execute generation for each item
    for idx, item in enumerate(items_to_process, 1):
        print(f"\n" + "=" * 70)
        print(f"  🎬 PRODUCING MORNING REEL #{idx} OF {len(items_to_process)}")
        print("=" * 70)

        # Step 1: Ingestion / Topic Analysis
        if item["type"] == "url":
            print(f"🔗 Source: Queued URL -> {item['data']}")
            analysis = insta_analyzer.analyze_from_url_or_query(item["data"])
            target_style = None
        else:
            pool_data = item["data"]
            print(f"🎯 Source: Curated Viral Matrix -> {pool_data['topic']}")
            analysis = pool_data
            target_style = pool_data.get("style")

        # Step 2: Viral AI Recreation & Remix Screenplay
        script_data = recreation_director.recreate_reel(analysis, target_style=target_style)
        if scene_preset and scene_preset != "auto":
            script_data["scenePreset"] = scene_preset

        # Step 3: Neural Character Voices & DSP Mastering
        audio_res = audio_director.synthesize_soundtrack(script_data)

        # Step 4 & 5: Remotion Render & Multi-Check Quality Loop
        safe_title = "".join(c if c.isalnum() else "_" for c in script_data["title"].lower()).strip("_")[:30]
        output_filename = f"reel_{idx:02d}_{safe_title}.mp4"

        max_attempts = 2
        rendered_mp4 = None
        audit_res = None

        for attempt in range(1, max_attempts + 1):
            print(f"\n🔄 Render & Quality Check Attempt {attempt}/{max_attempts}...")
            rendered_mp4 = scene_director.compile_and_render(
                script_data=script_data,
                audio_result=audio_res,
                output_name=output_filename
            )

            audit_res = quality_auditor.audit_video(rendered_mp4, auto_heal=True)
            if audit_res["status"] == "PASS":
                print("🏆 Quality Watchdog: Approved!")
                break
            else:
                print(f"⚠️ Quality check attempt {attempt} issues: {audit_res.get('reasons')}")

        # Copy finalized video & thumbnails into morning batch directory
        final_video_dest = batch_dir / output_filename
        if Path(rendered_mp4).exists():
            shutil.copy2(rendered_mp4, final_video_dest)

        # Copy audit keyframes to thumbs directory
        for kf in audit_res.get("keyframes", []):
            if kf.get("path") and Path(kf["path"]).exists():
                shutil.copy2(kf["path"], thumbs_dir / Path(kf["path"]).name)

        # Generate Caption & Posting metadata
        caption_text = generate_social_caption(script_data)
        caption_file = batch_dir / f"reel_{idx:02d}_{safe_title}_caption.txt"
        with open(caption_file, "w", encoding="utf-8") as f:
            f.write(caption_text)

        # Optional Cloud Drive Sync
        drive_status = "SKIPPED"
        if drive_dispatcher:
            try:
                has_creds = (
                    os.environ.get("GDRIVE_CREDENTIALS")
                    or os.environ.get("GOOGLE_DRIVE_TOKEN")
                    or os.environ.get("GDRIVE_ACCESS_TOKEN")
                )
                target_folder = drive_folder_id or os.environ.get("GDRIVE_FOLDER_ID")
                if not has_creds and not target_folder:
                    print("ℹ️ Google Drive credentials/folder not configured; skipping Drive sync cleanly.")
                    drive_status = "SKIPPED_NO_SECRETS"
                else:
                    vtt_file = str(PROJECT_ROOT / "public" / "subs.vtt")
                    d_res = drive_dispatcher.upload_reel(
                        video_path=str(final_video_dest),
                        vtt_path=vtt_file,
                        meta_data={
                            "title": script_data["title"],
                            "hook": script_data.get("hook", {}).get("headline"),
                            "batch": today_str,
                        },
                        drive_folder_id=target_folder,
                    )
                    drive_status = d_res.get("status", "SUCCESS")
            except Exception as e_drive:
                print(f"ℹ️ Google Drive sync notice (non-fatal): {e_drive}")
                drive_status = f"SKIPPED: {e_drive}"

        generated_reels.append({
            "index": idx,
            "title": script_data["title"],
            "video_path": str(final_video_dest),
            "caption_path": str(caption_file),
            "duration": audit_res.get("duration", 0),
            "quality_score": audit_res.get("score", 100),
            "status": audit_res.get("status", "PASS"),
            "drive_status": drive_status
        })

    # Archive processed URLs
    if processed_urls:
        archive_processed_urls(inbox_file, processed_urls)

    elapsed = time.time() - start_time

    # Save Batch Summary Report
    batch_report = {
        "date": today_str,
        "total_generated": len(generated_reels),
        "elapsed_seconds": round(elapsed, 1),
        "batch_directory": str(batch_dir),
        "reels": generated_reels
    }

    report_json_path = batch_dir / "batch_report.json"
    with open(report_json_path, "w", encoding="utf-8") as f:
        json.dump(batch_report, f, indent=2)

    print("\n" + "=" * 70)
    print("  🎉 MORNING BATCH COMPLETE! 2-3 REELS GENERATED & AUDITED")
    print(f"  📁 Output Directory : {batch_dir}")
    print(f"  ⏱️ Total Batch Time : {elapsed:.1f}s")
    for r in generated_reels:
        print(f"  🎬 Reel #{r['index']:02d}: {r['title']} [{r['duration']:.1f}s | Score: {r['quality_score']}/100]")
    print("=" * 70)

    return batch_report


def setup_cron_schedule(hour: int = 8, minute: int = 30):
    """Configures local Linux crontab to execute morning batch daily."""
    python_bin = PROJECT_ROOT / ".venv" / "bin" / "python3"
    runner_script = PROJECT_ROOT / "engine" / "morning_batch_runner.py"

    cron_cmd = f"{minute} {hour} * * * cd {PROJECT_ROOT} && {python_bin} {runner_script} >> {PROJECT_ROOT}/out/morning_cron.log 2>&1"

    try:
        current_crontab = subprocess.run(["crontab", "-l"], capture_output=True, text=True).stdout
        lines = [line for line in current_crontab.splitlines() if "morning_batch_runner.py" not in line]
        lines.append(cron_cmd)
        new_crontab = "\n".join(lines) + "\n"

        p = subprocess.run(["crontab", "-"], input=new_crontab, text=True, capture_output=True)
        if p.returncode == 0:
            print(f"✅ Morning Cron Scheduled! Runs daily at {hour:02d}:{minute:02d} AM.")
            print(f"   Command: {cron_cmd}")
            return True
        else:
            print(f"⚠️ Crontab update failed: {p.stderr}")
    except Exception as e:
        print(f"⚠️ Crontab scheduling error: {e}")
    return False


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Antigravity Morning Video Batch Engine")
    parser.add_argument("--count", type=int, default=2, help="Number of reels to generate (1, 2, or 3)")
    parser.add_argument("--schedule", action="store_true", help="Set up daily morning crontab schedule (08:30 AM)")
    parser.add_argument("--hour", type=int, default=8, help="Cron schedule hour (default: 8)")
    parser.add_argument("--minute", type=int, default=30, help="Cron schedule minute (default: 30)")
    parser.add_argument("--drive", action="store_true", help="Enable Google Drive cloud upload")
    parser.add_argument("--drive-folder", type=str, default=None, help="Google Drive folder ID")
    parser.add_argument("--insta-url", type=str, default=None, help="Specific Instagram/Shorts URL to recreate")
    parser.add_argument("--scene-preset", type=str, default="diner", choices=["diner", "desk", "auto"], help="3D Scene Preset")
    args = parser.parse_args()

    if args.schedule:
        setup_cron_schedule(hour=args.hour, minute=args.minute)
    else:
        run_morning_batch(
            count=args.count,
            drive_sync=args.drive,
            drive_folder_id=args.drive_folder,
            insta_url=args.insta_url,
            scene_preset=args.scene_preset,
        )
