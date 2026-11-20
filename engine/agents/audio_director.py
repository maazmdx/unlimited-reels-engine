"""
Agent 3: Neural Voice & Lip-Sync Sound Designer
Synthesizes distinct character voices via Kokoro-82M (am_michael, bm_george, af_bella, am_fenrir, bm_lewis)
and Edge-TTS (authentic Indian Dad en-IN-PrabhatNeural at +0Hz), applies clean broadcast DSP mastering
(-14.0 LUFS, -22 dB lo-fi ambient bed), and exports synchronized 30fps lip-sync envelopes to timeline.json.
"""

import os
import sys
import shutil
from pathlib import Path
from typing import Dict, Any

# Ensure project root in sys.path
PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from engine.tts_engine import generate_dialogue_speech


class AudioDirectorAgent:
    """Agent 3: Synthesizes dialogue voiceover with distinct neural character acoustics and lip-sync timeline."""

    def __init__(self, project_root: Path = PROJECT_ROOT):
        self.project_root = project_root
        self.public_dir = self.project_root / "public"
        self.remotion_public = self.project_root / "my-edu-reels" / "public"
        self.public_dir.mkdir(parents=True, exist_ok=True)
        self.remotion_public.mkdir(parents=True, exist_ok=True)

    def synthesize_soundtrack(self, script_data: Dict[str, Any]) -> Dict[str, Any]:
        print("🎙️ [Agent 3: Audio Director] Synthesizing neural Kokoro & Edge-TTS voices & broadcast sound design...")
        dialogue = script_data.get("dialogue", [])

        out_audio = str(self.public_dir / "voice.mp3")
        out_vtt = str(self.public_dir / "subs.vtt")
        out_json = str(self.public_dir / "subs.json")
        meta_json = str(self.public_dir / "video-meta.json")
        timeline_json = str(self.public_dir / "timeline.json")

        result = generate_dialogue_speech(
            dialogue=dialogue,
            out_audio=out_audio,
            out_vtt=out_vtt,
            out_json=out_json,
            meta_json=meta_json,
            timeline_json=timeline_json,
            title=script_data.get("title", "Daily AI Reel"),
            pause_between_turns=0.20,
        )

        # Mirror output files to my-edu-reels/public for Remotion renderer
        for fname in ["voice.mp3", "voiceover.mp3", "master.mp3", "subs.vtt", "subs.json", "video-meta.json", "timeline.json"]:
            src = self.public_dir / fname
            dst = self.remotion_public / fname
            if src.exists():
                shutil.copy2(str(src), str(dst))

        print(f"✅ [Agent 3] Audio soundtrack generated: {result['duration']:.2f}s ({result['frames']} frames @ 30fps)")
        print(f"✅ [Agent 3] Timeline & mouth envelopes exported to {timeline_json}")
        return result


if __name__ == "__main__":
    from engine.agents.script_director import ScriptDirectorAgent
    script = ScriptDirectorAgent().build_script({"id": "boiler_plate_blunder"})
    audio_agent = AudioDirectorAgent()
    res = audio_agent.synthesize_soundtrack(script)
    print("Audio Synthesis Success:", res["duration"], "seconds")
