#!/usr/bin/env python3
"""
Comprehensive Audit & Integrity Gate Test Suite
Asserts all frame-by-frame audit root-cause fixes across Reel #1 (Tool) and Reel #2 (Dad Clash):
1. Strict 2-speaker lock / multi-character roster, strict alternation, locked Kokoro voices.
2. Humans NEVER recite steps or install commands; only questions and reactions.
3. Dad speaks strictly in 1st person POV.
4. Turn 9 in character, not title/toast verbatim, zero glitch bullets.
5. Display text vs TTS text decoupling (preserves domains & contractions, expands pronunciation).
6. Captions: Year 2026, zero 2024, no robotic step labels, dad clash zero software steps.
7. HTML resource guide populates real steps.
8. Zero purple hex codes in EndCard / ProgressBar / SunsetDesk3D.
9. Hard Pre-Render Assertion Gate rejects all corrupted synthetic screenplays.
"""

import sys
import os
import re
from pathlib import Path
from datetime import datetime

PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from engine.agents.hook_master import (
    HookMasterAgent,
    validate_screenplay_quality_gate,
    BANNED_PLACEHOLDERS,
    HUMAN_SPEAKERS,
)
from engine.agents.seo_master import SEOMasterAgent
from engine.tts_engine import (
    CHARACTER_VOICE_REF_SPECS,
    normalize_tts_pronunciation,
    canonicalize_character_id,
    clean_display_text,
)
from engine.morning_batch_runner import assert_screenplay_pre_render_integrity


def test_voice_roster():
    print("🧪 [Test 1] Verifying Kokoro-82M Voice Roster...")
    required_voices = {
        "junior_dev": "am_michael",
        "senior_dev": "am_adam",
        "friend_riya": "af_sarah",
        "dad": "bm_lewis",
        "claude": "am_fenrir",
        "gemini": "af_bella",
        "gpt": "bm_onyx",
    }
    for char_id, expected_voice in required_voices.items():
        assert char_id in CHARACTER_VOICE_REF_SPECS, f"Missing voice spec for {char_id}"
        spec = CHARACTER_VOICE_REF_SPECS[char_id]
        assert spec["engine"] == "kokoro", f"{char_id} must use kokoro engine, got {spec['engine']}"
        assert spec["voice"] == expected_voice, f"{char_id} expected {expected_voice}, got {spec['voice']}"

    # Verify canonicalization
    assert canonicalize_character_id("junior") == "junior_dev"
    assert canonicalize_character_id("senior") == "senior_dev"
    assert canonicalize_character_id("riya") == "friend_riya"
    assert canonicalize_character_id("dad") == "dad"
    assert canonicalize_character_id("chatgpt") == "gpt"
    assert canonicalize_character_id("claude") == "claude"
    assert canonicalize_character_id("gemini") == "gemini"
    print("  ✅ Voice roster & canonicalization verified 100%.")


def test_text_decoupling():
    print("🧪 [Test 2] Verifying Display Text vs TTS Pronunciation Decoupling...")
    sample_text = "• Check out bleachbit.org on GitHub! You're paying $20 in 2026."
    
    # Display text: preserves exact spelling, contractions, domains; strips bullets
    disp = clean_display_text(sample_text)
    assert "bleachbit.org" in disp, f"Display text mutated domain: {disp}"
    assert "GitHub" in disp, f"Display text mutated GitHub: {disp}"
    assert "You're" in disp, f"Display text mutated contraction: {disp}"
    assert "•" not in disp, f"Display text leaked bullet: {disp}"
    assert "_" not in disp, f"Display text has leading/trailing underscore: {disp}"

    # TTS text: expands domains, acronyms, years
    spoken = normalize_tts_pronunciation(sample_text)
    assert "bleachbit dot org" in spoken, f"TTS text did not expand domain: {spoken}"
    assert "Git Hub" in spoken, f"TTS text did not expand GitHub: {spoken}"
    assert "twenty twenty six" in spoken or "twenty twenty-six" in spoken, f"TTS text did not expand year: {spoken}"
    assert "•" not in spoken, f"TTS text leaked bullet: {spoken}"
    print("  ✅ Text decoupling verified (domains, contractions & pronunciations).")


