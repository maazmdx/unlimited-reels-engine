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

from engine.agents.topic_master import TopicMasterAgent
from engine.agents.hook_master import HookMasterAgent
from engine.agents.seo_master import SEOMasterAgent
from engine.agents.insta_analyzer import InstaAnalyzerAgent
from engine.agents.recreation_director import RecreationDirectorAgent
from engine.agents.audio_director import AudioDirectorAgent
from engine.agents.scene_director import SceneDirectorAgent
from engine.agents.quality_auditor import QualityAuditorAgent
from engine.agents.drive_dispatcher import DriveDispatcherAgent
from engine.agents.instagram_publisher import InstagramPublisherAgent
from engine.tts_engine import export_srt_file

BANNER = r"""
======================================================================
  🌅 ANTIGRAVITY MORNING BATCH VIDEO ENGINE (2-3 DAILY REELS)
  Intelligence: TopicMaster -> HookMaster -> SEOMaster
  Production  : AudioDirector -> SceneDirector -> QualityAuditor
  Delivery    : out/morning_YYYY_MM_DD/ + Captions + Drive Sync
======================================================================
"""

def load_content_pillars_pool() -> List[Dict[str, Any]]:
    """Loads rich rotating viral matrix across all 6 content pillars from content_pillars.json."""
    pillars_file = PROJECT_ROOT / "engine" / "config" / "content_pillars.json"
    if pillars_file.exists():
        try:
            with open(pillars_file, "r", encoding="utf-8") as f:
                data = json.load(f)
            pool = []
            for pillar in data.get("pillars", []):
                for topic in pillar.get("topics", []):
                    item = dict(topic)
                    item["pillar_name"] = pillar.get("name")
                    item["style"] = "diner_ai" if topic.get("format_type") != "ai_vs_dad" else "ai_vs_dad"
                    pool.append(item)
            if pool:
                return pool
        except Exception as e:
            print(f"⚠️ Failed loading content_pillars.json: {e}")

    # Fallback minimal pool if config missing
    return [
        {
            "id": "gta_vice_city_web",
            "title": "GTA Vice City Running 100% in Browser",
            "hook": "You can play full GTA Vice City directly inside Google Chrome without installing a single file.",
            "core_topic": "WebAssembly GTA Vice City Port",
            "format_type": "ai_vs_dev",
            "left_character": "junior_dev",
            "right_character": "claude",
            "cta_keyword": "VICE",
            "cta_phrase": "Comment VICE and I'll DM you the direct playable browser link.",
            "card_title": "WebAssembly Vice City Benchmark",
            "card_data": {"engine": "WebAssembly + WebGL2", "framerate": "Locked 60 FPS", "download": "0 MB"}
        },
        {
            "id": "notebooklm_deep_dive",
            "title": "Google NotebookLM Turning 200-Page PDFs into Deep Dive Podcasts",
            "hook": "Stop reading 200-page corporate PDF documents when Google will turn them into a Joe Rogan style podcast.",
            "core_topic": "NotebookLM Audio Overviews",
            "format_type": "ai_vs_dev",
            "left_character": "junior_dev",
            "right_character": "gemini",
            "cta_keyword": "NOTEBOOK",
            "cta_phrase": "Comment NOTEBOOK and I'll DM you the exact prompt template and workflow.",
            "card_title": "NotebookLM Audio Synthesis",
            "card_data": {"source_capacity": "50 Sources", "hallucination": "0% Grounded", "cost": "$0.00"}
        },
        {
            "id": "openrouter_pros_and_cons",
            "title": "OpenRouter Honest Review: 3 Real Pros vs 3 Nasty Cons",
            "hook": "Everyone on Twitter is hyping OpenRouter as the ultimate AI tool, but nobody mentions the hidden markup and latency spikes.",
            "core_topic": "OpenRouter Pros and Cons Teardown",
            "format_type": "ai_vs_dev",
            "left_character": "junior_dev",
            "right_character": "claude",
            "cta_keyword": "ROUTER",
            "cta_phrase": "Comment ROUTER and I'll DM you the unbiased routing cheat sheet.",
            "card_title": "OpenRouter: Hype vs Reality",
            "card_data": {"pro": "Single API for 200+ Models", "con": "50-150ms Added Latency", "cost": "0 Monthly Minimum"}
        },
        {
            "id": "dad_vs_cloud_backup",
            "title": "Dad Discovers Cloud Storage Subscription on Credit Card",
            "hook": "Why are you paying Google two hundred rupees every month for clouds?! Clouds are in the sky for free!",
            "core_topic": "Indian Dad Cloud Storage Outrage",
            "format_type": "ai_vs_dad",
            "left_character": "dad",
            "right_character": "claude",
            "cta_keyword": "MEME",
            "cta_phrase": "Comment MEME and I'll DM you the free unlimited self-hosted photo backup guide.",
            "card_title": "Indian Dad Storage Economics",
            "card_data": {"google_fee": "₹130/month Recurring", "dad_fix": "4GB Kingston Pen Drive in Cupboard", "cost": "₹0 Forever"}
        }
    ]


