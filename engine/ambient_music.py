"""
Procedural Lo-Fi Ambient Music Bed & UI SFX Generator
Generates:
1. Warm, copyright-free Rhodes/sine jazz chords for background ambience ducked cleanly at -22 dB.
2. Crisp procedural UI sound effects (soft whoosh/pop and iOS-style chime) at -10 dB.
"""

import os
from pathlib import Path
from typing import Optional
import numpy as np
import soundfile as sf

PROJECT_ROOT = Path(__file__).resolve().parent.parent
DEFAULT_AMBIENT_PATH = PROJECT_ROOT / "assets" / "audio" / "ambient_bed.wav"
DEFAULT_SFX_WHOOSH_PATH = PROJECT_ROOT / "assets" / "audio" / "sfx_whoosh.wav"
DEFAULT_SFX_CHIME_PATH = PROJECT_ROOT / "assets" / "audio" / "sfx_chime.wav"
DEFAULT_SFX_BASS_THUD_PATH = PROJECT_ROOT / "assets" / "audio" / "sfx_bass_thud.wav"


def note_to_freq(note_name: str) -> float:
    """Converts a note name (e.g. 'C3', 'F#4') to its frequency in Hz."""
    notes = ['C', 'C#', 'D', 'D#', 'E', 'F', 'F#', 'G', 'G#', 'A', 'A#', 'B']
    flat_map = {'Db': 'C#', 'Eb': 'D#', 'Gb': 'F#', 'Ab': 'G#', 'Bb': 'A#'}

    name = flat_map.get(note_name[:-1], note_name[:-1])
    octave = int(note_name[-1])
    semitone = notes.index(name)
    midi_num = (octave + 1) * 12 + semitone
    return 440.0 * (2.0 ** ((midi_num - 69) / 12.0))


def generate_ambient_music_bed(
    duration_sec: float = 45.0,
    out_path: Path = DEFAULT_AMBIENT_PATH,
    sample_rate: int = 24000
) -> str:
    """
    Generates a lush, warm lo-fi Rhodes/pad ambient chord progression:
    Progression: Cmaj9 -> Am9 -> Fmaj7 -> G13 (warm, contemplative, relaxed).
    """
    out_path = Path(out_path)
    if out_path.exists() and out_path.stat().st_size > 10000:
        return str(out_path)

    out_path.parent.mkdir(parents=True, exist_ok=True)

    # 4 warm chord voicings (frequencies in Hz)
    chord_notes = [
        ['C3', 'G3', 'B3', 'D4', 'E4'],  # Cmaj9
        ['A2', 'E3', 'G3', 'C4', 'E4'],  # Am9
        ['F2', 'C3', 'E3', 'A3', 'C4'],  # Fmaj7
        ['G2', 'F3', 'B3', 'E4', 'A4'],  # G13
    ]

    chord_freqs = [[note_to_freq(n) for n in c] for c in chord_notes]
    chord_duration = 6.0  # seconds per chord
    total_samples = int(duration_sec * sample_rate)
    full_audio = np.zeros(total_samples, dtype=np.float32)

    t = np.arange(total_samples) / sample_rate
    num_chords = int(np.ceil(duration_sec / chord_duration))

    for i in range(num_chords):
        c_idx = i % len(chord_freqs)
        freqs = chord_freqs[c_idx]
        start_sample = int(i * chord_duration * sample_rate)
        chord_len = int(chord_duration * 1.25 * sample_rate)  # smooth crossfade overlap
        end_sample = min(total_samples, start_sample + chord_len)
        actual_len = end_sample - start_sample
        if actual_len <= 0:
            break

        chord_t = np.arange(actual_len) / sample_rate

        # Rhodes-like harmonic envelope: bell attack + warm body decay
        amp_env = np.exp(-chord_t * 0.45) * (1.0 - np.exp(-chord_t * 25.0))
        # Gentle tremolo (3.5 Hz)
        tremolo = 1.0 + 0.12 * np.sin(2.0 * np.pi * 3.5 * chord_t)

        chord_wave = np.zeros(actual_len, dtype=np.float32)
        for f in freqs:
            # Subtle detuning for analog chorus warmth
            detune = 1.0 + 0.0015 * np.sin(2.0 * np.pi * 0.4 * chord_t)
            # Fundamental sine
            w1 = np.sin(2.0 * np.pi * f * detune * chord_t)
            # 2nd harmonic (warmth)
            w2 = 0.30 * np.sin(2.0 * np.pi * f * 2.0 * chord_t) * np.exp(-chord_t * 0.7)
            # 3rd harmonic (subtle chime)
            w3 = 0.10 * np.sin(2.0 * np.pi * f * 3.0 * chord_t) * np.exp(-chord_t * 1.2)
            chord_wave += (w1 + w2 + w3)

        chord_wave = chord_wave * amp_env * tremolo * 0.08
        full_audio[start_sample:end_sample] += chord_wave[:actual_len]

    # Gentle vinyl-like lo-fi soft clipping & normalization
    max_val = np.max(np.abs(full_audio))
    if max_val > 0:
        full_audio = (full_audio / max_val) * 0.65

    sf.write(str(out_path), full_audio, sample_rate, subtype='PCM_16')
    print(f"🎹 [Ambient Music] Generated procedural lo-fi ambient bed: {out_path} ({duration_sec:.1f}s)")
    return str(out_path)