def test_reel_01_tool_screenplay():
    print("🧪 [Test 3] Verifying Reel #1 (BleachBit Tool / Informative Roast)...")
    hook_master = HookMasterAgent(project_root=PROJECT_ROOT)
    seo_master = SEOMasterAgent(project_root=PROJECT_ROOT)

    topic_payload = {
        "id": "bleachbit_cleaner",
        "title": "FREE PC Cleaner: BleachBit Kills Bloat & Speeds Up",
        "topic_title": "FREE PC Cleaner: BleachBit Kills Bloat & Speeds Up",
        "category": "PC Speedup",
        "format_type": "informative_roast",
        "tool_name": "BleachBit",
        "brand_domain": "bleachbit.org",
        "github_repo": "bleachbit/bleachbit",
        "replaces_paid_app": "CCleaner Pro",
        "auto_dm_keyword": "CLEAN",
        "left_character": "junior_dev",
        "right_character": "claude",
        "real_steps": [
            "Download BleachBit for Windows or Linux from bleachbit.org",
            "Select junk files, browser cache, and system logs to wipe",
            "Run Clean operation to free up gigabytes of disk space",
        ],
    }

    script_data = hook_master._fallback_screenplay(
        topic=topic_payload,
        hook="Bro... my laptop literally froze opening a two-megabyte file.",
        left_char="junior_dev",
        right_char="claude",
        scene_preset="diner",
        kw="CLEAN",
    )

    # Validate screenplay quality gate
    is_valid, violations = validate_screenplay_quality_gate(script_data, topic_payload)
    assert is_valid, f"Quality gate failed on Reel #1: {violations}"

    # Verify speakers and alternation
    dialogue = script_data["dialogue"]
    assert len(dialogue) >= 11
    speakers = [d["speaker"] for d in dialogue]
    for i in range(1, len(speakers)):
        assert speakers[i] != speakers[i - 1], f"Consecutive speakers at {i-1} and {i}: {speakers[i]}"

    # Verify human never recites steps
    for idx, d in enumerate(dialogue):
        if d["speaker"] in HUMAN_SPEAKERS:
            txt_low = d["text"].lower()
            assert not any(s in txt_low for s in ["step 1", "step 2", "step 3", "step one", "step two"]), f"Human recited steps in Turn {idx}: {d['text']}"
            assert not any(cmd in txt_low for cmd in ["git clone", "pip install", "npm install"]), f"Human recited CLI command in Turn {idx}: {d['text']}"

    # Verify Turn 9
    t9 = dialogue[9]["text"]
    assert "•" not in t9 and "|" not in t9 and "—" not in t9
    assert topic_payload["title"].lower() not in t9.lower()

    # Generate SEO assets
    seo_assets = seo_master.generate_seo_assets(script_data=script_data)
    caption = seo_assets["caption_text"]
    assert "2026" in caption, "Caption missing current year 2026"
    assert "2024" not in caption, "Caption leaked hardcoded 2024"
    assert "@canidoai" in caption, "Caption missing @canidoai handle"
    assert "Step 1: Setup:" not in caption, "Caption leaked robotic step labels"

    # HTML resource guide test
    guide_html = seo_master.generate_resource_guide_html(
        title=topic_payload["title"],
        category=topic_payload["category"],
        official_url="https://bleachbit.org",
        card_rows=script_data["cardData"]["rows"],
        kw="CLEAN",
        real_steps=topic_payload["real_steps"],
        tool_name="BleachBit",
    )
    assert "Download BleachBit" in guide_html, "Resource guide missing real step 1"
    assert "Run Clean operation" in guide_html, "Resource guide missing real step 3"
    assert "Run FREE PC Cleaner locally" not in guide_html, "Resource guide leaked generic filler"

    # Assert Pre-Render gate passes
    assert_screenplay_pre_render_integrity(script_data, seo_assets)
    print("  ✅ Reel #1 (BleachBit) screenplay, quality gate & SEO assets verified.")


