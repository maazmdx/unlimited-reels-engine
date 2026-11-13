#!/usr/bin/env python3
"""
Antigravity Master Multi-Agent Orchestrator
Coordinates the 6 autonomous subagents in an end-to-end quality feedback loop:
Agent 1: Trend & Ragebait Researcher
Agent 2: Viral Hook Director & Multi-Character Screenwriter
Agent 3: Neural Voice & SFX Sound Designer
Agent 4: Remotion Visual Scene & Render Compiler
Agent 5: Autonomous Multi-Loop Quality Auditor (Loops if quality < 90%)
Agent 6: Google Drive Cloud Dispatcher
"""

import sys
import os
import time
import json
import argparse
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from engine.agents.trend_researcher import TrendResearcherAgent
from engine.agents.script_director import ScriptDirectorAgent
from engine.agents.audio_director import AudioDirectorAgent
from engine.agents.scene_director import SceneDirectorAgent
from engine.agents.quality_auditor import QualityAuditorAgent
from engine.agents.drive_dispatcher import DriveDispatcherAgent

BANNER = r"""
======================================================================
  🤖 ANTIGRAVITY MULTI-AGENT AUTONOMOUS VIDEO ORCHESTRATOR
  Quality Guarantee : Multi-Loop Watchdog Audit (95%+ Target)
  Acoustics         : Multi-Voice Neural Edge-TTS + Pitch Deepening
  Visual Scene      : 2.5D Animated Engine (Weather, Props, Zooms)
  Cloud Delivery    : Automated Google Drive Sync with Captions
======================================================================
"""


def run_pipeline(
    topic_override: str = None,
    output_filename: str = None,
    drive_folder_id: str = None,
    max_audit_attempts: int = 3
) -> str:
    print(BANNER)
    start_time = time.time()

    # Step 1: Agent 1 (Trend Researcher)
    researcher = TrendResearcherAgent(topic_override=topic_override)
    topic_data = researcher.research_daily_topic()

    # Step 2: Agent 2 (Script Director)
    script_agent = ScriptDirectorAgent()
    script_data = script_agent.build_script(topic_data)

    # Step 3: Agent 3 (Audio Director)
    audio_agent = AudioDirectorAgent(project_root=PROJECT_ROOT)
    audio_result = audio_agent.synthesize_soundtrack(script_data)

    # Multi-Agent Quality Loop (Agents 4 & 5)
    scene_agent = SceneDirectorAgent(project_root=PROJECT_ROOT)
    auditor = QualityAuditorAgent(target_lufs=-14.0)

    if not output_filename:
        safe_title = "".join(c if c.isalnum() else "_" for c in topic_data["title"].lower()).strip("_")
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

        audit_res = auditor.audit_video(rendered_video_path)
        if audit_res["status"] == "PASS":
            passed_audit = True
            print("🏆 Quality Auditor Approved: Video passed all safety and broadcast standards!")
            break
        else:
            print(f"⚠️ Quality check failed on attempt {attempt}: {audit_res['reasons']}")
            time.sleep(1.0)

    if not passed_audit:
        print("⚠️ Warning: Proceeding with best-effort render after maximum audit attempts.")

    # Step 6: Agent 6 (Drive Dispatcher)
    drive_agent = DriveDispatcherAgent()
    vtt_path = str(PROJECT_ROOT / "public" / "subs.vtt")
    dispatch_res = drive_agent.upload_reel(
        video_path=rendered_video_path,
        vtt_path=vtt_path,
        meta_data={
            "title": topic_data["title"],
            "category": topic_data.get("category"),
            "hook": script_data["hook"],
            "duration": audio_result.get("duration"),
            "environment": script_data.get("environment"),
            "characters": [c["name"] for c in script_data.get("characters", [])],
        },
        drive_folder_id=drive_folder_id
    )

    elapsed = time.time() - start_time
    print("\n" + "=" * 70)
    print("  🎉 FULL PIPELINE EXECUTION COMPLETED")
    print(f"  ⏱️ Total Elapsed Time: {elapsed:.1f}s")
    print(f"  🎬 Rendered Video    : {rendered_video_path}")
    print(f"  ☁️ Cloud Dispatch    : {dispatch_res['status']} -> {dispatch_res['mirror_path']}")
    print("=" * 70)
    return rendered_video_path


def main():
    parser = argparse.ArgumentParser(description="Run Antigravity Autonomous Video Orchestrator")
    parser.add_argument("--topic", type=str, default=None, help="Custom topic override")
    parser.add_argument("--out", type=str, default=None, help="Custom output filename")
    parser.add_argument("--drive-folder", type=str, default=None, help="Google Drive folder ID")
    args = parser.parse_args()

    run_pipeline(
        topic_override=args.topic,
        output_filename=args.out,
        drive_folder_id=args.drive_folder
    )


if __name__ == "__main__":
    main()
