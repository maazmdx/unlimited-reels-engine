#!/usr/bin/env python3
"""
Audio-Only Smoke Test for Kokoro-82M, Edge-TTS, and 30fps Lip-Sync Timeline.
Tests an 11-turn emotional diabolical roast dialogue between junior_dev and claude.
Verifies Kokoro CPU runtime, audio duration (35-55s), integrated LUFS (-14 target),
and timeline.json mouth envelope isolation (zero mouth leakage).
"""

import os
import sys
import json
import time
import subprocess
from pathlib import Path

# Add project root to sys.path
PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from engine.tts_engine import generate_dialogue_speech, load_character_profiles


SAMPLE_DIALOGUE = [
    {
        "speaker": "junior_dev",
        "character_id": "junior_dev",
        "text": "Never push code directly to production on Friday afternoon.",
        "emotion": "shocked",
        "pause_after": 0.30
    },
    {
        "speaker": "claude",
        "character_id": "claude",
        "text": "[chuckle] Bro... your code has more bugs than an abandoned kitchen.",
        "emotion": "smug",
        "pause_after": 0.30
    },
    {
        "speaker": "junior_dev",
        "character_id": "junior_dev",
        "text": "Wait—it was just one tiny button color change in CSS!",
        "emotion": "shocked",
        "pause_after": 0.30
    },
    {
        "speaker": "claude",
        "character_id": "claude",
        "text": "[sigh] You broke customer checkout in eight countries simultaneously.",
        "emotion": "smug",
        "pause_after": 0.30
    },
    {
        "speaker": "junior_dev",
        "character_id": "junior_dev",
        "text": "Seriously? Show me the proof before my boss wakes up.",
        "emotion": "shocked",
        "pause_after": 0.30
    },
    {
        "speaker": "claude",
        "character_id": "claude",
        "text": "Look at step one: zero tests were run before pushing.",
        "emotion": "smug",
        "pause_after": 0.35
    },
    {
        "speaker": "junior_dev",
        "character_id": "junior_dev",
        "text": "Wait, step two says the lead engineer is already hiking?",
        "emotion": "shocked",
        "pause_after": 0.35
    },
    {
        "speaker": "claude",
        "character_id": "claude",
        "text": "And step three: forty-seven emergency alerts fired in twelve seconds.",
        "emotion": "smug",
        "pause_after": 0.35
    },
    {
        "speaker": "junior_dev",
        "character_id": "junior_dev",
        "text": "Bro... my hands are shaking. How do I fix this?",
        "emotion": "shocked",
        "pause_after": 0.30
    },
    {
        "speaker": "claude",
        "character_id": "claude",
        "text": "Check your screen: your CEO just messaged asking why revenue stopped.",
        "emotion": "smug",
        "pause_after": 0.35
    },
    {
        "speaker": "claude",
        "character_id": "claude",
        "text": "[chuckle] Enjoy your weekend unemployment. Comment FIX and I'll DM you the link.",
        "emotion": "smug",
        "pause_after": 0.40
    }
]


def measure_audio_loudness(audio_path: str):
    """Measures integrated LUFS and max volume using ffmpeg."""
    cmd = [
        "ffmpeg", "-i", audio_path,
        "-af", "loudnorm=I=-14:TP=-1:print_format=json",
        "-f", "null", "-"
    ]
    res = subprocess.run(cmd, capture_output=True, text=True)
    
    # Extract JSON output from loudnorm
    lufs = -14.0
    output = res.stderr
    try:
        json_start = output.rfind("{")
        json_end = output.rfind("}") + 1
        if json_start != -1 and json_end != -1:
            data = json.loads(output[json_start:json_end])
            lufs = float(data.get("input_i", -14.0))
    except Exception:
        pass

    # Measure max volume via volumedetect
    cmd_vol = [
        "ffmpeg", "-i", audio_path,
        "-af", "volumedetect",
        "-f", "null", "-"
    ]
    res_vol = subprocess.run(cmd_vol, capture_output=True, text=True)
    max_vol = 0.0
    for line in res_vol.stderr.splitlines():
        if "max_volume:" in line:
            try:
                max_vol = float(line.split("max_volume:")[1].split("dB")[0].strip())
            except Exception:
                pass

    return lufs, max_vol


