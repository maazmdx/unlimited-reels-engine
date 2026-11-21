"""
Antigravity Unlimited Video Engine - Neural Voice & Lip-Sync Timeline Generator
Features:
- Primary Engine (GPU): Chatterbox-Turbo / Chatterbox-TTS on CUDA GPU with per-turn emotion exaggeration
- Primary Engine (CPU): Kokoro-82M (kokoro-onnx) high-energy neural voice synthesis (speed 1.06 - 1.16)
- Fallback & Per-Character Engine: Edge-TTS (with strict pitch="+0Hz", no metallic artifacts)
- Auto model caching in .cache/kokoro/ (kokoro-v1.0.onnx + voices-v1.0.bin)
- Leading/trailing silence trimming (dead air <= 0.05s) via FFmpeg silenceremove
- Snappy comedic turn pauses (0.10s - 0.18s, punchline max 0.24s)
- Clean broadcast DSP mastering (highpass=75, warmth EQ, transparent compressor, -14.0 LUFS loudnorm)
- Subtle lo-fi ambient music bed ducked at -22 dB
- Multi-character 30fps lip-sync envelopes exported to timeline.json & subs.json
"""

import os
import sys
import json
import math
import asyncio
import re
import subprocess
import shutil
import tempfile
from pathlib import Path
from typing import List, Dict, Any, Optional, Tuple

import numpy as np
import soundfile as sf

# Optional edge_tts and gtts imports
try:
    import edge_tts
except ImportError:
    edge_tts = None

try:
    from gtts import gTTS
except ImportError:
    gTTS = None

try:
    from mutagen.mp3 import MP3
except ImportError:
    MP3 = None

PROJECT_ROOT = Path(__file__).resolve().parent.parent
CONFIG_PATH = PROJECT_ROOT / "engine" / "config" / "characters.json"
CACHE_DIR = PROJECT_ROOT / ".cache" / "kokoro"

# Kokoro model download endpoints
KOKORO_MODEL_URL = "https://github.com/thewh1teagle/kokoro-onnx/releases/download/model-files-v1.0/kokoro-v1.0.onnx"
KOKORO_VOICES_URL = "https://github.com/thewh1teagle/kokoro-onnx/releases/download/model-files-v1.0/voices-v1.0.bin"

# Global Singletons
_KOKORO_INSTANCE = None
_CHATTERBOX_INSTANCE = None
VOICE_REFS_DIR = PROJECT_ROOT / ".cache" / "voice_refs"

# Emotion to Chatterbox Exaggeration & CFG Weight mapping
# 0.45 tired/sad, 0.65 deadpan/smug, 0.85 shocked/roast, 0.95 angry/screaming
EMOTION_EXAGGERATION_MAP: Dict[str, Dict[str, float]] = {
    "neutral": {"exaggeration": 0.65, "cfg_weight": 0.50},
    "tired": {"exaggeration": 0.45, "cfg_weight": 0.55},
    "sad": {"exaggeration": 0.45, "cfg_weight": 0.55},
    "deadpan": {"exaggeration": 0.65, "cfg_weight": 0.50},
    "smug": {"exaggeration": 0.65, "cfg_weight": 0.50},
    "sarcastic": {"exaggeration": 0.75, "cfg_weight": 0.45},
    "roast": {"exaggeration": 0.85, "cfg_weight": 0.40},
    "shocked": {"exaggeration": 0.85, "cfg_weight": 0.40},
    "excited": {"exaggeration": 0.85, "cfg_weight": 0.40},
    "angry": {"exaggeration": 0.95, "cfg_weight": 0.35},
    "screaming": {"exaggeration": 0.95, "cfg_weight": 0.35},
}

CHARACTER_VOICE_REF_SPECS = {
    "junior_dev": {
        "engine": "kokoro",
        "voice": "am_michael",
        "text": "Hello there. I am ready to test this project on my computer today without any delay.",
    },
    "claude": {
        "engine": "kokoro",
        "voice": "bm_george",
        "text": "Greetings. Let us examine the technical architecture and the verified facts objectively.",
    },
    "gemini": {
        "engine": "kokoro",
        "voice": "af_heart",
        "text": "Welcome. Here is the verified technical breakdown and what you need to know.",
    },
    "grok": {
        "engine": "kokoro",
        "voice": "am_fenrir",
        "text": "Look at the numbers. The data shows this runs faster and smoother than you think.",
    },
    "dad": {
        "engine": "edge_tts",
        "voice": "en-IN-PrabhatNeural",
        "text": "Listen to me, check this carefully and do not waste any more money on useless things.",
    },
}


def ensure_voice_reference(character_id: str) -> Optional[str]:
    """
    Returns path to cached 5-second clean neutral 24000Hz mono reference WAV for the character.
    Generates and caches in .cache/voice_refs/<character_id>.wav if not already present.
    """
    VOICE_REFS_DIR.mkdir(parents=True, exist_ok=True)
    ref_path = VOICE_REFS_DIR / f"{character_id}.wav"
    if ref_path.exists() and ref_path.stat().st_size > 10000:
        return str(ref_path)

    spec = CHARACTER_VOICE_REF_SPECS.get(character_id, CHARACTER_VOICE_REF_SPECS["junior_dev"])
    print(f"🎙️ [VoiceRef] Generating 5s reference audio for {character_id} ({spec['voice']})...")
    try:
        if spec["engine"] == "kokoro":
            _synthesize_kokoro(
                text=spec["text"],
                voice_id=spec["voice"],
                speed=1.0,
                out_audio=str(ref_path)
            )
        else:
            asyncio.run(_synthesize_edge_tts(
                text=spec["text"],
                voice_name=spec["voice"],
                rate="+0%",
                out_audio=str(ref_path)
            ))
        if ref_path.exists() and ref_path.stat().st_size > 5000:
            # Ensure strictly clean 24000Hz mono PCM_16 WAV
            clean_wav = str(ref_path) + ".clean.wav"
            cmd = ["ffmpeg", "-y", "-i", str(ref_path), "-ar", "24000", "-ac", "1", "-c:a", "pcm_s16le", clean_wav]
            subprocess.run(cmd, capture_output=True, check=True)
            if os.path.exists(clean_wav) and os.path.getsize(clean_wav) > 1000:
                shutil.move(clean_wav, str(ref_path))
            print(f"✅ [VoiceRef] Cached clean 24000Hz mono reference audio: {ref_path}")
            return str(ref_path)
    except Exception as e:
        print(f"⚠️ [VoiceRef] Generation notice for {character_id}: {e}")

    return None