CURATED_MORNING_POOL = load_content_pillars_pool()

SCENE_MOODS = [
    ("diner", "rain"),    # 1. Rainy Midnight Diner
    ("diner", "sunny"),   # 2. Sunny Morning Diner (warm sunbeams)
    ("desk", "sunset"),   # 3. Purple Twilight Desk
]


def load_covered_topics_history(covered_file: Path) -> List[Dict[str, Any]]:
    """Loads historical covered topics from inbox/covered_topics.json."""
    if not covered_file.exists():
        return []
    try:
        with open(covered_file, "r", encoding="utf-8") as f:
            data = json.load(f)
        return data if isinstance(data, list) else []
    except Exception as e:
        print(f"⚠️ Error reading covered_topics.json: {e}")
        return []


def record_covered_topic(covered_file: Path, record: Dict[str, Any]):
    """Appends covered topic with episode tracking to inbox/covered_topics.json and channel_memory.json."""
    history = load_covered_topics_history(covered_file)
    history.append(record)
    try:
        covered_file.parent.mkdir(parents=True, exist_ok=True)
        with open(covered_file, "w", encoding="utf-8") as f:
            json.dump(history, f, indent=2)
        print(f"💾 [Covered Topics] Recorded {record.get('episode_str', 'Ep')} into inbox/covered_topics.json")
    except Exception as e:
        print(f"⚠️ Failed to update covered_topics.json: {e}")

    try:
        tm = TopicMasterAgent(project_root=PROJECT_ROOT)
        tm.update_channel_memory(record)
    except Exception as e:
        print(f"⚠️ Failed to update channel_memory.json from runner: {e}")


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
    """
    Generates an algorithm-optimized, searchable Instagram Reel caption:
    - Searchable hook headline
    - 2-3 bullet value summary with natural keywords
    - Comment [KEYWORD] for Auto-DM CTA
    - 8-12 targeted niche + mid-volume hashtags
    """
    title = script_data.get("title", "AI vs Humans")
    hook_data = script_data.get("hook", {})
    if isinstance(hook_data, dict):
        hook_tag = hook_data.get("tag", "⚠️ REAL TALK")
        hook_headline = hook_data.get("headline", title)
        hook_sub = hook_data.get("subheadline", "")
    else:
        hook_tag = "⚠️ REAL TALK"
        hook_headline = title
        hook_sub = str(hook_data)

    cta_kw = str(script_data.get("cta_keyword") or script_data.get("ctaKeyword", "LINK")).strip().upper()

    # Generate 2-3 value bullets from cardData or dialogue
    card_data = script_data.get("cardData") or {}
    bullets = []
    if isinstance(card_data, dict):
        for k, v in list(card_data.items())[:3]:
            clean_k = k.replace("_", " ").title()
            bullets.append(f"• {clean_k}: {v}")

    if not bullets:
        bullets = [
            "• Tested live in production with real metrics",
            "• Zero-cost setup vs overpriced cloud tools",
            "• Complete workflow breakdown & prompt template"
        ]

    bullets_text = "\n".join(bullets)

    # SEO Keywords line for Instagram Search indexing
    seo_keywords = script_data.get("seo_keywords", [])
    seo_str = " | ".join(seo_keywords[:4]) if seo_keywords else title

    # Targeted niche & mid-volume hashtags (8-12 tags)
    hashtags = script_data.get("hashtags", [])
    if not hashtags or len(hashtags) < 8:
        hashtags = [
            "#TechReels", "#DeveloperLife", "#SoftwareEngineering", "#CodingHumor",
            "#AIUpdates", "#DevCommunity", "#TechHacks", "#WebDevelopment",
            "#ArtificialIntelligence", "#Programming"
        ]
    hashtags_str = " ".join(hashtags[:12])

    caption = (
        f"{hook_tag} {hook_headline}\n\n"
        f"{hook_sub}\n\n"
        f"Key Breakdown:\n"
        f"{bullets_text}\n\n"
        f"🔍 Search keywords: {seo_str}\n\n"
        f"💬 Comment \"{cta_kw}\" below and I'll send you the link right to your DMs!\n\n"
        f"Follow @antigravity for daily zero-dollar AI workflows, developer humor & deep breakdowns!\n\n"
        f"{hashtags_str}"
    )
    return caption