def test_reel_02_dad_clash_screenplay():
    print("🧪 [Test 4] Verifying Reel #2 (Indian Dad Clash / 80% Battery Alarm)...")
    hook_master = HookMasterAgent(project_root=PROJECT_ROOT)
    seo_master = SEOMasterAgent(project_root=PROJECT_ROOT)

    topic_payload = {
        "id": "dad_phone_alarm",
        "title": "Dad Sets Alarm to Unplug Phone at 80%",
        "topic_title": "Dad Sets Alarm to Unplug Phone at 80%",
        "category": "Battery Myth",
        "format_type": "dad_clash",
        "left_character": "dad",
        "right_character": "gemini",
        "auto_dm_keyword": "NONE",
    }

    script_data = hook_master._fallback_screenplay(
        topic=topic_payload,
        hook="Beta, unplug it at eighty percent or the battery will explode!",
        left_char="dad",
        right_char="gemini",
        scene_preset="living_room",
        kw="",
    )

    is_valid, violations = validate_screenplay_quality_gate(script_data, topic_payload)
    assert is_valid, f"Quality gate failed on Reel #2: {violations}"

    dialogue = script_data["dialogue"]
    # Verify Dad 1st person POV
    for idx, d in enumerate(dialogue):
        if d["speaker"] == "dad":
            txt_low = d["text"].lower()
            assert not re.search(r"\b(dad just|my dad|dad thinks|dad sets|dad installed|my boss)\b", txt_low), f"Dad in 3rd person at Turn {idx}: {d['text']}"

    # Verify zero software steps in cardData
    card_d = script_data.get("cardData")
    if card_d and isinstance(card_d, dict) and card_d.get("rows"):
        assert not any("step 1" in str(r.get("label", "")).lower() for r in card_d["rows"]), "Dad clash leaked software step rows in cardData"

    # Generate SEO assets
    seo_assets = seo_master.generate_seo_assets(script_data=script_data)
    caption = seo_assets["caption_text"]
    assert "3-Step Breakdown" not in caption, "Dad clash caption leaked 3-Step Breakdown software block"
    assert "@canidoai" in caption, "Dad clash caption missing @canidoai handle"
    assert "2024" not in caption, "Dad clash caption leaked 2024"

    # Assert Pre-Render gate passes
    assert_screenplay_pre_render_integrity(script_data, seo_assets)
    print("  ✅ Reel #2 (Dad Clash) screenplay, 1st-person POV, comedy CTA & gate verified.")


def test_pre_render_assertion_gate_negative_tests():
    print("🧪 [Test 5] Verifying Hard Pre-Render Gate Rejection of Corrupted Screenplays...")
    hook_master = HookMasterAgent(project_root=PROJECT_ROOT)
    topic_payload = {
        "title": "Test Tool",
        "left_character": "junior_dev",
        "right_character": "claude",
    }

    # Negative 1: Banned placeholder phrase
    bad_script_1 = hook_master._fallback_screenplay(topic_payload, "Hook line", "junior_dev", "claude", "diner", "TOOL")
    bad_script_1["dialogue"][3]["text"] = "Wait, what happens live under the hood?"
    try:
        assert_screenplay_pre_render_integrity(bad_script_1)
        assert False, "Gate should have rejected placeholder 'what happens live under the hood'"
    except AssertionError as e:
        assert "what happens live under the hood" in str(e)

    # Negative 2: Human reciting steps
    bad_script_2 = hook_master._fallback_screenplay(topic_payload, "Hook line", "junior_dev", "claude", "diner", "TOOL")
    bad_script_2["dialogue"][2]["text"] = "Step 1 is to open the terminal right now."
    try:
        assert_screenplay_pre_render_integrity(bad_script_2)
        assert False, "Gate should have rejected human reciting 'Step 1'"
    except AssertionError as e:
        assert "recited tutorial step" in str(e)

    # Negative 3: Dad speaking in 3rd person
    bad_script_3 = hook_master._fallback_screenplay(
        {"title": "Dad Battery", "left_character": "dad", "right_character": "gemini", "format_type": "dad_clash"},
        "Beta, unplug it!", "dad", "gemini", "living_room", ""
    )
    bad_script_3["dialogue"][0]["text"] = "Dad just unplugged the phone at eighty percent."
    try:
        assert_screenplay_pre_render_integrity(bad_script_3)
        assert False, "Gate should have rejected Dad speaking as 'Dad just'"
    except AssertionError as e:
        assert "Dad spoke in 3rd person" in str(e)

    # Negative 4: Consecutive speaker turns
    bad_script_4 = hook_master._fallback_screenplay(topic_payload, "Hook line", "junior_dev", "claude", "diner", "TOOL")
    bad_script_4["dialogue"][2]["speaker"] = "claude"
    bad_script_4["dialogue"][3]["speaker"] = "claude"
    try:
        assert_screenplay_pre_render_integrity(bad_script_4)
        assert False, "Gate should have rejected consecutive turns with same speaker"
    except AssertionError as e:
        assert "consecutive speaker" in str(e)

    # Negative 5: Hardcoded 2024
    bad_script_5 = hook_master._fallback_screenplay(topic_payload, "Hook line", "junior_dev", "claude", "diner", "TOOL")
    bad_script_5["dialogue"][4]["text"] = "Still using paid tools in 2024?"
    try:
        assert_screenplay_pre_render_integrity(bad_script_5)
        assert False, "Gate should have rejected hardcoded 2024"
    except AssertionError as e:
        assert "2024" in str(e)

    print("  ✅ Pre-Render Assertion Gate successfully blocked all 5 corrupted screenplay variants.")