def is_cuda_available() -> bool:
    """Detects whether CUDA GPU is available for accelerated neural voice synthesis."""
    try:
        import torch
        return bool(torch.cuda.is_available())
    except Exception:
        return False


def get_chatterbox():
    """Returns initialized ChatterboxTTS singleton on CUDA GPU with dynamic class inspection."""
    global _CHATTERBOX_INSTANCE
    if _CHATTERBOX_INSTANCE is not None:
        return _CHATTERBOX_INSTANCE

    if not is_cuda_available():
        return None

    import traceback
    try:
        # Dynamically inspect chatterbox / chatterbox.tts
        TargetClass = None
        for mod_name in ["chatterbox.tts", "chatterbox"]:
            try:
                mod = sys.modules.get(mod_name) or __import__(mod_name, fromlist=["*"])
                for attr in ["ChatterboxTTS", "ChatterboxTurboTTS", "Chatterbox"]:
                    if hasattr(mod, attr):
                        TargetClass = getattr(mod, attr)
                        break
            except Exception:
                pass
            if TargetClass:
                break

        if TargetClass:
            print(f"🚀 [Chatterbox GPU] Loading {TargetClass.__name__}.from_pretrained(device='cuda')...")
            if hasattr(TargetClass, "from_pretrained"):
                _CHATTERBOX_INSTANCE = TargetClass.from_pretrained(device="cuda")
            else:
                _CHATTERBOX_INSTANCE = TargetClass()
            print(f"✅ [Chatterbox GPU] Engine loaded successfully: {TargetClass.__name__}")
            return _CHATTERBOX_INSTANCE
        else:
            try:
                import chatterbox
                print(f"⚠️ [Chatterbox GPU] No recognizable TTS class in chatterbox! dir(chatterbox)={dir(chatterbox)}")
            except Exception as e:
                print(f"⚠️ [Chatterbox GPU] chatterbox import error: {e}")
    except Exception as e:
        print(f"❌ [Chatterbox GPU] Critical loading traceback:\n{traceback.format_exc()}")

    return None


def ensure_kokoro_model(cache_dir: Optional[Path] = None) -> Tuple[Path, Path]:
    """
    Ensures that kokoro-v1.0.onnx and voices-v1.0.bin are cached and ready.
    Downloads them automatically if missing or incomplete.
    """
    target_dir = Path(cache_dir) if cache_dir else CACHE_DIR
    target_dir.mkdir(parents=True, exist_ok=True)

    onnx_file = target_dir / "kokoro-v1.0.onnx"
    voices_file = target_dir / "voices-v1.0.bin"

    # Also check user home cache as a secondary search path
    user_cache = Path.home() / ".cache" / "kokoro"
    if not (onnx_file.exists() and onnx_file.stat().st_size > 50_000_000):
        if (user_cache / "kokoro-v1.0.onnx").exists() and (user_cache / "kokoro-v1.0.onnx").stat().st_size > 50_000_000:
            onnx_file = user_cache / "kokoro-v1.0.onnx"

    if not (voices_file.exists() and voices_file.stat().st_size > 5_000_000):
        if (user_cache / "voices-v1.0.bin").exists() and (user_cache / "voices-v1.0.bin").stat().st_size > 5_000_000:
            voices_file = user_cache / "voices-v1.0.bin"

    import urllib.request

    if not (voices_file.exists() and voices_file.stat().st_size > 5_000_000):
        print(f"📥 [Kokoro] Downloading voices-v1.0.bin to {voices_file}...")
        urllib.request.urlretrieve(KOKORO_VOICES_URL, str(voices_file))

    if not (onnx_file.exists() and onnx_file.stat().st_size > 50_000_000):
        print(f"📥 [Kokoro] Downloading kokoro-v1.0.onnx to {onnx_file}...")
        urllib.request.urlretrieve(KOKORO_MODEL_URL, str(onnx_file))

    return onnx_file, voices_file


def get_kokoro():
    """Returns initialized Kokoro ONNX singleton."""
    global _KOKORO_INSTANCE
    if _KOKORO_INSTANCE is not None:
        return _KOKORO_INSTANCE

    try:
        from kokoro_onnx import Kokoro
        onnx_path, voices_path = ensure_kokoro_model()
        print(f"🧠 [Kokoro-82M] Loading ONNX runtime from {onnx_path.name} & {voices_path.name}...")
        _KOKORO_INSTANCE = Kokoro(str(onnx_path), str(voices_path))
        print("✅ [Kokoro-82M] Engine initialized on CPU.")
        return _KOKORO_INSTANCE
    except Exception as e:
        print(f"⚠️ [Kokoro-82M] Initialization notice: {e}")
        return None


def load_character_profiles() -> Dict[str, Any]:
    """Loads characters.json as single source of truth for voices and parameters."""
    if CONFIG_PATH.exists():
        with open(CONFIG_PATH, "r", encoding="utf-8") as f:
            return json.load(f)
    return {}


def canonicalize_character_id(speaker_str: str) -> str:
    """Normalizes any speaker label or alias to its canonical characters.json ID."""
    s = (speaker_str or "").lower().strip()
    if s in ["junior", "dev", "junior_dev", "human_male", "junior developer"]:
        return "junior_dev"
    if s in ["dad", "father", "indian_dad", "boomer_dad", "parent"]:
        return "dad"
    if s in ["claude", "claude_ai", "anthropic"]:
        return "claude"
    if s in ["gemini", "gemini_ai", "google_gemini"]:
        return "gemini"
    if s in ["grok", "grok_ai", "xai"]:
        return "grok"
    if s in ["bot", "antigravity", "antigravity_bot", "ai"]:
        return "antigravity_bot"
    return s if s in load_character_profiles() else "junior_dev"


def detect_language(text: str) -> str:
    """Detects primary language script: 'kn' (Kannada), 'hi' (Hindi), or 'en' (English)."""
    if re.search(r'[\u0C80-\u0CFF]', text):
        return "kn"
    if re.search(r'[\u0900-\u097F]', text):
        return "hi"
    return "en"