def generate_sfx_whoosh(
    out_path: Path = DEFAULT_SFX_WHOOSH_PATH,
    sample_rate: int = 24000,
    volume_db: float = -10.0
) -> str:
    """
    Synthesizes a crisp, subtle copyright-free whoosh/pop WAV via pure NumPy:
    - Rapid exponential pitch drop (450 Hz -> 80 Hz) for a punchy modern pop.
    - Subtle smoothed noise swoosh for air texture.
    - Normalized and scaled to volume_db (-10 dB by default).
    """
    out_path = Path(out_path)
    out_path.parent.mkdir(parents=True, exist_ok=True)

    dur_whoosh = 0.22
    n_samples = int(dur_whoosh * sample_rate)
    t = np.arange(n_samples) / sample_rate

    # Exponential pitch drop from 450 Hz to 80 Hz
    decay_rate = 25.0
    phi = 2.0 * np.pi * (80.0 * t + (450.0 - 80.0) * (1.0 - np.exp(-t * decay_rate)) / decay_rate)
    pop_sine = np.sin(phi)

    # Gentle whoosh noise
    rng = np.random.RandomState(42)
    noise = rng.normal(0, 0.2, n_samples)
    noise = np.convolve(noise, np.ones(5) / 5.0, mode='same')

    env = (1.0 - np.exp(-t * 70.0)) * np.exp(-t * 13.0)
    whoosh_wave = (0.75 * pop_sine + 0.25 * noise) * env
    max_val = np.max(np.abs(whoosh_wave))
    if max_val > 0:
        target_amp = 10.0 ** (volume_db / 20.0)
        whoosh_wave = (whoosh_wave / max_val) * target_amp

    sf.write(str(out_path), whoosh_wave.astype(np.float32), sample_rate, subtype='PCM_16')
    return str(out_path)


def generate_sfx_chime(
    out_path: Path = DEFAULT_SFX_CHIME_PATH,
    sample_rate: int = 24000,
    volume_db: float = -10.0
) -> str:
    """
    Synthesizes a subtle, pristine iOS-style chime WAV via pure NumPy:
    - Two harmonic bell tones (E6: 1318.5 Hz + B6: 1975.5 Hz) staggered by 35ms.
    - Instant attack with smooth exponential ring decay.
    - Normalized and scaled to volume_db (-10 dB by default).
    """
    out_path = Path(out_path)
    out_path.parent.mkdir(parents=True, exist_ok=True)

    dur_chime = 0.40
    n_samples = int(dur_chime * sample_rate)
    t = np.arange(n_samples) / sample_rate

    # Tone 1: E6 (1318.5 Hz)
    env1 = (1.0 - np.exp(-t * 400.0)) * np.exp(-t * 8.0)
    tone1 = np.sin(2.0 * np.pi * 1318.5 * t) * env1 + 0.22 * np.sin(2.0 * np.pi * 2637.0 * t) * np.exp(-t * 14.0)

    # Tone 2: B6 (1975.5 Hz), staggered by 35ms
    delay_samples = int(0.035 * sample_rate)
    tone2 = np.zeros_like(t)
    t2_sub = t[delay_samples:] - 0.035
    env2 = (1.0 - np.exp(-t2_sub * 400.0)) * np.exp(-t2_sub * 7.5)
    tone2[delay_samples:] = np.sin(2.0 * np.pi * 1975.5 * t2_sub) * env2 + 0.22 * np.sin(2.0 * np.pi * 3951.0 * t2_sub) * np.exp(-t2_sub * 13.0)

    chime_wave = (0.5 * tone1 + 0.7 * tone2)
    max_val = np.max(np.abs(chime_wave))
    if max_val > 0:
        target_amp = 10.0 ** (volume_db / 20.0)
        chime_wave = (chime_wave / max_val) * target_amp

    sf.write(str(out_path), chime_wave.astype(np.float32), sample_rate, subtype='PCM_16')
    return str(out_path)


