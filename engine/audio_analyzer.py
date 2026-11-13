import os
import subprocess
import wave
import struct
import math
import json
from typing import List, Dict, Any


def extract_frame_audio_envelope(
    audio_path: str,
    fps: int = 30,
    out_json: str = "public/audio_envelope.json",
    smooth_factor: float = 0.35
) -> List[float]:
    """
    Extracts frame-by-frame normalized volume amplitude (0.0 to 1.0) for every video frame (at fps).
    Applies an exponential moving average attack/decay filter to produce organic, natural mouth lip-sync motion.
    """
    if not os.path.exists(audio_path):
        # Fallback dummy envelope
        dummy = [0.0] * 300
        os.makedirs(os.path.dirname(os.path.abspath(out_json)), exist_ok=True)
        with open(out_json, "w") as f:
            json.dump({"envelope": dummy, "fps": fps}, f)
        return dummy

    wav_path = os.path.splitext(audio_path)[0] + "_temp.wav"
    try:
        # Convert to 16-bit mono 44.1kHz PCM wav
        subprocess.run(
            [
                "ffmpeg", "-y", "-i", audio_path,
                "-ac", "1", "-ar", "44100",
                "-f", "wav", wav_path
            ],
            capture_output=True,
            check=True
        )

        with wave.open(wav_path, "r") as wf:
            n_frames = wf.getnframes()
            sample_rate = wf.getframerate()
            raw_bytes = wf.readframes(n_frames)
            samples = struct.unpack(f"{n_frames}h", raw_bytes)

        samples_per_video_frame = int(sample_rate / fps)
        total_video_frames = max(1, int(n_frames / samples_per_video_frame))
        raw_envelope = []

        # Peak reference for normalization
        max_seen_rms = 1000.0

        for i in range(total_video_frames):
            start_idx = i * samples_per_video_frame
            end_idx = min(start_idx + samples_per_video_frame, len(samples))
            chunk = samples[start_idx:end_idx]
            if not chunk:
                raw_envelope.append(0.0)
                continue

            sum_sq = sum(s * s for s in chunk)
            rms = math.sqrt(sum_sq / len(chunk))
            if rms > max_seen_rms:
                max_seen_rms = rms
            raw_envelope.append(rms)

        # Normalize and apply organic smoothing filter
        smooth_envelope = []
        prev_val = 0.0
        peak_rms = max(max_seen_rms, 6000.0)

        for rms in raw_envelope:
            # Non-linear perceptual scaling (power 0.8 to accentuate speech syllables)
            norm = min(1.0, math.pow(rms / peak_rms, 0.85)) if peak_rms > 0 else 0.0
            # Attack is fast, decay is smooth
            if norm > prev_val:
                current_val = prev_val + (norm - prev_val) * 0.70  # fast attack
            else:
                current_val = prev_val + (norm - prev_val) * (1.0 - smooth_factor)  # smooth decay
            
            smooth_envelope.append(round(current_val, 4))
            prev_val = current_val

        # Pad with 0.0 for safety
        while len(smooth_envelope) < total_video_frames:
            smooth_envelope.append(0.0)

        payload = {
            "fps": fps,
            "total_frames": len(smooth_envelope),
            "envelope": smooth_envelope
        }

        os.makedirs(os.path.dirname(os.path.abspath(out_json)), exist_ok=True)
        with open(out_json, "w") as f:
            json.dump(payload, f, indent=2)

        return smooth_envelope

    finally:
        if os.path.exists(wav_path):
            try:
                os.remove(wav_path)
            except OSError:
                pass


if __name__ == "__main__":
    import sys
    audio = sys.argv[1] if len(sys.argv) > 1 else "public/voice.mp3"
    out = sys.argv[2] if len(sys.argv) > 2 else "public/audio_envelope.json"
    env = extract_frame_audio_envelope(audio, fps=30, out_json=out)
    print(f"Generated {len(env)} frame envelopes into {out}")