def convert_years_to_words(text: str) -> str:
    """Converts 4-digit years (e.g. 1993, 2026, 2008) into spoken words."""
    def _rep(m):
        y = int(m.group(0))
        ones = ["", "one", "two", "three", "four", "five", "six", "seven", "eight", "nine", "ten", "eleven", "twelve", "thirteen", "fourteen", "fifteen", "sixteen", "seventeen", "eighteen", "nineteen"]
        tens = ["", "", "twenty", "thirty", "forty", "fifty", "sixty", "seventy", "eighty", "ninety"]
        if 2000 <= y <= 2009:
            return f"two thousand {ones[y - 2000]}".strip()
        c1, c2 = y // 100, y % 100
        w1 = f"{tens[c1 // 10]} {ones[c1 % 10]}".strip() if c1 >= 20 else ones[c1]
        if c2 == 0:
            w2 = "hundred"
        elif c2 < 20:
            w2 = ones[c2]
        else:
            w2 = f"{tens[c2 // 10]} {ones[c2 % 10]}".strip()
        return f"{w1} {w2}".strip()

    return re.sub(r'\b(19\d{2}|20\d{2})\b', _rep, text)


def clean_text_for_speech(text: str, is_chatterbox: bool = False) -> str:
    """
    Cleans text of Markdown formatting, asterisks, brackets for clean TTS synthesis.
    - Replaces em-dash / en-dash (— / –) with a natural pause comma (, ).
    - Converts 4-digit years (1993 -> nineteen ninety-three) in TTS text only.
    - Strips ALL bracketed cues ([chuckle], [sigh], [laugh], [gasp], [groan], etc.)
      BEFORE passing text to Chatterbox, Kokoro, or Edge-TTS so it NEVER speaks
      the word "chuckle" or "sigh" aloud!
    """
    # Replace em-dash and en-dash with comma pause
    text = text.replace("—", ", ").replace("–", ", ")

    # Convert 4-digit years into spoken words
    text = convert_years_to_words(text)

    # Strip ALL bracketed cues ([chuckle], [sigh], [laugh], [gasp], [groan], [snicker], etc.)
    text = re.sub(r'\[(?:chuckle|sigh|gasp|giggle|laughter|laugh|groan|snicker|cough|pause)\]', '', text, flags=re.IGNORECASE)
    # Strip any remaining bracketed tokens [anything]
    text = re.sub(r'\[.*?\]', '', text)
    # Strip markdown and bracket characters
    text = re.sub(r'[*#_~`>\[\]\(\)]', ' ', text)

    # Clean up excess punctuation and leading ellipses
    text = re.sub(r'^\s*\.{2,}\s*', '', text)
    text = re.sub(r'\s+,', ',', text)
    text = re.sub(r'\s+', ' ', text).strip()
    return text