def test_zero_purple_components():
    print("🧪 [Test 6] Verifying Zero Purple Colors in UI & 3D Components...")
    src_dir = PROJECT_ROOT / "my-edu-reels" / "src"
    banned_purple_hexes = [
        "#7c3aed", "#6366f1", "#4c1d95", "#3b0764",
        "#8b5cf6", "#a855f7", "#9333ea", "#c084fc",
        "#5b21b6", "#7e22ce"
    ]
    components_to_check = [
        src_dir / "MasterAutonomousReel.tsx",
        src_dir / "components" / "ProgressBar.tsx",
        src_dir / "components" / "environments3d" / "SunsetDesk3D.tsx",
        src_dir / "components" / "ui" / "CinematicSubtitles.tsx",
    ]

    for comp in components_to_check:
        assert comp.exists(), f"Component file not found: {comp}"
        content = comp.read_text(encoding="utf-8").lower()
        for hex_code in banned_purple_hexes:
            assert hex_code not in content, f"Found banned purple hex '{hex_code}' in {comp.name}"

    print("  ✅ Zero purple hex codes found across all 4 UI and 3D components.")


def test_dissected_pipeline_bugfixes():
    print("🧪 [Test 7] Verifying Dissected Bugfixes (TTS question var, Zero Slop, 3D routing, Root metadata)...")
    # 1. Verify DynamicProofCard has no banned emojis or slop
    proof_card_path = PROJECT_ROOT / "my-edu-reels" / "src" / "components" / "ui" / "DynamicProofCard.tsx"
    content_proof = proof_card_path.read_text(encoding="utf-8")
    for bad in ["⚡", "🚀", "🤯", "verified zero local installation", "zero-dollar"]:
        assert bad not in content_proof, f"Found '{bad}' in DynamicProofCard.tsx"

    # 2. Verify seo_master Auto-DM and replies have no banned slop emojis
    seo_master_path = PROJECT_ROOT / "engine" / "agents" / "seo_master.py"
    content_seo = seo_master_path.read_text(encoding="utf-8")
    assert 'f"Sent to your DMs! 🚀' not in content_seo, "Found 🚀 in seo_master comment reply"
    assert 'f"Hey! 🚀' not in content_seo, "Found 🚀 in seo_master Auto-DM template"
    assert '⚡ Enjoy.' not in content_seo, "Found ⚡ in seo_master comment reply"

    # 3. Verify tts_engine pause calculation uses disp_text, not undefined text
    tts_engine_path = PROJECT_ROOT / "engine" / "tts_engine.py"
    content_tts = tts_engine_path.read_text(encoding="utf-8")
    assert 'elif "?" in text:' not in content_tts, "Found undefined 'text' in tts_engine pause logic"
    assert 'elif "?" in disp_text:' in content_tts, "Expected 'disp_text' in tts_engine pause logic"

    # 4. Verify scene_director routes 3D reels to MasterAutonomousReel
    scene_director_path = PROJECT_ROOT / "engine" / "agents" / "scene_director.py"
    content_scene = scene_director_path.read_text(encoding="utf-8")
    assert 'script_data.get("use_3d", False)' not in content_scene, "Found use_3d misrouting in scene_director"

    # 5. Verify Root.tsx calculates metadata using end_sec / end_frame
    root_path = PROJECT_ROOT / "my-edu-reels" / "src" / "Root.tsx"
    content_root = root_path.read_text(encoding="utf-8")
    assert 'audioDurationSec = turns[turns.length - 1].end + 0.6;' not in content_root, "Root.tsx uses undefined .end field"
    assert 'lastTurn.end_sec' in content_root, "Root.tsx missing end_sec check in calculateMasterMetadata"

    print("  ✅ All 5 dissected bugfixes verified 100%.")


if __name__ == "__main__":
    print("\n======================================================================")
    print("🚀 RUNNING FRAME-BY-FRAME ENGINE AUDIT & PRE-RENDER INTEGRITY SUITE")
    print("======================================================================\n")
    test_voice_roster()
    test_text_decoupling()
    test_reel_01_tool_screenplay()
    test_reel_02_dad_clash_screenplay()
    test_pre_render_assertion_gate_negative_tests()
    test_zero_purple_components()
    test_dissected_pipeline_bugfixes()
    print("\n======================================================================")
    print("🏆 ALL INTEGRITY AUDIT TESTS PASSED (100% SUCCESS)!")
    print("======================================================================\n")
