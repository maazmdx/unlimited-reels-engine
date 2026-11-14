"""
Antigravity Unlimited Video Engine - Multilingual Neural Voice & Subtitle Generator
100% Free Zero-Cost ($0) TTS Engine with Edge-TTS and gTTS Fallback.
Supported Languages: English, Hindi (हिंदी), Kannada (ಕನ್ನಡ), Indian English.
"""

import os
import sys
import json
import math
import asyncio
import re
from typing import List, Dict, Any, Optional

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


# Curated high-performing voices for Reels & Shorts across languages
PRESET_VOICES = {
    # English - Educational & Documentary
    "educational_male": "en-US-ChristopherNeural",   # Deep, authoritative, clear
    "educational_female": "en-US-JennyNeural",         # Crisp, informative, engaging
    "british_documentary": "en-GB-RyanNeural",         # Sophisticated BBC style
    # English - Dynamic, Anime & Funny
    "energetic_male": "en-US-AndrewMultilingualNeural", # High-tempo YouTube creator tone
    "punchy_female": "en-US-AvaNeural",                # Vibrant, upbeat, punchy
    "quirky_expressive": "en-US-GuyNeural",            # Natural conversation & reactions
    "deep_cinema": "en-US-EricNeural",                 # Dramatic & intense
    # Indian English
    "indian_english_male": "en-IN-PrabhatNeural",      # Natural Indian English male
    "indian_english_female": "en-IN-NeerjaExpressiveNeural", # Expressive Indian English female
    # Hindi (हिंदी)
    "hindi_male": "hi-IN-MadhurNeural",                # High-energy, engaging, perfect for viral/anime
    "hindi_female": "hi-IN-SwaraNeural",               # Warm, clear, documentary/storytelling
    # Curated dialogue voices
    "human_male": "en-US-AndrewNeural",         # Ultra-warm, natural podcast conversational tone
    "human_female": "en-US-JennyNeural",
    "bot_male": "en-US-BrianNeural",            # Deep, resonant, authoritative baritone AI
    "bot_female": "en-US-AriaNeural",
    "rival_male": "en-US-ChristopherNeural",    # Confident, sharp senior developer tone
    # Hindi dialogue
    "hindi_human": "hi-IN-MadhurNeural",
    "hindi_bot": "hi-IN-SwaraNeural",
    "hindi_rival": "hi-IN-DivyaNeural",
    # Kannada dialogue
    "kannada_human": "kn-IN-GaganNeural",
    "kannada_bot": "kn-IN-SapnaNeural",
}

# Dedicated Character Voice Profiles with tailored pitch deepening (Hz), rate, and persona
CHARACTER_VOICE_PROFILES = {
    "human_male": {
        "voice": "en-US-AndrewNeural",
        "pitch": "+0Hz",
        "rate": "+2%",
        "description": "Natural conversational developer tone, expressive",
    },
    "human_female": {
        "voice": "en-US-JennyNeural",
        "pitch": "+0Hz",
        "rate": "+0%",
        "description": "Sharp, articulate tech lead / skeptic",
    },
    "antigravity_bot": {
        "voice": "en-US-BrianNeural",
        "pitch": "-14Hz",
        "rate": "-2%",
        "description": "Deep resonant authoritative baritone Google Antigravity AI",
    },
    "gemini": {
        "voice": "en-US-BrianNeural",
        "pitch": "-12Hz",
        "rate": "-1%",
        "description": "Smooth cosmic authoritative baritone Gemini AI",
    },
    "claude": {
        "voice": "en-GB-RyanNeural",
        "pitch": "-10Hz",
        "rate": "-1%",
        "description": "Sophisticated British intellectual dry-witted Claude AI",
    },
    "grok": {
        "voice": "en-US-ChristopherNeural",
        "pitch": "-16Hz",
        "rate": "+4%",
        "description": "Deep sarcastic fast rogue cyber AI",
    },
    "codex": {
        "voice": "en-US-EricNeural",
        "pitch": "-22Hz",
        "rate": "-3%",
        "description": "Deep resonant cinematic hacker bass AI",
    },
    "dad": {
        "voice": "en-IN-PrabhatNeural",
        "pitch": "-4Hz",
        "rate": "-1%",
        "description": "Authoritative, nostalgic Indian Dad tone, scolding yet hilarious",
    },
    "boomer_dad": {
        "voice": "en-US-ChristopherNeural",
        "pitch": "-8Hz",
        "rate": "-2%",
        "description": "Grumpy traditional Dad questioning electronics and power bills",
    },
}


