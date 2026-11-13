"""
Agent 3: Neural Voice & SFX Sound Designer
Synthesizes distinct character voices via Edge-TTS with Hz pitch deepening, emotional prosody,
dramatic punchline pauses, and broadcast DSP mastering.
"""

import os
import sys
from pathlib import Path
from typing import Dict, Any

# Ensure project root in sys.path
PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from engine.tts_engine import generate_dialogue_speech


class AudioDirectorAgent:
    """Agent 3: Synthesizes dialogue voiceover with distinct character acoustics and subtitles."""

    def __init__(self, project_root: Path = PROJECT_ROOT):
        self.project_root = project_root
        self.public_dir = self.project_root / "public"
        self.public_dir.mkdir(parents=True, exist_ok=True)

    def synthesize_soundtrack(self, script_data: Dict[str, Any]) -> Dict[str, Any]:
        print("🎙️ [Agent 3: Audio Director] Synthesizing neural character voices & sound design...")
        dialogue = script_data.get("dialogue", [])

        out_audio = str(self.public_dir / "voice.mp3")
        out_vtt = str(self.public_dir / "subs.vtt")
        out_json = str(self.public_dir / "subs.json")
        meta_json = str(self.public_dir / "video-meta.json")

        result = generate_dialogue_speech(
            dialogue=dialogue,
            out_audio=out_audio,
            out_vtt=out_vtt,
            out_json=out_json,
            meta_json=meta_json,
            title=script_data.get("title", "Daily AI Reel"),
            pause_between_turns=0.32,
        )

        print(f"✅ [Agent 3] Audio generated: {result['duration']:.2f}s ({result['frames']} frames)")
        return result


if __name__ == "__main__":
    from engine.agents.script_director import ScriptDirectorAgent
    script = ScriptDirectorAgent().build_script({"id": "boiler_plate_blunder"})
    audio_agent = AudioDirectorAgent()
    res = audio_agent.synthesize_soundtrack(script)
    print("Audio Synthesis Success:", res["duration"])
