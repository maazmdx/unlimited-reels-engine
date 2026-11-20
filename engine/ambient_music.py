"""
Procedural Lo-Fi Ambient Music Bed Generator
Generates warm, copyright-free Rhodes/sine jazz chords for background ambience
ducked cleanly at -22 dB under dialogue.
"""

import os
from pathlib import Path
import numpy as np
import soundfile as sf

PROJECT_ROOT = Path(__file__).resolve().parent.parent
DEFAULT_AMBIENT_PATH = PROJECT_ROOT / "assets" / "audio" / "ambient_bed.wav"


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


if __name__ == "__main__":
    generate_ambient_music_bed(30.0)
