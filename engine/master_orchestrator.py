#!/usr/bin/env python3
"""
Antigravity Master Multi-Agent Orchestrator
Coordinates the autonomous subagents in an end-to-end quality feedback loop:
Agent 1: Trend & Social Video Ingestion (Instagram / Reels / HN Trends)
Agent 2: Viral Recreation Director & Screenwriter (Slightly remixes with our animations)
Agent 3: Neural Voice & Broadcast SFX Sound Designer
Agent 4: Remotion 3D / 2.5D Scene & Render Compiler
Agent 5: Autonomous Multi-Check Quality Watchdog (Loops if quality < 85%)
Agent 6: Google Drive Cloud Dispatcher & Local Daily Exporter
"""

import sys
import os
import subprocess
from pathlib import Path

# Self-bootstrap virtualenv if available
PROJECT_ROOT = Path(__file__).resolve().parent.parent
venv_python = PROJECT_ROOT / ".venv" / "bin" / "python3"
if venv_python.exists() and sys.prefix == getattr(sys, "base_prefix", sys.prefix):
    res = subprocess.call([str(venv_python)] + sys.argv)
    sys.exit(res)

import time
import json
import argparse

if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from engine.agents.trend_researcher import TrendResearcherAgent
from engine.agents.insta_analyzer import InstaAnalyzerAgent
from engine.agents.recreation_director import RecreationDirectorAgent
from engine.agents.script_director import ScriptDirectorAgent
from engine.agents.audio_director import AudioDirectorAgent
from engine.agents.scene_director import SceneDirectorAgent
from engine.agents.quality_auditor import QualityAuditorAgent
from engine.agents.drive_dispatcher import DriveDispatcherAgent
from engine.morning_batch_runner import run_morning_batch, setup_cron_schedule

BANNER = r"""
======================================================================
  🤖 ANTIGRAVITY MULTI-AGENT AUTONOMOUS VIDEO ORCHESTRATOR
  Workflow          : Social Reel Ingestion -> Viral Remix -> 3D Remotion
  Quality Guarantee : 5-Stage Multi-Check Quality Watchdog (95%+ Target)
  Acoustics         : Multi-Voice Neural Edge-TTS + Proximity DSP
  Visual Scene      : 3D Diner / 2.5D Animated Engine (Weather, Props, Zooms)
  Cloud Delivery    : Automated Google Drive Sync with Subtitles & Captions
======================================================================
"""


