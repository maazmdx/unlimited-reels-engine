#!/usr/bin/env python3
import sys
import json
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from engine.agents.topic_master import TopicMasterAgent
from engine.agents.hook_master import HookMasterAgent
from engine.agents.seo_master import SEOMasterAgent

def main():
    print("=" * 65)
    print("🚀 LIVE DRY RUN: TopicMaster -> HookMaster -> SEOMaster")
    print("=" * 65)

    print("\n--- STEP 1: TOPIC MASTER ---")
    tm = TopicMasterAgent()
    topics = tm.curate_fresh_topics(count=1)
    if not topics:
        print("❌ No topics returned!")
        sys.exit(1)
    topic = topics[0]
    print(f"Title:       {topic.get('title')}")
    print(f"Viral Score: {topic.get('viral_score')}/100")
    print(f"Breakdown:   {topic.get('score_breakdown')}")
    print(f"Roast Angle: {topic.get('roast_angle')}")
    print(f"Keyword:     {topic.get('auto_dm_keyword')}")

    print("\n--- STEP 2: HOOK MASTER ---")
    hm = HookMasterAgent()
    screenplay = hm.craft_reel_screenplay(topic)
    turns = screenplay.get("dialogue", [])
    print(f"Screenplay Turns: {len(turns)}")
    print(f"Winning Hook:     \"{screenplay.get('winning_hook')}\"")
    print(f"Toast Data:       {json.dumps(screenplay.get('toastData'), indent=2)}")
    print(f"End Card:         {json.dumps(screenplay.get('endCard'), indent=2)}")

    print("\n--- STEP 3: SEO MASTER ---")
    seo = SEOMasterAgent()
    assets = seo.generate_seo_assets(screenplay)
    print(f"SEO Headline:     {assets.get('seo_headline')}")
    print(f"Pinned Bait:      {assets.get('pinned_comment')}")
    print(f"Hashtags:         {' '.join(assets.get('tiered_hashtags', []))}")
    print(f"Auto-DM Replies:  {json.dumps(assets.get('autodm_payload', {}).get('public_comment_replies'), indent=2)}")

    print("\n--- FULL 11-12 TURN DIALOGUE ---")
    for i, turn in enumerate(turns):
        print(f"Turn {i:02d} [{turn.get('speaker').upper()}]: {turn.get('text')}")

    print("\n" + "=" * 65)
    print("✅ DRY RUN PIPELINE COMPLETED SUCCESSFULLY!")
    print("=" * 65)

if __name__ == "__main__":
    main()
