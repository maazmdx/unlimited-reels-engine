"""
sfx_manager.py - Antigravity Autonomous Sound Design Engine
Integrates:
1. Openverse API - Programmatic search and download of CC0 recorded sound effects
2. Real SFX - Frame-accurate cue alignment and multi-track audio mastering
3. Earshot - Acoustic auditing (LUFS, True Peak, AV sync, silence detection)
"""

import json
import os
import subprocess
import sys
from pathlib import Path
from typing import Dict, Any, List, Optional

# Import Openverse fetcher from ~/.agents/skills/openverse/scripts
sys.path.append(os.path.expanduser("~/.agents/skills/openverse/scripts"))
try:
    from fetch_openverse_sfx import search_audio, download_audio
except ImportError:
    search_audio = None
    download_audio = None

# Import Earshot auditor from ~/.agents/skills/earshot/scripts
sys.path.append(os.path.expanduser("~/.agents/skills/earshot/scripts"))
try:
    from audio_auditor import audit_audio, run_loudness_analysis
except ImportError:
    audit_audio = None
    run_loudness_analysis = None


class SFXManager:
    def __init__(self, project_root: Optional[Path] = None):
        self.project_root = Path(project_root or Path(__file__).resolve().parent.parent)
        self.sfx_dir = self.project_root / "public" / "sfx"
        self.sfx_dir.mkdir(parents=True, exist_ok=True)

    def ensure_sfx_kit(self, kit_name: str = "reel_standard") -> Dict[str, str]:
        """Ensures key sound effects are present locally; fetches CC0 audio from Openverse if missing."""
        default_sounds = {
            "whoosh": "whoosh air swish",
            "pop": "bubble pop ui",
            "impact": "cinematic bass impact hit",
            "chime": "bell chime"
        }
        downloaded = {}
        for key, query in default_sounds.items():
            candidate = list(self.sfx_dir.glob(f"{key}.*"))
            if candidate:
                downloaded[key] = str(candidate[0])
            else:
                if search_audio and download_audio:
                    print(f"🔍 [Openverse] Fetching missing CC0 sound effect for '{key}'...")
                    results = search_audio(query, license="cc0", page_size=3)
                    if results:
                        path = download_audio(results[0], target_dir=str(self.sfx_dir), filename_override=key)
                        if path:
                            downloaded[key] = path
                else:
                    print(f"⚠️ Openverse fetcher not loaded, cannot auto-fetch '{key}'")
        return downloaded

    def generate_cue_list(self, total_frames: int, fps: float = 30.0, sfx_map: Optional[Dict[str, str]] = None) -> Dict[str, Any]:
        """Automatically synthesizes a frame-accurate Real SFX cue list matching standard video pacing."""
        if not sfx_map:
            sfx_map = self.ensure_sfx_kit()

        cues = []
        # Frame 0: Hook transition whoosh
        if "whoosh" in sfx_map:
            cues.append({
                "frame": 0,
                "sfx": sfx_map["whoosh"],
                "volume": 0.85,
                "description": "Opening Hook Swish"
            })

        # Frame 30-45 (1.0-1.5s): Card/UI Pop
        if "pop" in sfx_map and total_frames > 60:
            cues.append({
                "frame": int(fps * 1.5),
                "sfx": sfx_map["pop"],
                "volume": 0.90,
                "description": "First Point Reveal"
            })

        # Midpoint Climax: Impact
        if "impact" in sfx_map and total_frames > int(fps * 5):
            climax_frame = int(total_frames * 0.45)
            cues.append({
                "frame": climax_frame,
                "sfx": sfx_map["impact"],
                "volume": 1.0,
                "description": "Core Climax Reveal"
            })

        # Climax Outro / CTA: Chime
        if "chime" in sfx_map and total_frames > int(fps * 8):
            cta_frame = max(0, total_frames - int(fps * 2.5))
            cues.append({
                "frame": cta_frame,
                "sfx": sfx_map["chime"],
                "volume": 0.75,
                "description": "Call to Action Chime"
            })

        return {
            "fps": fps,
            "master_lufs": -14.0,
            "cues": cues
        }

    def apply_sfx_to_video(
        self,
        video_path: str,
        cues: Dict[str, Any],
        output_path: str,
        voiceover_path: Optional[str] = None,
        bgm_path: Optional[str] = None,
        target_lufs: float = -14.0
    ) -> bool:
        """Invokes Real SFX mixing engine to produce a broadcast-ready audio master."""
        apply_script = os.path.expanduser("~/.agents/skills/real-sfx/scripts/apply_real_sfx.py")
        temp_cues_path = self.project_root / "public" / "temp_cues.json"

        with open(temp_cues_path, "w", encoding="utf-8") as f:
            json.dump(cues, f, indent=2)

        cmd = [
            "python3", apply_script,
            "--video", str(video_path),
            "--cues", str(temp_cues_path),
            "--output", str(output_path),
            "--lufs", str(target_lufs)
        ]
        if voiceover_path and os.path.isfile(voiceover_path):
            cmd.extend(["--voiceover", str(voiceover_path)])
        if bgm_path and os.path.isfile(bgm_path):
            cmd.extend(["--bgm", str(bgm_path)])

        print(f"🎬 [Real SFX] Applying frame-accurate sound effects to {output_path}...")
        res = subprocess.run(cmd, capture_output=True, text=True)
        if temp_cues_path.exists():
            temp_cues_path.unlink()

        if res.returncode != 0:
            print("❌ Real SFX application failed:", res.stderr)
            return False

        print("✅ [Real SFX] Sound design applied successfully.")
        return True

    def audit_master(self, video_path: str, target_lufs: float = -14.0) -> bool:
        """Runs Earshot acoustic audit against broadcast criteria."""
        if audit_audio:
            print(f"🎧 [Earshot] Auditing soundtrack for: {video_path}")
            return audit_audio(video_path, target_lufs=target_lufs)
        else:
            print("⚠️ Earshot auditor module not loaded.")
            return True


if __name__ == "__main__":
    manager = SFXManager()
    print("📦 Provisioning default CC0 sound kit from Openverse...")
    kit = manager.ensure_sfx_kit()
    print("Sound kit status:", kit)