def run_pipeline(
    topic_override: str = None,
    topic_id: str = None,
    category: str = None,
    insta_url: str = None,
    output_filename: str = None,
    drive_folder_id: str = None,
    max_audit_attempts: int = 2
) -> str:
    print(BANNER)
    start_time = time.time()

    # Step 1 & 2: Topic Ingestion & Screenplay Generation
    if insta_url:
        print(f"\n📥 [Agent 1: Social Ingestion] Ingesting Instagram / Video: {insta_url}")
        insta_agent = InstaAnalyzerAgent(project_root=PROJECT_ROOT)
        source_analysis = insta_agent.analyze_from_url_or_query(insta_url)

        print("\n🎨 [Agent 2: Viral Recreation] Remixing reel into our signature Remotion animations...")
        recreator = RecreationDirectorAgent(project_root=PROJECT_ROOT)
        script_data = recreator.recreate_reel(source_analysis)
        topic_title = script_data.get("title", "Remixed AI Reel")
        topic_cat = source_analysis.get("core_topic", "Social Remix")
    else:
        # Standard trend researcher & script director
        researcher = TrendResearcherAgent(
            topic_override=topic_override,
            topic_id=topic_id,
            category=category
        )
        topic_data = researcher.research_daily_topic()
        topic_title = topic_data["title"]
        topic_cat = topic_data.get("category", "Tech Trends")

        script_agent = ScriptDirectorAgent()
        script_data = script_agent.build_script(topic_data)

    # Step 3: Agent 3 (Audio Director)
    print("\n🎙️ [Agent 3: Audio Director] Synthesizing character voices with broadcast mastering...")
    audio_agent = AudioDirectorAgent(project_root=PROJECT_ROOT)
    audio_result = audio_agent.synthesize_soundtrack(script_data)

    # Multi-Agent Quality Loop (Agents 4 & 5)
    scene_agent = SceneDirectorAgent(project_root=PROJECT_ROOT)
    auditor = QualityAuditorAgent(project_root=PROJECT_ROOT, target_lufs=-14.0)

    if not output_filename:
        safe_title = "".join(c if c.isalnum() else "_" for c in topic_title.lower()).strip("_")[:32]
        output_filename = f"daily_{safe_title}.mp4"

    rendered_video_path = None
    passed_audit = False

    for attempt in range(1, max_audit_attempts + 1):
        print(f"\n🔄 [Multi-Agent Quality Loop - Attempt {attempt}/{max_audit_attempts}]")
        rendered_video_path = scene_agent.compile_and_render(
            script_data=script_data,
            audio_result=audio_result,
            output_name=output_filename
        )

        audit_res = auditor.audit_video(rendered_video_path, auto_heal=True)
        if audit_res["status"] == "PASS":
            passed_audit = True
            print("🏆 Quality Watchdog Approved: Video passed all safety and broadcast standards!")
            break
        else:
            print(f"⚠️ Quality check issue on attempt {attempt}: {audit_res.get('reasons')}")
            time.sleep(1.0)

    if not passed_audit:
        print("⚠️ Warning: Proceeding with best-effort render after audit inspection.")

    # Step 6: Agent 6 (Drive Dispatcher)
    drive_agent = DriveDispatcherAgent()
    vtt_path = str(PROJECT_ROOT / "public" / "subs.vtt")
    dispatch_res = drive_agent.upload_reel(
        video_path=rendered_video_path,
        vtt_path=vtt_path,
        meta_data={
            "title": topic_title,
            "category": topic_cat,
            "hook": script_data.get("hook", {}).get("headline"),
            "duration": audio_result.get("duration"),
            "environment": script_data.get("environment"),
            "characters": [c.get("name", "") for c in script_data.get("characters", [])],
        },
        drive_folder_id=drive_folder_id
    )

    elapsed = time.time() - start_time
    print("\n" + "=" * 70)
    print("  🎉 FULL PIPELINE EXECUTION COMPLETED")
    print(f"  ⏱️ Total Elapsed Time: {elapsed:.1f}s")
    print(f"  🎬 Rendered Video    : {rendered_video_path}")
    print(f"  ☁️ Cloud Dispatch    : {dispatch_res.get('status')} -> {dispatch_res.get('mirror_path')}")
    print("=" * 70)
    return rendered_video_path


def main():
    parser = argparse.ArgumentParser(description="Run Antigravity Autonomous Video Orchestrator")
    parser.add_argument("--insta", "--recreate", type=str, default=None, help="Instagram Reel URL, video file, or topic to recreate and remix")
    parser.add_argument("--morning-batch", action="store_true", help="Run daily morning batch (generates 2-3 reels)")
    parser.add_argument("--count", type=int, default=3, help="Number of reels in morning batch (2 or 3)")
    parser.add_argument("--schedule-morning", action="store_true", help="Set up daily morning cron schedule (08:30 AM)")
    parser.add_argument("--topic", type=str, default=None, help="Custom topic override")
    parser.add_argument("--topic-id", type=str, default=None, help="Exact topic ID (e.g. diner_fellow_3850, dad_vs_wifi_ai)")
    parser.add_argument("--category", type=str, default=None, help="Category (e.g. 'AI vs Dad', 'AI vs AI', 'AI vs Humans')")
    parser.add_argument("--out", type=str, default=None, help="Custom output filename")
    parser.add_argument("--drive-folder", type=str, default=None, help="Google Drive folder ID")
    args = parser.parse_args()

    if args.schedule_morning:
        setup_cron_schedule(hour=8, minute=30)
    elif args.morning_batch:
        run_morning_batch(count=args.count, drive_sync=bool(args.drive_folder), drive_folder_id=args.drive_folder)
    else:
        run_pipeline(
            topic_override=args.topic,
            topic_id=args.topic_id,
            category=args.category,
            insta_url=args.insta,
            output_filename=args.out,
            drive_folder_id=args.drive_folder
        )


if __name__ == "__main__":
    main()
