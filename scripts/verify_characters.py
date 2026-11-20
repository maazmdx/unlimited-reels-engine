#!/usr/bin/env python3
"""
Validation script for Modular Low-Poly 3D Character Rigs.
Verifies engine/config/characters.json configuration, 3D rig components,
palettes, and Three.js geometry assets.
"""

import sys
import json
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
CONFIG_FILE = PROJECT_ROOT / "engine" / "config" / "characters.json"
CHARACTERS_3D_DIR = PROJECT_ROOT / "my-edu-reels" / "src" / "components" / "characters3d"

REQUIRED_CHARACTERS = ["junior_dev", "dad", "claude", "gemini", "grok", "antigravity_bot"]
REQUIRED_PALETTE_KEYS = ["primary", "secondary", "accent", "skin", "shell", "eyeGlow"]


def verify_characters():
    print("🔍 [verify_characters.py] Auditing Modular Low-Poly 3D Character Rigs...")

    if not CONFIG_FILE.exists():
        print(f"❌ Config file not found at: {CONFIG_FILE}")
        return False

    with open(CONFIG_FILE, "r") as f:
        registry = json.load(f)

    print(f"📋 Loaded {len(registry)} character profiles from {CONFIG_FILE.name}\n")

    # Verify 3D rig files
    human_rig = CHARACTERS_3D_DIR / "LowPolyHumanRig.tsx"
    orb_rig = CHARACTERS_3D_DIR / "LowPolyAIOrbRig.tsx"
    index_file = CHARACTERS_3D_DIR / "index.ts"

    for fpath in [human_rig, orb_rig, index_file]:
        if not fpath.exists():
            print(f"❌ Missing 3D rig file: {fpath}")
            return False
        print(f"✅ Verified 3D Rig Component: {fpath.name}")

    print()
    all_ok = True

    for char_id in REQUIRED_CHARACTERS:
        if char_id not in registry:
            print(f"❌ Missing required character in registry: {char_id}")
            all_ok = False
            continue

        meta = registry[char_id]
        c_type = meta.get("type")
        c_rig = meta.get("rig_component")
        palette = meta.get("palette", {})
        pos = meta.get("default_position")
        voice = meta.get("voice_profile")

        if c_type not in ["human", "ai_orb"]:
            print(f"❌ Character {char_id} has invalid type: {c_type}")
            all_ok = False

        if c_type == "human" and c_rig != "LowPolyHumanRig":
            print(f"❌ Human {char_id} should use LowPolyHumanRig (got {c_rig})")
            all_ok = False

        if c_type == "ai_orb" and c_rig != "LowPolyAIOrbRig":
            print(f"❌ AI Orb {char_id} should use LowPolyAIOrbRig (got {c_rig})")
            all_ok = False

        # Check palette
        for k in REQUIRED_PALETTE_KEYS:
            if k not in palette:
                print(f"⚠️ Character {char_id} missing palette key: {k}")

        if not isinstance(pos, list) or len(pos) != 3:
            print(f"❌ Character {char_id} missing valid default_position [x, y, z]")
            all_ok = False

        if not voice:
            print(f"❌ Character {char_id} missing voice_profile placeholder")
            all_ok = False

        print(f"✅ Verified character '{char_id}' ({c_type} -> {c_rig})")

    print("\n" + "=" * 60)
    if all_ok:
        print("🎉 ALL 3D LOW-POLY CHARACTER RIGS & CONFIGS VERIFIED SUCCESSFULLY!")
    else:
        print("❌ VERIFICATION FAILED")

    return all_ok


if __name__ == "__main__":
    success = verify_characters()
    sys.exit(0 if success else 1)