def format_vtt_timestamp(seconds: float) -> str:
    """Converts seconds float into WebVTT timestamp: 00:00:00.000"""
    hrs = int(seconds // 3600)
    mins = int((seconds % 3600) // 60)
    secs = int(seconds % 60)
    millis = int(round((seconds - int(seconds)) * 1000))
    if millis >= 1000:
        millis = 999
    return f"{hrs:02d}:{mins:02d}:{secs:02d}.{millis:03d}"


def format_srt_timestamp(seconds: float) -> str:
    """Converts seconds float into standard SubRip (.srt) timestamp: 00:00:00,000"""
    hrs = int(seconds // 3600)
    mins = int((seconds % 3600) // 60)
    secs = int(seconds % 60)
    millis = int(round((seconds - int(seconds)) * 1000))
    if millis >= 1000:
        millis = 999
    return f"{hrs:02d}:{mins:02d}:{secs:02d},{millis:03d}"


def clean_srt_text(text: str) -> str:
    """Strips emojis and formatting glitches for clean, professional subtitles (2-5 words)."""
    cleaned = re.sub(r'[\U00010000-\U0010ffff]', '', text)
    cleaned = re.sub(r'[^\x00-\x7F]+', ' ', cleaned)
    cleaned = re.sub(r'\s+', ' ', cleaned).strip()
    return cleaned


def generate_srt_content(chunks: List[Dict[str, Any]]) -> str:
    """Generates standard RFC/SubRip formatted .srt string from chunk timestamps."""
    srt_blocks = []
    idx = 1
    for chunk in chunks:
        start_ts = format_srt_timestamp(chunk.get("start", 0.0))
        end_ts = format_srt_timestamp(chunk.get("end", 0.0))
        clean_text = clean_srt_text(chunk.get("text", ""))
        if not clean_text:
            continue
        srt_blocks.append(f"{idx}\n{start_ts} --> {end_ts}\n{clean_text}\n")
        idx += 1
    return "\n".join(srt_blocks)


def export_srt_file(source: Any, dest_srt_path: Any) -> str:
    """
    Exports clean .srt captions file directly from timeline dict, subs.json, or chunk list.
    """
    dest = Path(dest_srt_path)
    dest.parent.mkdir(parents=True, exist_ok=True)
    chunks = []
    if isinstance(source, list):
        chunks = source
    elif isinstance(source, (str, Path)):
        p = Path(source)
        if p.exists():
            try:
                with open(p, "r", encoding="utf-8") as f:
                    data = json.load(f)
                chunks = data.get("chunks") or data.get("all_chunks") or []
                if not chunks and "turns" in data:
                    for t in data["turns"]:
                        chunks.append({
                            "start": t.get("start_sec", 0.0),
                            "end": t.get("end_sec", 0.0),
                            "text": t.get("text", "")
                        })
            except Exception as e:
                print(f"⚠️ Failed reading subtitle source {p}: {e}")
    elif isinstance(source, dict):
        chunks = source.get("chunks") or source.get("all_chunks") or []
        if not chunks and "turns" in source:
            for t in source["turns"]:
                chunks.append({
                    "start": t.get("start_sec", 0.0),
                    "end": t.get("end_sec", 0.0),
                    "text": t.get("text", "")
                })

    srt_text = generate_srt_content(chunks)
    with open(dest, "w", encoding="utf-8") as f:
        f.write(srt_text)
    return str(dest)


def get_audio_duration(file_path: str) -> float:
    """Calculates audio duration in seconds using ffprobe or soundfile."""
    try:
        info = sf.info(file_path)
        return float(info.duration)
    except Exception:
        pass

    try:
        res = subprocess.run(
            [
                "ffprobe", "-v", "error", "-show_entries",
                "format=duration", "-of", "default=noprint_wrappers=1:nokey=1",
                file_path
            ],
            capture_output=True,
            text=True,
            check=True
        )
        return float(res.stdout.strip())
    except Exception:
        return 10.0


def trim_silence(input_audio: str, output_audio: str) -> bool:
    """
    Trims leading and trailing silence via FFmpeg silenceremove
    so no line has dead air > 0.05s.
    """
    filter_str = "silenceremove=start_periods=1:start_duration=0.02:start_threshold=-42dB:stop_periods=-1:stop_duration=0.04:stop_threshold=-42dB"
    cmd = [
        "ffmpeg", "-y",
        "-i", input_audio,
        "-af", filter_str,
        output_audio
    ]
    try:
        subprocess.run(cmd, capture_output=True, check=True)
        return True
    except Exception as e:
        if os.path.realpath(str(input_audio)) != os.path.realpath(str(output_audio)):
            shutil.copy2(input_audio, output_audio)
        return False


async def _synthesize_edge_tts(
    text: str,
    voice: str,
    rate: str = "+0%",
    out_audio: str = "temp.mp3",
    pitch: str = "+0Hz"
) -> List[Dict[str, Any]]:
    """
    Synthesizes voice using Edge-TTS with pitch strictly at '+0Hz' (no metallic pitch shift).
    """
    if edge_tts is None:
        raise RuntimeError("edge-tts package not installed.")

    # Enforce zero metallic pitch shifts
    clean_pitch = "+0Hz"

    last_err = None
    for attempt in range(1, 4):
        try:
            comm = edge_tts.Communicate(text, voice=voice, rate=rate, pitch=clean_pitch)
            sentences = []
            audio_data = bytearray()

            async def _collect_stream():
                async for chunk in comm.stream():
                    chunk_type = chunk.get("type")
                    if chunk_type == "audio":
                        audio_data.extend(chunk["data"])
                    elif chunk_type == "SentenceBoundary":
                        offset = chunk.get("offset", 0) / 10_000_000.0
                        duration = chunk.get("duration", 0) / 10_000_000.0
                        sentences.append({
                            "text": chunk.get("text", "").strip(),
                            "start": round(offset, 3),
                            "end": round(offset + duration, 3)
                        })

            await asyncio.wait_for(_collect_stream(), timeout=25.0)

            if len(audio_data) > 200:
                os.makedirs(os.path.dirname(os.path.abspath(out_audio)), exist_ok=True)
                with open(out_audio, "wb") as f:
                    f.write(audio_data)
                return sentences
        except Exception as e:
            last_err = e
            await asyncio.sleep(0.4 * attempt)

    raise RuntimeError(f"Edge-TTS failed after 3 attempts: {repr(last_err)}")


def _synthesize_kokoro(
    text: str,
    voice_id: str = "am_michael",
    speed: float = 1.0,
    out_audio: str = "temp.wav"
) -> Tuple[List[Dict[str, Any]], float]:
    """
    Synthesizes speech using Kokoro-82M ONNX on CPU.
    Returns (word_timings, duration).
    """
    kokoro = get_kokoro()
    if kokoro is None:
        raise RuntimeError("Kokoro ONNX engine unavailable.")

    # Determine language tag from voice prefix (b -> British, a -> American)
    lang_tag = "en-gb" if voice_id.startswith("b") else "en-us"

    samples, sample_rate = kokoro.create(
        text=text,
        voice=voice_id,
        speed=float(speed),
        lang=lang_tag,
        trim=True
    )

    os.makedirs(os.path.dirname(os.path.abspath(out_audio)), exist_ok=True)
    sf.write(out_audio, samples, sample_rate, subtype="PCM_16")

    # Trim leading/trailing dead air using FFmpeg
    trimmed_audio = out_audio + ".trim.wav"
    if trim_silence(out_audio, trimmed_audio):
        if os.path.exists(trimmed_audio) and os.path.getsize(trimmed_audio) > 1000:
            shutil.move(trimmed_audio, out_audio)

    duration = get_audio_duration(out_audio)

    # Build proportional word boundaries
    words = text.split()
    weights = [max(len(w), 2) for w in words]
    total_w = sum(weights) or 1.0
    current_t = 0.0
    word_timings = []

    for i, w in enumerate(words):
        dur = (weights[i] / total_w) * duration
        word_timings.append({
            "word": re.sub(r'[^\w]', '', w) or w,
            "raw": w,
            "start": round(current_t, 3),
            "end": round(current_t + dur, 3)
        })
        current_t += dur

    return word_timings, duration


def _synthesize_chatterbox(
    text: str,
    voice_id: str = "junior_dev",
    emotion: str = "neutral",
    out_audio: str = "temp.wav",
    audio_prompt_path: Optional[str] = None
) -> Tuple[List[Dict[str, Any]], float]:
    """
    Synthesizes speech using Chatterbox GPU TTS on CUDA with emotion-mapped exaggeration & cfg_weight.
    Supports audio_prompt_path reference voice cloning for consistent character identities.
    Returns (word_timings, duration).
    """
    model = get_chatterbox()
    if model is None:
        raise RuntimeError("Chatterbox GPU engine unavailable.")

    emo_cfg = EMOTION_EXAGGERATION_MAP.get(emotion.lower(), EMOTION_EXAGGERATION_MAP["neutral"])
    exaggeration = emo_cfg["exaggeration"]
    cfg_weight = emo_cfg["cfg_weight"]

    gen_kwargs: Dict[str, Any] = {
        "text": text,
        "exaggeration": exaggeration,
        "cfg_weight": cfg_weight,
    }
    if audio_prompt_path and os.path.exists(audio_prompt_path):
        gen_kwargs["audio_prompt_path"] = audio_prompt_path

    # Synthesize audio with model (ChatterboxTurboTTS / ChatterboxTTS)
    try:
        if hasattr(model, "generate"):
            audio_out = model.generate(**gen_kwargs)
        elif callable(model):
            audio_out = model(**gen_kwargs)
        else:
            raise RuntimeError("Chatterbox model has no recognized generate or callable interface")
    except TypeError:
        # Fallback if audio_prompt_path keyword has different name (e.g. ref_audio) or not accepted
        gen_kwargs.pop("audio_prompt_path", None)
        if audio_prompt_path and os.path.exists(audio_prompt_path):
            gen_kwargs["ref_audio"] = audio_prompt_path
        try:
            if hasattr(model, "generate"):
                audio_out = model.generate(**gen_kwargs)
            else:
                audio_out = model(**gen_kwargs)
        except TypeError:
            gen_kwargs.pop("ref_audio", None)
            if hasattr(model, "generate"):
                audio_out = model.generate(**gen_kwargs)
            else:
                audio_out = model(**gen_kwargs)

    os.makedirs(os.path.dirname(os.path.abspath(out_audio)), exist_ok=True)
    if isinstance(audio_out, tuple):
        samples, sr = audio_out
    elif hasattr(audio_out, "numpy"):
        samples = audio_out.cpu().numpy()
        sr = 24000
    elif isinstance(audio_out, np.ndarray):
        samples = audio_out
        sr = 24000
    else:
        samples = np.array(audio_out)
        sr = 24000

    samples = np.asarray(samples, dtype=np.float32).squeeze()
    sf.write(out_audio, samples, int(sr), format="WAV", subtype="PCM_16")

    # Trim leading/trailing dead air using FFmpeg
    trimmed_audio = out_audio + ".trim.wav"
    if trim_silence(out_audio, trimmed_audio):
        if os.path.exists(trimmed_audio) and os.path.getsize(trimmed_audio) > 1000:
            shutil.move(trimmed_audio, out_audio)

    duration = get_audio_duration(out_audio)

    # Build proportional word boundaries
    clean_words = [w for w in text.split() if not (w.startswith("[") and w.endswith("]"))]
    weights = [max(len(w), 2) for w in clean_words]
    total_w = sum(weights) or 1.0
    current_t = 0.0
    word_timings = []

    for i, w in enumerate(clean_words):
        dur = (weights[i] / total_w) * duration
        word_timings.append({
            "word": re.sub(r'[^\w]', '', w) or w,
            "raw": w,
            "start": round(current_t, 3),
            "end": round(current_t + dur, 3)
        })
        current_t += dur

    return word_timings, duration


def apply_broadcast_mastering(
    input_vocal_audio: str,
    output_audio: str,
    ambient_bed_path: Optional[str] = None,
    ambient_db: float = -22.0,
    sfx_track_path: Optional[str] = None,
    music_drop_sec: Optional[float] = None
) -> bool:
    """
    Applies clean broadcast mastering:
    - Highpass filter at 75 Hz (removes sub-rumble)
    - Gentle warmth & clarity EQ
    - Gentle compressor (ratio=3.0, threshold=-18dB)
    - Removed hollow 'aecho' and pitch shifts
    - Adds subtle warm lo-fi ambient piano bed ducked quietly at -22 dB
    - Automates 0.65s music drop right before roast punchline at music_drop_sec
    - Mixes procedural UI SFX (whoosh at Turn 5 + punchline thud + chime at CTA) at -10 dB
    - Final Loudnorm to exactly -14.0 LUFS (True Peak -1.0 dB, LRA 7)
    """
    from engine.ambient_music import generate_ambient_music_bed, DEFAULT_AMBIENT_PATH

    vocal_dur = get_audio_duration(input_vocal_audio)

    # Ensure ambient bed exists
    if not ambient_bed_path or not os.path.exists(ambient_bed_path):
        if DEFAULT_AMBIENT_PATH.exists():
            ambient_bed_path = str(DEFAULT_AMBIENT_PATH)
        else:
            ambient_bed_path = generate_ambient_music_bed(max(vocal_dur + 5.0, 30.0))

    has_sfx = bool(sfx_track_path and os.path.exists(sfx_track_path))

    # Comedic 0.65s music drop volume automation before savage punchline
    if music_drop_sec is not None and music_drop_sec >= 0:
        music_filter = (
            f"volume='if(between(t,{music_drop_sec:.3f},{music_drop_sec + 0.65:.3f}),0.0,1.0)':eval=frame,"
            f"volume={ambient_db}dB,aloop=loop=-1:size=2e+09"
        )
    else:
        music_filter = f"volume={ambient_db}dB,aloop=loop=-1:size=2e+09"

    vocal_dur = get_audio_duration(input_vocal_audio)
    fade_start = max(0.0, vocal_dur - 1.0)
    fade_filter = f",afade=t=out:st={fade_start:.2f}:d=1.0"

    if has_sfx:
        filter_chain = (
            "[0:a]highpass=f=75,"
            "equalizer=f=120:t=q:w=1.2:g=3.5,"
            "equalizer=f=900:t=q:w=2.0:g=-1.5,"
            "equalizer=f=4000:t=q:w=1.5:g=2.0,"
            "acompressor=threshold=-18dB:ratio=3.0:attack=15:release=85:makeup=2.0dB[vocal];"
            f"[1:a]{music_filter}[music];"
            "[2:a]volume=0dB[sfx];"
            "[vocal][music][sfx]amix=inputs=3:duration=first:dropout_transition=2,"
            f"loudnorm=I=-14.0:TP=-1.0:LRA=7{fade_filter}[out]"
        )
        cmd = [
            "ffmpeg", "-y",
            "-i", input_vocal_audio,
            "-i", ambient_bed_path,
            "-i", sfx_track_path,
            "-filter_complex", filter_chain,
            "-map", "[out]",
            "-c:a", "libmp3lame",
            "-b:a", "192k",
            output_audio
        ]
    else:
        filter_chain = (
            "[0:a]highpass=f=75,"
            "equalizer=f=120:t=q:w=1.2:g=3.5,"
            "equalizer=f=900:t=q:w=2.0:g=-1.5,"
            "equalizer=f=4000:t=q:w=1.5:g=2.0,"
            "acompressor=threshold=-18dB:ratio=3.0:attack=15:release=85:makeup=2.0dB[vocal];"
            f"[1:a]{music_filter}[music];"
            "[vocal][music]amix=inputs=2:duration=first:dropout_transition=2,"
            f"loudnorm=I=-14.0:TP=-1.0:LRA=7{fade_filter}[out]"
        )
        cmd = [
            "ffmpeg", "-y",
            "-i", input_vocal_audio,
            "-i", ambient_bed_path,
            "-filter_complex", filter_chain,
            "-map", "[out]",
            "-c:a", "libmp3lame",
            "-b:a", "192k",
            output_audio
        ]

    try:
        subprocess.run(cmd, capture_output=True, check=True)
        return True
    except Exception as e:
        print(f"⚠️ [DSP] FFmpeg mastering notice: {e}, falling back to single stream loudnorm...")
        simple_cmd = [
            "ffmpeg", "-y",
            "-i", input_vocal_audio,
            "-af", f"highpass=f=75,acompressor=threshold=-18dB:ratio=3.0,loudnorm=I=-14.0:TP=-1.0:LRA=7{fade_filter}",
            "-c:a", "libmp3lame",
            "-b:a", "192k",
            output_audio
        ]
        try:
            subprocess.run(simple_cmd, capture_output=True, check=True)
            return True
        except Exception:
            if os.path.realpath(str(input_vocal_audio)) != os.path.realpath(str(output_audio)):
                shutil.copy2(input_vocal_audio, output_audio)
            return False


def extract_character_mouth_envelopes(
    turns_data: List[Dict[str, Any]],
    total_frames: int,
    fps: int = 30
) -> Dict[str, List[float]]:
    """
    Computes real 30fps RMS audio mouth envelopes per character.
    Envelope is strictly 0.0 whenever that character is not speaking.
    """
    registry = load_character_profiles()
    all_chars = list(registry.keys())
    if "junior_dev" not in all_chars:
        all_chars.append("junior_dev")
    if "dad" not in all_chars:
        all_chars.append("dad")
    if "claude" not in all_chars:
        all_chars.append("claude")
    if "gemini" not in all_chars:
        all_chars.append("gemini")
    if "grok" not in all_chars:
        all_chars.append("grok")
    if "antigravity_bot" not in all_chars:
        all_chars.append("antigravity_bot")

    envelopes = {char_id: [0.0] * total_frames for char_id in all_chars}

    for turn in turns_data:
        char_id = turn["character_id"]
        audio_file = turn.get("audio_file")
        if not audio_file or not os.path.exists(audio_file):
            continue

        start_frame = turn["start_frame"]
        end_frame = turn["end_frame"]

        try:
            samples, sr = sf.read(audio_file)
            if len(samples.shape) > 1:
                samples = np.mean(samples, axis=1)

            turn_frames = max(end_frame - start_frame, 1)
            samples_per_frame = sr / fps

            for f_idx in range(turn_frames):
                target_frame = start_frame + f_idx
                if target_frame >= total_frames:
                    break

                s_start = int(f_idx * samples_per_frame)
                s_end = int((f_idx + 1) * samples_per_frame)
                slice_audio = samples[s_start:s_end]

                if len(slice_audio) > 0:
                    rms = float(np.sqrt(np.mean(slice_audio ** 2)))
                    # Normalize RMS smoothly between 0.0 and 1.0
                    val = min(1.0, max(0.0, (rms - 0.008) * 8.5))
                    val = round(float(val), 3)
                else:
                    val = 0.0

                if char_id in envelopes:
                    envelopes[char_id][target_frame] = val
        except Exception as e:
            print(f"⚠️ Mouth envelope extraction notice for {char_id}: {e}")

    return envelopes


def generate_dialogue_speech(
    dialogue: List[Dict[str, Any]],
    human_voice: Optional[str] = None,
    bot_voice: Optional[str] = None,
    rival_voice: Optional[str] = None,
    rate: str = "+0%",
    out_audio: str = "public/voice.mp3",
    out_vtt: str = "public/subs.vtt",
    out_json: str = "public/subs.json",
    meta_json: str = "public/video-meta.json",
    timeline_json: str = "public/timeline.json",
    title: str = "3D Low-Poly Dialogue Reel",
    pause_between_turns: float = 0.20,
) -> Dict[str, Any]:
    """
    Main Multi-Speaker Neural Voice & Lip-Sync Pipeline:
    - Uses Kokoro-82M neural voices per characters.json
    - Edge-TTS authentic Indian Dad & clean fallback
    - Strips dead air with silenceremove
    - Tight comedic pauses (0.15s - 0.28s)
    - Broadcast mastering at -14.0 LUFS + ambient lo-fi music bed ducked at -22 dB
    - Exports unified timeline.json with per-character 30fps mouth envelopes.
    """
    if not dialogue:
        raise ValueError("Dialogue list cannot be empty.")

    registry = load_character_profiles()
    first_text = dialogue[0]["text"]
    lang = detect_language(first_text)

    print(f"🎙️ Synthesizing Skit Audio ({len(dialogue)} turns) with Neural Kokoro & Edge-TTS...")

    turns_summary = []
    all_words = []
    all_chunks = []

    with tempfile.TemporaryDirectory() as tmpdir:
        turn_audio_files = []
        turn_raw_files = []
        current_timeline = 0.0

        for idx, turn in enumerate(dialogue):
            raw_speaker = turn.get("speaker") or turn.get("character_id") or "junior_dev"
            canonical_char = canonicalize_character_id(raw_speaker)
            char_config = registry.get(canonical_char, {})
            voice_prof = char_config.get("voice_profile", {})

            text = clean_text_for_speech(turn.get("text", ""))
            if not text:
                continue

            engine_type = voice_prof.get("engine", "kokoro").lower()
            voice_id = voice_prof.get("voice_id", "am_michael")
            speed = float(voice_prof.get("speed", 1.0))
            emotion = (turn.get("emotion") or "neutral").lower()

            turn_wav_raw = os.path.join(tmpdir, f"turn_{idx:03d}_raw.wav")
            turn_wav_trimmed = os.path.join(tmpdir, f"turn_{idx:03d}_trimmed.wav")
            word_timings = []
            turn_dur = 0.0

            synthesis_success = False

            # 1. Primary Engine (GPU): Chatterbox-Turbo / Chatterbox-TTS (if CUDA GPU is active)
            chatterbox_voice = voice_prof.get("chatterbox_voice") or canonical_char
            if is_cuda_available() and engine_type != "edge_tts":
                try:
                    ref_audio = ensure_voice_reference(canonical_char)
                    c_text = clean_text_for_speech(turn.get("text", ""), is_chatterbox=True)
                    word_timings, turn_dur = _synthesize_chatterbox(
                        text=c_text,
                        voice_id=chatterbox_voice,
                        emotion=emotion,
                        out_audio=turn_wav_raw,
                        audio_prompt_path=ref_audio
                    )
                    trim_silence(turn_wav_raw, turn_wav_trimmed)
                    turn_dur = get_audio_duration(turn_wav_trimmed)
                    synthesis_success = True
                    exag_val = EMOTION_EXAGGERATION_MAP.get(emotion.lower(), {}).get("exaggeration", 0.65)
                    print(f"🎭 [Chatterbox GPU exag={exag_val:.2f}] Turn {idx} ({canonical_char}) synthesized ({turn_dur:.2f}s).")
                except Exception as e_chatterbox:
                    import traceback
                    print(f"❌ [Chatterbox GPU Failure] Turn {idx} ({canonical_char}) exception:\n{traceback.format_exc()}\nFalling back to Kokoro ONNX...")
                    engine_type = "kokoro"

            # 2. Primary Engine (CPU Fallback): Kokoro-82M High-Energy ONNX
            if not synthesis_success and engine_type == "kokoro":
                try:
                    k_text = clean_text_for_speech(turn.get("text", ""), is_chatterbox=False)
                    word_timings, turn_dur = _synthesize_kokoro(
                        text=k_text,
                        voice_id=voice_id,
                        speed=speed,
                        out_audio=turn_wav_raw
                    )
                    trim_silence(turn_wav_raw, turn_wav_trimmed)
                    turn_dur = get_audio_duration(turn_wav_trimmed)
                    synthesis_success = True
                    print(f"⚠️ [Kokoro CPU fallback] Turn {idx} ({canonical_char}) synthesized ({turn_dur:.2f}s).")
                except Exception as e_kokoro:
                    print(f"⚠️ Kokoro fallback for turn {idx} ({canonical_char}): {e_kokoro}")
                    engine_type = "edge_tts"

            # 3. Fallback or Specific Engine: Edge-TTS
            if not synthesis_success:
                fallback_voice = voice_prof.get("fallback_edge_voice") or voice_prof.get("voice_id") or "en-US-AndrewNeural"
                edge_rate = voice_prof.get("rate") or "+0%"
                turn_mp3 = os.path.join(tmpdir, f"turn_{idx:03d}_edge.mp3")

                try:
                    sentences = asyncio.run(_synthesize_edge_tts(text, fallback_voice, rate=edge_rate, out_audio=turn_mp3, pitch="+0Hz"))
                    trim_silence(turn_mp3, turn_wav_trimmed)
                    turn_dur = get_audio_duration(turn_wav_trimmed)

                    # Build timings
                    words = text.split()
                    weights = [max(len(w), 2) for w in words]
                    total_w = sum(weights) or 1.0
                    cur_w_t = 0.0
                    for i, w in enumerate(words):
                        w_dur = (weights[i] / total_w) * turn_dur
                        word_timings.append({
                            "word": re.sub(r'[^\w]', '', w) or w,
                            "raw": w,
                            "start": round(cur_w_t, 3),
                            "end": round(cur_w_t + w_dur, 3)
                        })
                        cur_w_t += w_dur
                except Exception as e_edge:
                    print(f"⚠️ Edge-TTS error for turn {idx}: {e_edge}")
                    # gTTS absolute safety fallback
                    _synthesize_gtts(text, turn_wav_trimmed, lang=lang)
                    turn_dur = get_audio_duration(turn_wav_trimmed)

            turn_start = round(current_timeline, 3)
            turn_end = round(turn_start + turn_dur, 3)
            start_frame = int(round(turn_start * 30))
            end_frame = int(round(turn_end * 30))

            # Store turn audio file path for envelope analysis
            persistent_turn_audio = os.path.join(tmpdir, f"turn_{idx:03d}_final.wav")
            if os.path.realpath(str(turn_wav_trimmed)) != os.path.realpath(str(persistent_turn_audio)):
                shutil.copy2(turn_wav_trimmed, persistent_turn_audio)

            # Global word timestamps
            turn_words_obj = []
            for w in word_timings:
                w_start = round(turn_start + w["start"], 3)
                w_end = round(turn_start + w["end"], 3)
                w_data = {
                    "word": w["word"],
                    "start_sec": w_start,
                    "end_sec": w_end
                }
                turn_words_obj.append(w_data)
                all_words.append({
                    "word": w["word"],
                    "raw": w.get("raw", w["word"]),
                    "start": w_start,
                    "end": w_end,
                    "character_id": canonical_char
                })

            # Subtitle chunking (2-3 words per pill)
            for i in range(0, len(turn_words_obj), 3):
                chunk_slice = turn_words_obj[i:i+3]
                all_chunks.append({
                    "start": chunk_slice[0]["start_sec"],
                    "end": chunk_slice[-1]["end_sec"],
                    "text": " ".join([cw["word"] for cw in chunk_slice]),
                    "character_id": canonical_char,
                    "words": chunk_slice
                })

            turns_summary.append({
                "turn_index": idx,
                "character_id": canonical_char,
                "text": text,
                "emotion": emotion,
                "start_sec": turn_start,
                "end_sec": turn_end,
                "start_frame": start_frame,
                "end_frame": end_frame,
                "duration_sec": round(turn_dur, 3),
                "words": turn_words_obj,
                "audio_file": persistent_turn_audio
            })

            turn_audio_files.append(persistent_turn_audio)

            # Snappy conversational pausing (0.10s - 0.18s, punchline beat max 0.24s)
            if idx < len(dialogue) - 1:
                if emotion in ["smug", "deadpan"]:
                    turn_pause = 0.24  # Punchline beat after smug roast
                elif emotion in ["shocked", "excited"]:
                    turn_pause = 0.14  # Snappy disbelief reaction
                elif emotion in ["angry", "sarcastic"]:
                    turn_pause = 0.10  # Rapid, heated cut-in
                elif "?" in text:
                    turn_pause = 0.18  # Prompt question beat
                else:
                    turn_pause = 0.12  # Fast natural conversational flow

                pause_file = os.path.join(tmpdir, f"pause_{idx:03d}.wav")
                sf.write(pause_file, np.zeros(int(turn_pause * 24000), dtype=np.float32), 24000)
                turn_audio_files.append(pause_file)
                current_timeline = round(turn_end + turn_pause, 3)
            else:
                current_timeline = turn_end

        # Add +2.8s tail padding after the last spoken turn so the final word is NEVER cut off
        tail_padding_sec = 2.8
        tail_file = os.path.join(tmpdir, "tail_padding.wav")
        sf.write(tail_file, np.zeros(int(tail_padding_sec * 24000), dtype=np.float32), 24000)
        turn_audio_files.append(tail_file)
        current_timeline = round(current_timeline + tail_padding_sec, 3)

        # Concatenate audio files into vocal master
        concat_txt = os.path.join(tmpdir, "concat.txt")
        with open(concat_txt, "w", encoding="utf-8") as f:
            for p in turn_audio_files:
                f.write(f"file '{p}'\n")

        vocal_master_wav = os.path.join(tmpdir, "vocal_master.wav")
        subprocess.run(
            ["ffmpeg", "-y", "-f", "concat", "-safe", "0", "-i", concat_txt, "-c:a", "pcm_s16le", vocal_master_wav],
            capture_output=True,
            check=True
        )

        # Apply broadcast DSP mastering, procedural UI SFX & ducked ambient music bed
        print("🎛️ Mastering Dialogue with Broadcast DSP, UI SFX & Ambient Bed (-14.0 LUFS, -22 dB bed, -10 dB SFX)...")
        os.makedirs(os.path.dirname(os.path.abspath(out_audio)), exist_ok=True)

        vocal_dur = get_audio_duration(vocal_master_wav)
        # Procedural UI SFX & Comedic Punchline Audio:
        # 1. Whoosh/pop at Turn 5 start_sec (Act 3 proof card open)
        whoosh_sec = turns_summary[5]["start_sec"] if len(turns_summary) > 5 else (turns_summary[3]["start_sec"] if len(turns_summary) > 3 else None)
        # 2. Subtle iOS chime at Turn 9 start_sec (Act 4 notification toast pop-in)
        toast_sec = turns_summary[9]["start_sec"] if len(turns_summary) > 9 else None
        # 3. Punchline deep bass thud right as Turn 9 roast lands
        punchline_turn = turns_summary[9] if len(turns_summary) > 9 else (turns_summary[-2] if len(turns_summary) > 2 else None)
        punchline_sec = punchline_turn["start_sec"] if punchline_turn else None
        # 4. 0.65s music mute/drop 0.15s before the punchline
        music_drop_sec = max(0.0, punchline_sec - 0.15) if punchline_sec is not None else None
        # 5. iOS-style chime at total_duration - 2.5s (Act 5 clean black End-Card)
        chime_sec = max(0.0, vocal_dur - 2.5)

        from engine.ambient_music import generate_sfx_track, generate_sfx_whoosh, generate_sfx_chime, generate_sfx_bass_thud
        sfx_track_file = os.path.join(tmpdir, "sfx_track.wav")
        generate_sfx_track(
            total_duration_sec=vocal_dur + 1.0,
            whoosh_time_sec=whoosh_sec,
            toast_chime_sec=toast_sec,
            punchline_thud_sec=punchline_sec,
            chime_time_sec=chime_sec,
            out_path=Path(sfx_track_file),
            volume_db=-10.0
        )

        apply_broadcast_mastering(
            vocal_master_wav,
            out_audio,
            sfx_track_path=sfx_track_file,
            music_drop_sec=music_drop_sec
        )

        total_duration = get_audio_duration(out_audio)
        duration_in_frames = int(math.ceil((total_duration + 0.4) * 30))

        # Extract real 30fps RMS mouth envelopes per character
        mouth_envelopes = extract_character_mouth_envelopes(
            turns_data=turns_summary,
            total_frames=duration_in_frames,
            fps=30
        )

    # Clean internal temporary file references
    for t in turns_summary:
        t.pop("audio_file", None)

    # 1. Write timeline.json
    unified_timeline = {
        "total_duration_sec": round(total_duration, 3),
        "duration_in_frames": duration_in_frames,
        "fps": 30,
        "turns": turns_summary,
        "mouth_envelopes": mouth_envelopes
    }

    out_dirs = [
        os.path.dirname(os.path.abspath(timeline_json)),
        str(PROJECT_ROOT / "public"),
        str(PROJECT_ROOT / "my-edu-reels" / "public")
    ]
    for d in set(out_dirs):
        os.makedirs(d, exist_ok=True)
        with open(os.path.join(d, "timeline.json"), "w", encoding="utf-8") as f:
            json.dump(unified_timeline, f, indent=2, ensure_ascii=False)

    # 2. Write subs.json
    subs_data = {
        "words": all_words,
        "chunks": all_chunks,
        "turns": turns_summary
    }
    for d in set(out_dirs):
        with open(os.path.join(d, "subs.json"), "w", encoding="utf-8") as f:
            json.dump(subs_data, f, indent=2, ensure_ascii=False)

    # 3. Write WebVTT & SubRip (.srt)
    vtt_lines = ["WEBVTT\n"]
    for i, chunk in enumerate(all_chunks):
        start_ts = format_vtt_timestamp(chunk["start"])
        end_ts = format_vtt_timestamp(chunk["end"])
        vtt_lines.append(f"{i + 1}\n{start_ts} --> {end_ts}\n[{chunk['character_id'].upper()}] {chunk['text']}\n")

    srt_text = generate_srt_content(all_chunks)

    out_srt = str(PROJECT_ROOT / "public" / "subs.srt")
    for d in set(out_dirs):
        with open(os.path.join(d, "subs.vtt"), "w", encoding="utf-8") as f:
            f.write("\n".join(vtt_lines))
        with open(os.path.join(d, "subs.srt"), "w", encoding="utf-8") as f:
            f.write(srt_text)

    # 4. Copy audio and SFX files to both public folders (voice.mp3, voiceover.mp3, master.mp3, sfx_*.wav)
    for d in set(out_dirs):
        for audio_name in ["voice.mp3", "voiceover.mp3", "master.mp3"]:
            dest_audio = os.path.join(d, audio_name)
            if os.path.realpath(str(out_audio)) != os.path.realpath(str(dest_audio)):
                shutil.copy2(out_audio, dest_audio)
        for sfx_name in ["sfx_whoosh.wav", "sfx_chime.wav"]:
            src_sfx = PROJECT_ROOT / "assets" / "audio" / sfx_name
            if src_sfx.exists():
                shutil.copy2(str(src_sfx), os.path.join(d, sfx_name))

    # 5. Write video metadata
    meta = {
        "title": title,
        "language": lang,
        "type": "dialogue",
        "durationInSeconds": round(total_duration, 3),
        "durationInFrames": duration_in_frames,
        "fps": 30,
        "width": 1080,
        "height": 1920,
        "turnsCount": len(turns_summary),
        "wordCount": len(all_words),
        "chunksCount": len(all_chunks)
    }
    for d in set(out_dirs):
        with open(os.path.join(d, "video-meta.json"), "w", encoding="utf-8") as f:
            json.dump(meta, f, indent=2, ensure_ascii=False)

    print(f"✅ Dialogue complete: {out_audio} ({total_duration:.2f}s, {duration_in_frames} frames @ 30fps)")
    print(f"✅ Exported unified timeline.json with per-character 30fps lip-sync envelopes and subs.srt.")

    return {
        "audio_path": out_audio,
        "vtt_path": out_vtt,
        "srt_path": out_srt,
        "json_path": out_json,
        "timeline_path": timeline_json,
        "duration": total_duration,
        "frames": duration_in_frames,
        "turns": turns_summary,
        "chunks": all_chunks,
        "mouth_envelopes": mouth_envelopes
    }