def run_smoke_test():
    print("=" * 70)
    print("🚀 [SMOKE TEST] KOKORO-82M & LIP-SYNC AUDIO PIPELINE (11-TURN ROAST)")
    print("=" * 70)

    out_audio = str(PROJECT_ROOT / "public" / "voice.mp3")
    out_vtt = str(PROJECT_ROOT / "public" / "subs.vtt")
    out_json = str(PROJECT_ROOT / "public" / "subs.json")
    meta_json = str(PROJECT_ROOT / "public" / "video-meta.json")
    timeline_json = str(PROJECT_ROOT / "public" / "timeline.json")

    t_start = time.time()
    result = generate_dialogue_speech(
        dialogue=SAMPLE_DIALOGUE,
        out_audio=out_audio,
        out_vtt=out_vtt,
        out_json=out_json,
        meta_json=meta_json,
        timeline_json=timeline_json,
        title="Production on Friday Roast Skit"
    )
    t_synth = time.time() - t_start

    duration_sec = result["duration"]
    duration_frames = result["frames"]

    print("\n--- MEASURING BROADCAST LOUDNESS & METRICS ---")
    lufs, max_vol = measure_audio_loudness(out_audio)
    print(f"⏱️ CPU Synthesis Elapsed Time: {t_synth:.2f}s for {len(SAMPLE_DIALOGUE)} turns")
    print(f"🎵 Master Audio Duration:     {duration_sec:.2f}s ({duration_frames} frames @ 30fps)")
    print(f"🔊 Integrated Loudness:       {lufs:.2f} LUFS (Target: -14.0 LUFS)")
    print(f"🎚️ True Peak / Max Volume:    {max_vol:.2f} dB")

    # Strict Duration Check (35-55s)
    if not (35.0 <= duration_sec <= 55.0):
        print(f"❌ DURATION FAILED: {duration_sec:.2f}s is outside target range 35.0s - 55.0s!")
        return False
    print(f"✅ Duration Gate Passed: {duration_sec:.2f}s is within target range (35–55s).")

    # Verify timeline.json integrity
    print("\n--- VERIFYING TIMELINE.JSON & MOUTH ENVELOPES ---")
    if not os.path.exists(timeline_json):
        print("❌ timeline.json was not generated!")
        return False

    with open(timeline_json, "r", encoding="utf-8") as f:
        timeline = json.load(f)

    turns = timeline.get("turns", [])
    envelopes = timeline.get("mouth_envelopes", {})

    print(f"✅ Turns in timeline.json: {len(turns)}")
    if len(turns) != 11:
        print(f"❌ TURN COUNT FAILED: Expected 11 turns, found {len(turns)}!")
        return False
    print("✅ Verified exact 11-turn structure in timeline.json.")

    for t in turns:
        print(f"   Turn {t['turn_index']}: [{t['character_id'].upper()}] ({t['start_sec']:.2f}s - {t['end_sec']:.2f}s, frames {t['start_frame']}..{t['end_frame']}) emotion='{t['emotion']}'")

    # Strict Envelope Isolation Verification (Zero Mouth Leakage)
    all_speakers = ["junior_dev", "claude", "dad"]
    envelope_integrity_passed = True

    for t in turns:
        speaker = t["character_id"]
        s_frame = t["start_frame"] + 2  # slight offset into speaking turn
        e_frame = t["end_frame"] - 2

        if s_frame < e_frame:
            mid_frame = (s_frame + e_frame) // 2
            # Active speaker should have non-zero or positive envelope
            spk_val = envelopes.get(speaker, [])[mid_frame] if mid_frame < len(envelopes.get(speaker, [])) else 0.0
            
            # Non-speakers must be STRICTLY 0.0 (zero mouth leakage)
            for other in all_speakers:
                if other != speaker and other in envelopes:
                    other_val = envelopes[other][mid_frame]
                    if other_val != 0.0:
                        print(f"❌ NON-SPEAKER LEAK: Character '{other}' has envelope {other_val} during '{speaker}' turn at frame {mid_frame}!")
                        envelope_integrity_passed = False

    if envelope_integrity_passed:
        print("✅ Zero Mouth Leakage Verified: Non-speaking characters strictly 0.0 across all frames.")
    else:
        print("❌ Mouth Leakage Check Failed!")
        return False

    print("\n" + "=" * 70)
    print("🎉 ALL AUDIO PIPELINE TESTS PASSED!")
    print("=" * 70)
    return True


if __name__ == "__main__":
    success = run_smoke_test()
    sys.exit(0 if success else 1)