def apply_broadcast_vocal_depth(input_audio: str, output_audio: str) -> bool:
    """
    Applies studio-grade broadcast DSP mastering to TTS audio for maximum vocal depth,
    warmth, chest resonance (proximity effect), and crisp articulation matching the viral reels.
    """
    import subprocess
    filter_chain = (
        "highpass=f=70,"
        "equalizer=f=120:t=q:w=1.2:g=4.2,"
        "equalizer=f=900:t=q:w=2.0:g=-2.0,"
        "equalizer=f=4200:t=q:w=1.5:g=2.5,"
        "acompressor=threshold=-18dB:ratio=3.2:attack=15:release=85:makeup=2.5dB,"
        "aecho=0.8:0.85:26:0.08,"
        "loudnorm=I=-16:TP=-1.0:LRA=7"
    )
    cmd = [
        "ffmpeg", "-y",
        "-i", input_audio,
        "-af", filter_chain,
        "-c:a", "libmp3lame",
        "-b:a", "192k",
        output_audio
    ]
    try:
        res = subprocess.run(cmd, capture_output=True, check=True)
        return True
    except Exception as e:
        print(f"⚠️ Broadcast DSP mastering fallback: {e}")
        return False


def detect_language(text: str) -> str:
    """Detects primary language script: 'kn' (Kannada), 'hi' (Hindi), or 'en' (English)."""
    # Kannada Unicode block: U+0C80 - U+0CFF
    if re.search(r'[\u0C80-\u0CFF]', text):
        return "kn"
    # Devanagari Unicode block (Hindi): U+0900 - U+097F
    if re.search(r'[\u0900-\u097F]', text):
        return "hi"
    return "en"


def get_default_voice_for_text(text: str, style: str = "educational") -> str:
    """Selects the optimal neural voice based on language script and video style."""
    lang = detect_language(text)
    if lang == "kn":
        return PRESET_VOICES["kannada_male"]
    elif lang == "hi":
        return PRESET_VOICES["hindi_male"]
    else:
        if style in ["funny", "anime"]:
            return PRESET_VOICES["energetic_male"]
        return PRESET_VOICES["educational_male"]


def clean_text_for_speech(text: str) -> str:
    """Cleans text of Markdown formatting, asterisks, brackets for clean TTS synthesis."""
    text = re.sub(r'[*#_~`>\[\]\(\)]', ' ', text)
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


def get_audio_duration(file_path: str) -> float:
    """Calculates audio duration in seconds using mutagen or ffprobe."""
    if MP3 is not None and os.path.exists(file_path):
        try:
            audio = MP3(file_path)
            if audio.info and audio.info.length:
                return float(audio.info.length)
        except Exception:
            pass

    # Fallback to ffprobe
    try:
        import subprocess
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
        return 12.0