def generate_autodm_config(script_data: Dict[str, Any]) -> Dict[str, Any]:
    """Generates structured config for ManyChat or Instagram Auto-DM automation."""
    cta_kw = str(script_data.get("cta_keyword") or script_data.get("ctaKeyword", "LINK")).strip().upper()
    title = script_data.get("title", "Resource Guide")
    dm_msg = script_data.get("dm_message") or f"Hey! Here is the direct link and guide for {title}."

    return {
        "keyword": cta_kw,
        "reply_comment_text": "Check your DMs! 🚀 Sent the full guide.",
        "dm_message_template": dm_msg,
        "resource_topic": title,
        "created_at": datetime.now().isoformat()
    }


def run_morning_batch(
    count: int = 2,
    drive_sync: bool = False,
    drive_folder_id: Optional[str] = None,
    insta_url: Optional[str] = None,
    scene_preset: str = "diner",
    auto_publish: bool = False
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
        print("ℹ️ Inbox queue empty. Defaulting to 3-Master Agent Chain (TopicMaster -> HookMaster -> SEOMaster).")

    # Initialize specialist master agents & production directors
    topic_master = TopicMasterAgent(project_root=PROJECT_ROOT)
    hook_master = HookMasterAgent(project_root=PROJECT_ROOT)
    seo_master = SEOMasterAgent(project_root=PROJECT_ROOT)
    insta_analyzer = InstaAnalyzerAgent(project_root=PROJECT_ROOT)
    recreation_director = RecreationDirectorAgent(project_root=PROJECT_ROOT)
    audio_director = AudioDirectorAgent(project_root=PROJECT_ROOT)
    scene_director = SceneDirectorAgent(project_root=PROJECT_ROOT)
    quality_auditor = QualityAuditorAgent(project_root=PROJECT_ROOT)
    drive_dispatcher = DriveDispatcherAgent() if drive_sync else None

    processed_urls = []
    generated_reels = []

    # Priority 1: Queued URLs from inbox/insta_queue.txt
    items_to_process = []
    if insta_url and insta_url.strip():
        print(f"🎯 Target URL Override: {insta_url.strip()}")
        items_to_process.append({"type": "url", "data": insta_url.strip()})
    else:
        for u in queued_urls[:count]:
            items_to_process.append({"type": "url", "data": u})
            processed_urls.append(u)

    # Priority 2: TopicMasterAgent (Consumer Tech, AI Apps, Browser Games, Business Models)
    needed = count - len(items_to_process)
    if needed > 0:
        print(f"📡 [Intelligence: TopicMaster] Curating {needed} mass-appeal viral topic(s)...")
        try:
            fresh_topics = topic_master.curate_fresh_topics(count=needed)
            for topic in fresh_topics:
                items_to_process.append({"type": "dynamic", "data": topic})
        except Exception as e:
            print(f"⚠️ TopicMaster curation notice: {e}")

    # Priority 3: Emergency Offline Fallback from content_pillars.json
    if len(items_to_process) < count:
        print("⚠️ Falling back to offline emergency content pillars matrix.")
        pool_index = datetime.now().timetuple().tm_yday
        while len(items_to_process) < count:
            candidate = CURATED_MORNING_POOL[pool_index % len(CURATED_MORNING_POOL)]
            if candidate not in [it["data"] for it in items_to_process if it["type"] == "pool"]:
                items_to_process.append({"type": "pool", "data": candidate})
            pool_index += 1

    covered_file = PROJECT_ROOT / "inbox" / "covered_topics.json"
    covered_history = load_covered_topics_history(covered_file)
    current_episode_count = len(covered_history)

    # Execute sequential generation chain for each item
    for idx, item in enumerate(items_to_process, 1):
        ep_num = current_episode_count + idx
        ep_str = f"Ep. {ep_num:02d}"
        next_ep_str = f"Ep. {ep_num + 1:02d}"

        # Auto-Rotate 3 distinct scene moods:
        # 1. ("diner", "rain") — Rainy Midnight Diner
        # 2. ("diner", "sunny") — Sunny Morning Diner (warm sunbeams)
        # 3. ("desk", "sunset") — Purple Twilight Desk
        preset_mood, weather_mood = SCENE_MOODS[(ep_num - 1) % len(SCENE_MOODS)]
        selected_scene = scene_preset if (scene_preset and scene_preset != "auto") else preset_mood

        print(f"\n" + "=" * 70)
        print(f"  🎬 PRODUCING MORNING REEL #{idx} OF {len(items_to_process)} [{ep_str}]")
        print(f"  🎨 Scene Mood Rotation: {selected_scene} ({weather_mood}) | Follow for {next_ep_str}")
        print("  Sequential Chain: TopicMaster -> HookMaster -> SEOMaster -> Audio -> Scene -> Audit")
        print("=" * 70)

        # 1. Topic Master / Ingestion Stage
        if item["type"] == "url":
            print(f"🔗 [Topic Ingestion] Queued URL -> {item['data']}")
            analysis = insta_analyzer.analyze_from_url_or_query(item["data"])
            topic_payload = {
                "title": analysis.get("title", "Remixed Viral Reel"),
                "topic_title": analysis.get("title", "Remixed Viral Reel"),
                "category": analysis.get("category", "Trending Social Remix"),
                "auto_dm_keyword": analysis.get("cta_keyword", "LINK"),
                "left_character": analysis.get("left_character", "junior_dev"),
                "right_character": analysis.get("right_character", "claude"),
                "scene_preset": selected_scene,
                "weather": weather_mood,
                "core_conflict": analysis.get("core_conflict", "Social hype vs engineering facts"),
                "viral_score": 85,
                "card_data": analysis.get("card_data") or analysis.get("cardData", {}),
            }
        elif item["type"] == "dynamic":
            topic_payload = item["data"]
            topic_payload["scene_preset"] = selected_scene
            topic_payload["weather"] = weather_mood
            print(f"🔥 [TopicMaster] Curated: {topic_payload.get('title')} | Score: {topic_payload.get('viral_score', 85)}/100 [{topic_payload.get('category')}]")
        else:
            pool_data = item["data"]
            print(f"🎯 [Offline Fallback] Picked: {pool_data.get('title') or pool_data.get('topic')}")
            topic_payload = {
                "title": pool_data.get("title", "Offline Tech Breakdown"),
                "topic_title": pool_data.get("title", "Offline Tech Breakdown"),
                "category": pool_data.get("pillar_style") or pool_data.get("category", "Retro Tech"),
                "auto_dm_keyword": pool_data.get("cta_keyword", "TECH"),
                "left_character": pool_data.get("left_character", "junior_dev"),
                "right_character": pool_data.get("right_character", "claude"),
                "scene_preset": selected_scene,
                "weather": weather_mood,
                "core_conflict": pool_data.get("core_conflict", "Dev nostalgia vs reality"),
                "viral_score": 82,
                "card_data": pool_data.get("card_data", {}),
            }

        # 2. HookMaster Stage (0-3s Hook Battle + Tight Screenplay)
        print("⚡ [HookMaster] Conducting 0-3s Hook Battle and writing screenplay...")
        script_data = hook_master.craft_reel_screenplay(topic_payload)
        script_data["scenePreset"] = selected_scene
        script_data["environment"] = selected_scene
        script_data["weather"] = weather_mood
        script_data["weatherMode"] = weather_mood
        script_data["episode_number"] = ep_num
        script_data["episode_str"] = ep_str
        if not script_data.get("endCard"):
            script_data["endCard"] = {}
        script_data["endCard"]["subtext"] = f"Follow for {next_ep_str}"

        # 3. AudioDirector Stage (Neural character voices & DSP mastering)
        print("🎙️ [AudioDirector] Synthesizing neural character voices & audio mastering...")
        audio_res = audio_director.synthesize_soundtrack(script_data)

        # 4 & 5. SceneDirector & QualityAuditor Stages (Remotion Render & 5-Stage Audit Loop)
        safe_title = "".join(c if c.isalnum() else "_" for c in script_data["title"].lower()).strip("_")[:30]
        output_filename = f"reel_{idx:02d}_{safe_title}.mp4"

        max_attempts = 2
        rendered_mp4 = None
        audit_res = None

        for attempt in range(1, max_attempts + 1):
            print(f"\n🔄 [SceneDirector & QualityAuditor] Render & Audit Attempt {attempt}/{max_attempts}...")
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
        if Path(rendered_mp4).exists() and os.path.realpath(str(rendered_mp4)) != os.path.realpath(str(final_video_dest)):
            shutil.copy2(rendered_mp4, final_video_dest)

        # Copy exported 4:5 cover still beside the MP4 in morning batch directory
        cover_src = Path(rendered_mp4).with_name(f"{Path(rendered_mp4).stem}_cover.png")
        cover_dest = batch_dir / f"{Path(output_filename).stem}_cover.png"
        if cover_src.exists():
            if os.path.realpath(str(cover_src)) != os.path.realpath(str(cover_dest)):
                shutil.copy2(cover_src, cover_dest)
            print(f"🖼️ [Cover Still] Delivered beside MP4: {cover_dest.name}")

        # Export clean, standard SubRip captions (.srt) beside MP4 in morning batch directory
        final_srt_dest = batch_dir / f"{Path(output_filename).stem}.srt"
        srt_source = audio_res.get("chunks") or (PROJECT_ROOT / "public" / "subs.json")
        try:
            export_srt_file(srt_source, final_srt_dest)
            print(f"📝 [SRT Subtitles] Delivered beside MP4: {final_srt_dest.name}")
        except Exception as e_srt:
            print(f"⚠️ [SRT Subtitles] Notice: {e_srt}")

        # Copy audit keyframes to thumbs directory
        for kf in audit_res.get("keyframes", []):
            if kf.get("path") and Path(kf["path"]).exists():
                src_kf = kf["path"]
                dst_kf = thumbs_dir / Path(kf["path"]).name
                if os.path.realpath(str(src_kf)) != os.path.realpath(str(dst_kf)):
                    shutil.copy2(src_kf, dst_kf)

        # 6. SEOMaster Stage (Instagram Discovery, Pinned Debate Bait, Anti-Throttle Auto-DM)
        print("🔍 [SEOMaster] Generating SEO headline, pinned comment bait, and 3-reply Auto-DM config...")
        file_prefix = f"reel_{idx:02d}_{safe_title}"
        seo_assets = seo_master.generate_seo_assets(
            script_data=script_data,
            batch_dir=batch_dir,
            file_prefix=file_prefix,
        )
        caption_file = seo_assets["caption_path"]
        autodm_file = seo_assets["autodm_path"]

        # Optional Cloud Drive Sync
        drive_status = "SKIPPED"
        d_res = None
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

        # 7. Optional Official Meta Graph API Reels Auto-Publish (Default: OFF)
        ig_publish_status = "SKIPPED_FLAG_OFF"
        ig_permalink = None
        if auto_publish:
            try:
                publisher = InstagramPublisherAgent()
                if publisher.is_configured():
                    public_vid_url = None
                    if isinstance(drive_status, dict):
                        public_vid_url = drive_status.get("drive_link")
                    elif isinstance(d_res, dict):
                        public_vid_url = d_res.get("drive_link")

                    if public_vid_url:
                        pub_res = publisher.publish_reel(
                            video_url=public_vid_url,
                            caption=seo_assets.get("caption_text", ""),
                        )
                        ig_publish_status = pub_res.get("status", "FAILED")
                        ig_permalink = pub_res.get("permalink")
                    else:
                        print("ℹ️ [InstagramPublisher] No public video URL available for upload; skipping auto-publish.")
                        ig_publish_status = "SKIPPED_NO_PUBLIC_URL"
                else:
                    print("ℹ️ [InstagramPublisher] IG_USER_ID or IG_ACCESS_TOKEN not set; skipping auto-publish.")
                    ig_publish_status = "SKIPPED_NO_SECRETS"
            except Exception as e_pub:
                print(f"⚠️ [InstagramPublisher] Publishing notice: {e_pub}")
                ig_publish_status = f"ERROR: {e_pub}"

        # Resolve autodm_data cleanly from seo_assets or autodm_file or script_data
        autodm_data = seo_assets.get("autodm_payload") or {}
        if not autodm_data and autodm_file and Path(autodm_file).exists():
            try:
                with open(autodm_file, "r", encoding="utf-8") as f:
                    autodm_data = json.load(f)
            except Exception:
                pass
        cta_keyword_val = (
            autodm_data.get("keyword")
            or script_data.get("auto_dm_keyword")
            or script_data.get("cta_keyword")
            or "LINK"
        )

        # Record topic & episode number into inbox/covered_topics.json
        record_covered_topic(covered_file, {
            "slug": safe_title,
            "title": script_data["title"],
            "date": datetime.now().strftime("%Y-%m-%d"),
            "episode_number": ep_num,
            "episode_str": ep_str,
            "auto_dm_keyword": cta_keyword_val,
            "pillar_style": topic_payload.get("category", "AI Satire"),
            "scene_preset": selected_scene,
            "weather_mood": weather_mood
        })

        generated_reels.append({
            "index": idx,
            "episode_number": ep_num,
            "episode_str": ep_str,
            "title": script_data["title"],
            "video_path": str(final_video_dest),
            "cover_path": str(cover_dest) if cover_dest.exists() else None,
            "srt_path": str(final_srt_dest) if final_srt_dest.exists() else None,
            "caption_path": str(caption_file),
            "autodm_path": str(autodm_file),
            "cta_keyword": cta_keyword_val,
            "scene_preset": selected_scene,
            "weather_mood": weather_mood,
            "duration": audit_res.get("duration", 0),
            "quality_score": audit_res.get("score", 100),
            "status": audit_res.get("status", "PASS"),
            "drive_status": drive_status,
            "ig_status": ig_publish_status,
            "ig_permalink": ig_permalink,
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
        print(f"  🎬 Reel #{r['index']:02d}: {r['title']} [{r['duration']:.1f}s | Score: {r['quality_score']}/100 | Auto-DM: {r.get('cta_keyword')}]")
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
    parser.add_argument("--auto-publish", action="store_true", default=False, help="Automatically publish rendered reels to Instagram via Meta Graph API if credentials are set")
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
            auto_publish=args.auto_publish,
        )