def generate_sfx_bass_thud(
    out_path: Path = DEFAULT_SFX_BASS_THUD_PATH,
    sample_rate: int = 24000,
    volume_db: float = -10.0
) -> str:
    """
    Synthesizes a deep procedural bass thud / comedic punchline sting WAV via pure NumPy:
    - Pitch glide from ~55 Hz down to 30 Hz over 0.35s duration.
    - Punchy transient attack with exponential decay envelope.
    - Scaled to volume_db (-10 dB by default) for a clean comedic sting.
    """
    out_path = Path(out_path)
    out_path.parent.mkdir(parents=True, exist_ok=True)

    dur = 0.35
    n_samples = int(dur * sample_rate)
    t = np.arange(n_samples) / sample_rate

    # Exponential pitch glide from 55 Hz down to 30 Hz
    decay_rate = 14.0
    phi = 2.0 * np.pi * (30.0 * t + (55.0 - 30.0) * (1.0 - np.exp(-t * decay_rate)) / decay_rate)
    sine_wave = np.sin(phi)

    # Sub-harmonic saturation for warm punch
    sub = 0.35 * np.sin(phi * 0.5)

    # Fast transient attack (4ms) + smooth exponential decay
    env = (1.0 - np.exp(-t * 220.0)) * np.exp(-t * 8.5)
    thud_wave = (sine_wave + sub) * env

    max_val = np.max(np.abs(thud_wave))
    if max_val > 0:
        target_amp = 10.0 ** (volume_db / 20.0)
        thud_wave = (thud_wave / max_val) * target_amp

    sf.write(str(out_path), thud_wave.astype(np.float32), sample_rate, subtype='PCM_16')
    return str(out_path)


def generate_sfx_track(
    total_duration_sec: float,
    whoosh_time_sec: Optional[float] = None,
    toast_chime_sec: Optional[float] = None,
    chime_time_sec: Optional[float] = None,
    punchline_thud_sec: Optional[float] = None,
    out_path: Optional[Path] = None,
    sample_rate: int = 24000,
    volume_db: float = -10.0
) -> str:
    """
    Generates a full-length synchronized UI SFX track:
    - Places whoosh/pop at whoosh_time_sec (Turn 5 proof card appearance).
    - Places subtle iOS chime at toast_chime_sec (Turn 9 notification toast appearance).
    - Places punchline bass thud at punchline_thud_sec (Turn 9/10 roast punchline sting).
    - Places iOS chime at chime_time_sec (End-Card cliffhanger).
    - All rendered at volume_db (-10 dB by default).
    """
    total_samples = int(max(total_duration_sec, 1.0) * sample_rate)
    sfx_track = np.zeros(total_samples, dtype=np.float32)

    # 1. Overlay whoosh at whoosh_time_sec
    if whoosh_time_sec is not None and whoosh_time_sec >= 0:
        whoosh_file = generate_sfx_whoosh(sample_rate=sample_rate, volume_db=volume_db)
        whoosh_data, _ = sf.read(whoosh_file)
        start_idx = int(whoosh_time_sec * sample_rate)
        end_idx = min(total_samples, start_idx + len(whoosh_data))
        if start_idx < total_samples and end_idx > start_idx:
            chunk_len = end_idx - start_idx
            sfx_track[start_idx:end_idx] += whoosh_data[:chunk_len]

    # 2. Overlay toast chime at toast_chime_sec
    if toast_chime_sec is not None and toast_chime_sec >= 0:
        chime_file = generate_sfx_chime(sample_rate=sample_rate, volume_db=volume_db)
        chime_data, _ = sf.read(chime_file)
        start_idx = int(toast_chime_sec * sample_rate)
        end_idx = min(total_samples, start_idx + len(chime_data))
        if start_idx < total_samples and end_idx > start_idx:
            chunk_len = end_idx - start_idx
            sfx_track[start_idx:end_idx] += chime_data[:chunk_len]

    # 3. Overlay punchline bass thud at punchline_thud_sec
    if punchline_thud_sec is not None and punchline_thud_sec >= 0:
        thud_file = generate_sfx_bass_thud(sample_rate=sample_rate, volume_db=volume_db)
        thud_data, _ = sf.read(thud_file)
        start_idx = int(punchline_thud_sec * sample_rate)
        end_idx = min(total_samples, start_idx + len(thud_data))
        if start_idx < total_samples and end_idx > start_idx:
            chunk_len = end_idx - start_idx
            sfx_track[start_idx:end_idx] += thud_data[:chunk_len]

    # 4. Overlay End-Card chime at chime_time_sec
    if chime_time_sec is not None and chime_time_sec >= 0:
        chime_file = generate_sfx_chime(sample_rate=sample_rate, volume_db=volume_db)
        chime_data, _ = sf.read(chime_file)
        start_idx = int(chime_time_sec * sample_rate)
        end_idx = min(total_samples, start_idx + len(chime_data))
        if start_idx < total_samples and end_idx > start_idx:
            chunk_len = end_idx - start_idx
            sfx_track[start_idx:end_idx] += chime_data[:chunk_len]

    if out_path is None:
        out_path = PROJECT_ROOT / "assets" / "audio" / "sfx_track.wav"
    out_path = Path(out_path)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    sf.write(str(out_path), sfx_track, sample_rate, subtype='PCM_16')
    return str(out_path)


if __name__ == "__main__":
    generate_ambient_music_bed(30.0)
    generate_sfx_whoosh()
    generate_sfx_chime()
    generate_sfx_bass_thud()
    print("Generated ambient bed, whoosh, chime, and bass thud SFX.")