def build_word_and_chunk_timings(sentences: List[Dict[str, Any]]) -> Dict[str, Any]:
    """
    Interpolates word-level timestamps within sentence boundaries
    and groups words into dynamic 2-4 word caption pills.
    Works seamlessly across English, Hindi, and Kannada.
    """
    all_words = []
    
    for sent in sentences:
        s_text = sent["text"].strip()
        s_start = sent["start"]
        s_end = sent["end"]
        s_duration = max(s_end - s_start, 0.2)
        
        words = s_text.split()
        if not words:
            continue
            
        weights = [max(len(w), 2) for w in words]
        total_weight = sum(weights)
        
        current_time = s_start
        for i, word in enumerate(words):
            word_dur = (weights[i] / total_weight) * s_duration
            w_start = round(current_time, 3)
            w_end = round(current_time + word_dur, 3)
            current_time += word_dur
            
            clean_word = re.sub(r'^[^\w\u0900-\u097F\u0C80-\u0CFF]+|[^\w\u0900-\u097F\u0C80-\u0CFF]+$', '', word)
            all_words.append({
                "word": clean_word if clean_word else word,
                "raw": word,
                "start": w_start,
                "end": w_end
            })

    # Group into readable subtitle chunks (2-3 words each or punctuation break)
    chunks = []
    chunk_words = []
    
    for w in all_words:
        chunk_words.append(w)
        ends_with_punct = bool(re.search(r'[.,!?:;|॥]$', w["raw"]))
        if len(chunk_words) >= 3 or ends_with_punct:
            chunks.append({
                "start": chunk_words[0]["start"],
                "end": chunk_words[-1]["end"],
                "text": " ".join([cw["raw"] for cw in chunk_words]),
                "words": list(chunk_words)
            })
            chunk_words = []
            
    if chunk_words:
        chunks.append({
            "start": chunk_words[0]["start"],
            "end": chunk_words[-1]["end"],
            "text": " ".join([cw["raw"] for cw in chunk_words]),
            "words": list(chunk_words)
        })

    return {
        "words": all_words,
        "chunks": chunks
    }


async def _synthesize_edge_tts(
    text: str,
    voice: str,
    rate: str,
    out_audio: str,
    pitch: str = "+0Hz"
) -> List[Dict[str, Any]]:
    """Synthesizes voice using Edge-TTS with strict timeout and automatic retry."""
    last_err = None
    for attempt in range(1, 4):
        try:
            comm = edge_tts.Communicate(text, voice=voice, rate=rate, pitch=pitch)
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
            await asyncio.sleep(0.5 * attempt)

    raise RuntimeError(f"Edge-TTS failed after 3 attempts: {repr(last_err)}")


def _synthesize_gtts(
    text: str,
    out_audio: str,
    lang: str = "en"
) -> List[Dict[str, Any]]:
    """Fallback TTS using Google Translate TTS with explicit timeout."""
    if gTTS is None:
        raise RuntimeError("gTTS package not installed for fallback.")
    gtts_lang = lang if lang in ["hi", "kn", "en"] else "en"
    tts = gTTS(text=text, lang=gtts_lang, timeout=12)
    os.makedirs(os.path.dirname(os.path.abspath(out_audio)), exist_ok=True)
    tts.save(out_audio)

    total_dur = get_audio_duration(out_audio)
    sentences_raw = [s.strip() for s in re.split(r'(?<=[.!?|॥])\s+', text) if s.strip()]
    if not sentences_raw:
        sentences_raw = [text]

    total_chars = sum(len(s) for s in sentences_raw)
    sentences = []
    cur_t = 0.0
    for s in sentences_raw:
        dur = (len(s) / max(total_chars, 1)) * total_dur
        sentences.append({
            "text": s,
            "start": round(cur_t, 3),
            "end": round(cur_t + dur, 3)
        })
        cur_t += dur

    return sentences


def generate_speech(
    text: str,
    voice: Optional[str] = None,
    rate: str = "+0%",
    style: str = "educational",
    out_audio: str = "public/voice.mp3",
    out_vtt: str = "public/subs.vtt",
    out_json: str = "public/subs.json",
    meta_json: str = "public/video-meta.json",
    title: str = "EduReel Video"
) -> Dict[str, Any]:
    """
    Main multilingual speech generator. Produces:
    1. MP3 audio
    2. WebVTT subtitles (.vtt)
    3. Karaoke word-level timings (.json)
    4. Video metadata (.json) with exact frame calculation for Remotion.
    """
    clean_text = clean_text_for_speech(text)
    if not clean_text:
        raise ValueError("Text cannot be empty.")

    lang = detect_language(clean_text)
    selected_voice = voice or get_default_voice_for_text(clean_text, style)

    print(f"🎙️ Synthesizing Voice [{lang.upper()}] with '{selected_voice}' (Rate: {rate})...")
    sentences = []
    tts_provider = "edge-tts"

    # Try Edge-TTS first
    try:
        sentences = asyncio.run(_synthesize_edge_tts(clean_text, selected_voice, rate, out_audio))
        if not sentences or os.path.getsize(out_audio) < 500:
            raise RuntimeError("Edge-TTS generated empty output.")
    except Exception as e:
        print(f"⚠️ Edge-TTS encountered error: {e}. Falling back to gTTS...")
        try:
            sentences = _synthesize_gtts(clean_text, out_audio, lang=lang)
            tts_provider = "gtts-fallback"
        except Exception as e_fallback:
            raise RuntimeError(f"All TTS engines failed: {e_fallback}")

    audio_duration = get_audio_duration(out_audio)
    duration_in_frames = int(math.ceil((audio_duration + 0.4) * 30))

    timing_data = build_word_and_chunk_timings(sentences)

    # Write WebVTT
    vtt_lines = ["WEBVTT\n"]
    for i, chunk in enumerate(timing_data["chunks"]):
        start_ts = format_vtt_timestamp(chunk["start"])
        end_ts = format_vtt_timestamp(chunk["end"])
        vtt_lines.append(f"{i + 1}\n{start_ts} --> {end_ts}\n{chunk['text']}\n")

    os.makedirs(os.path.dirname(os.path.abspath(out_vtt)), exist_ok=True)
    with open(out_vtt, "w", encoding="utf-8") as f:
        f.write("\n".join(vtt_lines))

    # Write word-level JSON for Karaoke bouncing animations
    os.makedirs(os.path.dirname(os.path.abspath(out_json)), exist_ok=True)
    with open(out_json, "w", encoding="utf-8") as f:
        json.dump(timing_data, f, indent=2, ensure_ascii=False)

    meta = {
        "title": title,
        "language": lang,
        "ttsProvider": tts_provider,
        "voice": selected_voice,
        "rate": rate,
        "durationInSeconds": round(audio_duration, 3),
        "durationInFrames": duration_in_frames,
        "fps": 30,
        "width": 1080,
        "height": 1920,
        "wordCount": len(timing_data["words"]),
        "chunksCount": len(timing_data["chunks"])
    }

    os.makedirs(os.path.dirname(os.path.abspath(meta_json)), exist_ok=True)
    with open(meta_json, "w", encoding="utf-8") as f:
        json.dump(meta, f, indent=2, ensure_ascii=False)

    print(f"✅ Voice generated: {out_audio} ({audio_duration:.2f}s, {duration_in_frames} frames @ 30fps)")
    print(f"✅ Subtitles generated: {out_vtt} & {out_json}")
    print(f"✅ Metadata generated: {meta_json}")

    return {
        "audio_path": out_audio,
        "vtt_path": out_vtt,
        "json_path": out_json,
        "meta_path": meta_json,
        "duration": audio_duration,
        "frames": duration_in_frames,
        "voice": selected_voice,
        "language": lang,
        "provider": tts_provider
    }


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
    title: str = "Diner Dialogue Reel",
    pause_between_turns: float = 0.20,
) -> Dict[str, Any]:
    """
    Synthesizes multi-speaker conversational dialogue (e.g. Junior Dev vs Rival Dev vs Antigravity Bot).
    Synthesizes each turn with corresponding voice, inserts natural micro-pauses,
    concatenates seamlessly via FFmpeg, applies broadcast vocal depth DSP, and generates synchronized word cues.
    """
    import tempfile
    import subprocess
    import shutil
    import time

    if not dialogue:
        raise ValueError("Dialogue list cannot be empty.")

    # Determine default voices based on first line's detected language
    first_text = dialogue[0]["text"]
    lang = detect_language(first_text)

    if not human_voice:
        if lang == "hi":
            human_voice = PRESET_VOICES["hindi_human"]
        elif lang == "kn":
            human_voice = PRESET_VOICES["kannada_human"]
        else:
            human_voice = PRESET_VOICES["human_male"]

    if not bot_voice:
        if lang == "hi":
            bot_voice = PRESET_VOICES["hindi_bot"]
        elif lang == "kn":
            bot_voice = PRESET_VOICES["kannada_bot"]
        else:
            bot_voice = PRESET_VOICES["bot_male"]

    if not rival_voice:
        if lang == "hi":
            rival_voice = PRESET_VOICES.get("hindi_rival", "hi-IN-DivyaNeural")
        else:
            rival_voice = PRESET_VOICES["rival_male"]

    print(f"🎙️ Synthesizing Dialogue ({len(dialogue)} turns) [Lang: {lang.upper()}]...")
    print(f"   👤 Dev/Skeptic Voice : {human_voice}")
    print(f"   👔 Rival/Senior Voice: {rival_voice}")
    print(f"   🤖 Antigravity Voice : {bot_voice}")

    all_words = []
    all_chunks = []
    turns_summary = []

    with tempfile.TemporaryDirectory() as tmpdir:
        turn_audio_files = []
        current_timeline = 0.0

        for idx, turn in enumerate(dialogue):
            speaker = turn.get("speaker", "human").lower()
            text = clean_text_for_speech(turn.get("text", ""))
            if not text:
                continue

            pitch = turn.get("pitch", "+0Hz")
            turn_rate = turn.get("rate") or rate

            # Dynamic Character Voice Profile matching
            matched_profile = None
            if "dad" in speaker or "father" in speaker or "uncle" in speaker:
                matched_profile = CHARACTER_VOICE_PROFILES.get("dad")
            elif "female" in speaker:
                matched_profile = CHARACTER_VOICE_PROFILES.get("human_female")
            elif "gemini" in speaker:
                matched_profile = CHARACTER_VOICE_PROFILES.get("gemini")
            elif "claude" in speaker:
                matched_profile = CHARACTER_VOICE_PROFILES.get("claude")
            elif "grok" in speaker:
                matched_profile = CHARACTER_VOICE_PROFILES.get("grok")
            elif "codex" in speaker:
                matched_profile = CHARACTER_VOICE_PROFILES.get("codex")
            elif "antigravity" in speaker or "bot" in speaker or "ai" in speaker:
                matched_profile = CHARACTER_VOICE_PROFILES.get("antigravity_bot")
            elif "male" in speaker or "human" in speaker or "junior" in speaker or "dev" in speaker:
                matched_profile = CHARACTER_VOICE_PROFILES.get("human_male")

            if matched_profile and not turn.get("voice"):
                voice = matched_profile["voice"]
                if not turn.get("pitch"):
                    pitch = matched_profile["pitch"]
                if not turn.get("rate"):
                    turn_rate = matched_profile["rate"]
            elif speaker in ["bot", "gemini", "antigravity", "ai"]:
                voice = turn.get("voice") or bot_voice
            elif speaker in ["rival", "senior", "traditional", "human2", "boss"]:
                voice = turn.get("voice") or rival_voice
            else:
                voice = turn.get("voice") or human_voice

            # Emotional prosody adjustment
            emotion = turn.get("emotion", "normal").lower()
            if emotion == "angry":
                turn_rate = "+5%"
                if pitch == "+0Hz":
                    pitch = "+6Hz"
            elif emotion == "smug":
                turn_rate = "-2%"
                if pitch == "+0Hz":
                    pitch = "-12Hz"
            elif emotion == "shocked":
                turn_rate = "+7%"
                if pitch == "+0Hz":
                    pitch = "+10Hz"

            turn_audio_path = os.path.join(tmpdir, f"turn_{idx:03d}.mp3")

            # Synthesize turn audio with pitch deepening & emotional rate
            try:
                sentences = asyncio.run(_synthesize_edge_tts(text, voice, turn_rate, turn_audio_path, pitch=pitch))
                if not sentences or os.path.getsize(turn_audio_path) < 200:
                    raise RuntimeError("Empty turn audio from edge-tts")
            except Exception as e:
                print(f"⚠️ Turn {idx} fallback to gTTS: {e}")
                turn_lang = detect_language(text)
                sentences = _synthesize_gtts(text, turn_audio_path, lang=turn_lang)
            time.sleep(0.12)

            turn_duration = get_audio_duration(turn_audio_path)
            turn_start = round(current_timeline, 3)
            turn_end = round(turn_start + turn_duration, 3)

            # Build word and chunk timings for this turn
            turn_timing = build_word_and_chunk_timings(sentences)

            # Offset timestamps to global timeline and attach speaker
            for w in turn_timing["words"]:
                w_start = round(turn_start + w["start"], 3)
                w_end = round(turn_start + w["end"], 3)
                all_words.append({
                    "word": w["word"],
                    "raw": w["raw"],
                    "start": w_start,
                    "end": w_end,
                    "speaker": speaker
                })

            for c in turn_timing["chunks"]:
                c_start = round(turn_start + c["start"], 3)
                c_end = round(turn_start + c["end"], 3)
                all_chunks.append({
                    "start": c_start,
                    "end": c_end,
                    "text": c["text"],
                    "speaker": speaker,
                    "words": [
                        {**cw, "start": round(turn_start + cw["start"], 3), "end": round(turn_start + cw["end"], 3), "speaker": speaker}
                        for cw in c.get("words", [])
                    ]
                })

            turns_summary.append({
                "index": idx,
                "speaker": speaker,
                "start": turn_start,
                "end": turn_end,
                "duration": round(turn_duration, 3),
                "text": text,
                "cardTrigger": turn.get("cardTrigger", None)
            })

            turn_audio_files.append(turn_audio_path)

            # Add dynamic dramatic pause between turns (except last turn)
            if idx < len(dialogue) - 1:
                # Comedic timing: calculate pause duration based on emotion, speaker, and text
                turn_pause = turn.get("pause_after")
                if turn_pause is None:
                    if emotion == "smug":
                        turn_pause = 0.50  # Deadpan pause after AI roast lands
                    elif emotion == "shocked":
                        turn_pause = 0.38  # Disbelief / pause before comeback
                    elif emotion == "angry":
                        turn_pause = 0.28  # Snappy, heated confrontation
                    elif "?" in text:
                        turn_pause = 0.42  # Setup question waiting for answer
                    else:
                        turn_pause = 0.25  # Natural conversational break

                if turn_pause > 0.04:
                    pause_turn_file = os.path.join(tmpdir, f"pause_{idx:03d}.mp3")
                    subprocess.run(
                        [
                            "ffmpeg", "-y", "-f", "lavfi",
                            "-i", "anullsrc=r=24000:cl=mono",
                            "-t", f"{turn_pause:.3f}",
                            "-q:a", "9", "-acodec", "libmp3lame",
                            pause_turn_file
                        ],
                        capture_output=True,
                        check=True
                    )
                    turn_audio_files.append(pause_turn_file)
                    current_timeline = round(turn_end + turn_pause, 3)
                else:
                    current_timeline = turn_end
            else:
                current_timeline = turn_end

        # Create concat list for ffmpeg
        concat_list_path = os.path.join(tmpdir, "concat.txt")
        with open(concat_list_path, "w", encoding="utf-8") as f:
            for file_path in turn_audio_files:
                f.write(f"file '{file_path}'\n")

        # Concat with ffmpeg to raw master
        raw_master = os.path.join(tmpdir, "raw_master.mp3")
        subprocess.run(
            [
                "ffmpeg", "-y", "-f", "concat", "-safe", "0",
                "-i", concat_list_path,
                "-c:a", "libmp3lame", "-b:a", "192k",
                raw_master
            ],
            capture_output=True,
            check=True
        )

        # Apply studio-grade broadcast DSP mastering for maximum vocal depth & warmth
        print("🎛️ Mastering Audio with Broadcast Vocal Depth (Chest Warmth + Proximity + Limiting)...")
        os.makedirs(os.path.dirname(os.path.abspath(out_audio)), exist_ok=True)
        if not apply_broadcast_vocal_depth(raw_master, out_audio):
            shutil.copy2(raw_master, out_audio)

    total_duration = get_audio_duration(out_audio)
    duration_in_frames = int(math.ceil((total_duration + 0.5) * 30))

    # Extract audio envelope for lip sync and audio-reactive 3D face animation
    envelope = []
    try:
        from engine.audio_analyzer import extract_frame_audio_envelope
        envelope_path = os.path.join(os.path.dirname(os.path.abspath(out_audio)), "audio_envelope.json")
        envelope = extract_frame_audio_envelope(out_audio, fps=30, out_json=envelope_path)
        print(f"📊 Extracted {len(envelope)} audio envelope frames for reactive mouth syncing.")
    except Exception as e_env:
        print(f"⚠️ Audio envelope extraction notice: {e_env}")

    # Write WebVTT
    vtt_lines = ["WEBVTT\n"]
    for i, chunk in enumerate(all_chunks):
        start_ts = format_vtt_timestamp(chunk["start"])
        end_ts = format_vtt_timestamp(chunk["end"])
        vtt_lines.append(f"{i + 1}\n{start_ts} --> {end_ts}\n[{chunk['speaker'].upper()}] {chunk['text']}\n")

    os.makedirs(os.path.dirname(os.path.abspath(out_vtt)), exist_ok=True)
    with open(out_vtt, "w", encoding="utf-8") as f:
        f.write("\n".join(vtt_lines))

    # Write JSON data with turns and chunks
    full_data = {
        "words": all_words,
        "chunks": all_chunks,
        "turns": turns_summary
    }

    os.makedirs(os.path.dirname(os.path.abspath(out_json)), exist_ok=True)
    with open(out_json, "w", encoding="utf-8") as f:
        json.dump(full_data, f, indent=2, ensure_ascii=False)

    # Write video metadata
    meta = {
        "title": title,
        "language": lang,
        "type": "dialogue",
        "durationInSeconds": round(total_duration, 3),
        "durationInFrames": duration_in_frames,
        "fps": 30,
        "width": 1080,
        "height": 1920,
        "speakers": {
            "human": human_voice,
            "bot": bot_voice
        },
        "turnsCount": len(turns_summary),
        "wordCount": len(all_words),
        "chunksCount": len(all_chunks)
    }

    os.makedirs(os.path.dirname(os.path.abspath(meta_json)), exist_ok=True)
    with open(meta_json, "w", encoding="utf-8") as f:
        json.dump(meta, f, indent=2, ensure_ascii=False)

    print(f"✅ Dialogue track generated: {out_audio} ({total_duration:.2f}s, {duration_in_frames} frames @ 30fps)")
    print(f"✅ Subtitles generated: {out_vtt} & {out_json}")
    print(f"✅ Metadata generated: {meta_json}")

    return {
        "audio_path": out_audio,
        "vtt_path": out_vtt,
        "json_path": out_json,
        "meta_path": meta_json,
        "duration": total_duration,
        "frames": duration_in_frames,
        "turns": turns_summary,
        "language": lang,
        "envelope": envelope
    }


if __name__ == "__main__":
    test_hi = "क्या आपको पता है कि ब्लैक होल के पास समय धीमा क्यों हो जाता है?"
    res_hi = generate_speech(test_hi, title="Hindi Test")
    print("Hindi Test completed:", res_hi)
