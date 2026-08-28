"""Command-line experiments for the executable textbook."""

from __future__ import annotations

import argparse
from pathlib import Path
from typing import Sequence

from .pitch import (
    interval_semitones,
    pitch_to_frequency,
    pitch_to_name,
    transpose_pitch,
)
from .waveform import SAMPLE_RATE, render_notes, write_wav
from .rhythm import sequential_starts, write_beat_sequence
from .events import NoteEvent, composition_duration, inspect_events, transpose_events
from .event_rendering import render_events

CHAPTER_00_NOTES = (
    ("C4", 261.63, 0.40),
    ("E4", 329.63, 0.40),
    ("G4", 392.00, 0.40),
    ("C5", 523.25, 0.60),
)
CHAPTER_00_FILENAME = "chapter_00_first_composition.wav"
CHAPTER_01_MELODY = (60, 64, 67, 72)
CHAPTER_01_DURATIONS = (0.40, 0.40, 0.40, 0.60)
CHAPTER_01_FILENAMES = (
    "chapter_01_original.wav",
    "chapter_01_transposed_5.wav",
    "chapter_01_transposed_octave.wav",
)
CHAPTER_02_PITCHES = (60, 64, 67, 72)
CHAPTER_02_RHYTHMS = {
    "even": (1.0, 1.0, 1.0, 1.0),
    "long_short": (2.0, 0.5, 0.5, 1.0),
    "short_long": (0.5, 0.5, 2.0, 2.0),
}
CHAPTER_02_FILENAMES = (
    "chapter_02_even.wav", "chapter_02_long_short.wav", "chapter_02_short_long.wav",
    "chapter_02_tempo_60.wav", "chapter_02_tempo_90.wav", "chapter_02_tempo_120.wav",
    "chapter_02_rest_filled.wav", "chapter_02_rest.wav",
    "chapter_02_onbeat.wav", "chapter_02_syncopated.wav",
)
CHAPTER_03_FILENAMES = (
    "chapter_03_structured_melody.wav",
    "chapter_03_even_velocity.wav",
    "chapter_03_shaped_velocity.wav",
    "chapter_03_sequential.wav",
    "chapter_03_simultaneous.wav",
    "chapter_03_original.wav",
    "chapter_03_transposed_5.wav",
)
CHAPTER_03_MELODY = (
    NoteEvent(60, 0.0, 1.0), NoteEvent(64, 1.0, 0.5),
    NoteEvent(67, 1.5, 0.5), NoteEvent(72, 2.0, 2.0),
)


def run_chapter_00(output_directory: Path = Path("outputs")) -> Path:
    """Render Chapter 0's fixed four-note composition and return its path."""
    composition = ((frequency, duration) for _, frequency, duration in CHAPTER_00_NOTES)
    output_path = output_directory / CHAPTER_00_FILENAME
    return write_wav(output_path, render_notes(composition))


def run_chapter_01(output_directory: Path = Path("outputs")) -> tuple[Path, Path, Path]:
    """Render the original melody and its +5 and +12 transpositions."""
    melodies = (
        CHAPTER_01_MELODY,
        tuple(transpose_pitch(pitch, 5) for pitch in CHAPTER_01_MELODY),
        tuple(transpose_pitch(pitch, 12) for pitch in CHAPTER_01_MELODY),
    )
    paths = tuple(output_directory / filename for filename in CHAPTER_01_FILENAMES)
    for path, melody in zip(paths, melodies, strict=True):
        notes = (
            (pitch_to_frequency(pitch), duration)
            for pitch, duration in zip(melody, CHAPTER_01_DURATIONS, strict=True)
        )
        write_wav(path, render_notes(notes))
    return paths


def run_chapter_02(output_directory: Path = Path("outputs")) -> tuple[Path, ...]:
    """Render same-pitch rhythm, tempo, silence, and offbeat comparisons."""
    paths = tuple(output_directory / name for name in CHAPTER_02_FILENAMES)
    jobs = [
        (CHAPTER_02_PITCHES, CHAPTER_02_RHYTHMS["even"], 120),
        (CHAPTER_02_PITCHES, CHAPTER_02_RHYTHMS["long_short"], 120),
        (CHAPTER_02_PITCHES, CHAPTER_02_RHYTHMS["short_long"], 120),
        *[(CHAPTER_02_PITCHES, CHAPTER_02_RHYTHMS["long_short"], bpm) for bpm in (60, 90, 120)],
        ((60, 60, 64, 67, 72), (1.0, 0.5, 0.5, 1.0, 2.0), 120),
        ((60, None, 64, 67, 72), (1.0, 0.5, 0.5, 1.0, 2.0), 120),
        ((60, None, 64, None, 67, None, 72, None), (0.5,) * 8, 120),
        ((None, 60, None, 64, None, 67, None, 72), (0.5,) * 8, 120),
    ]
    for path, (pitches, durations, bpm) in zip(paths, jobs, strict=True):
        write_beat_sequence(path, pitches, durations, bpm)
    return paths


def run_chapter_03(output_directory: Path = Path("outputs")) -> tuple[Path, ...]:
    """Render structured, intensity, simultaneity, and transformation studies."""
    even = CHAPTER_03_MELODY
    shaped = tuple(
        NoteEvent(event.pitch, event.start, event.duration, velocity)
        for event, velocity in zip(even, (60, 80, 105, 75), strict=True)
    )
    sequential = tuple(NoteEvent(pitch, index * 1.0, 1.0) for index, pitch in enumerate((60, 64, 67)))
    simultaneous = tuple(NoteEvent(pitch, 0.0, 2.0) for pitch in (60, 64, 67))
    jobs = (even, even, shaped, sequential, simultaneous, even, transpose_events(even, 5))
    paths = tuple(output_directory / name for name in CHAPTER_03_FILENAMES)
    for path, score in zip(paths, jobs, strict=True):
        write_wav(path, render_events(score, 120))
    return paths


def _pitch_table(melody: Sequence[int]) -> str:
    return "\n".join(
        f"{pitch:3}  {pitch_to_name(pitch):3}  {pitch_to_frequency(pitch):7.2f} Hz"
        for pitch in melody
    )


def _intervals(melody: Sequence[int]) -> str:
    return " ".join(
        f"{interval_semitones(first, second):+d}"
        for first, second in zip(melody, melody[1:])
    )


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Run Computational Music Composition Lab experiments.")
    parser.add_argument("chapter", choices=("chapter-00", "chapter-01", "chapter-02", "chapter-03"), help="experiment to run")
    parser.add_argument(
        "--output-directory",
        type=Path,
        default=Path("outputs"),
        help="directory for generated files (default: outputs)",
    )
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    if args.chapter == "chapter-00":
        output_path = run_chapter_00(args.output_directory)
        note_names = " → ".join(name for name, _, _ in CHAPTER_00_NOTES)
        print(
            "Chapter 0 — The Composition Laboratory\n\n"
            f"Composition:\n{note_names}\n\n"
            f"Rendering:\nsample rate: {SAMPLE_RATE} Hz\nwaveform: sine\n\n"
            f"Created:\n{output_path}\n\n"
            "Experiment complete.\nListen to the WAV file before continuing."
        )
    elif args.chapter == "chapter-01":
        paths = run_chapter_01(args.output_directory)
        transposed = tuple(transpose_pitch(pitch, 5) for pitch in CHAPTER_01_MELODY)
        print(
            "Chapter 1 — Pitch Becomes Computable\n\n"
            f"Original:\n{_pitch_table(CHAPTER_01_MELODY)}\n\n"
            f"Interval movement:\n{_intervals(CHAPTER_01_MELODY)}\n\n"
            f"Transpose: +5 semitones\n\n{_pitch_table(transposed)}\n\n"
            f"Interval movement:\n{_intervals(transposed)}\n\n"
            "The absolute pitches changed; the interval pattern stayed the same.\n\n"
            "Created:\n"
            + "\n".join(str(path) for path in paths)
            + "\n\nListen in order: original, +5 semitones, then +12 (one octave)."
        )
    elif args.chapter == "chapter-02":
        paths = run_chapter_02(args.output_directory)
        print(
            "Chapter 2 — Time and Rhythm\n\n"
            "Pitch material:\nC4 → E4 → G4 → C5\n\n"
            "PITCH asks what happens. RHYTHM asks when, and for how long.\n\n"
            "Experiment 1 — Same pitches, different rhythms\n"
            "Even:       1.0  1.0  1.0  1.0 beats\n"
            "Long-short: 2.0  0.5  0.5  1.0 beats\n"
            "Short-long: 0.5  0.5  2.0  2.0 beats\n\n"
            "Experiment 2 — Same rhythm, different tempo\n60 BPM  |  90 BPM  |  120 BPM\n"
            "Rhythmic proportions stay constant; only their unfolding rate changes.\n\n"
            "Experiment 3 — Silence\nA 0.5-beat note becomes a 0.5-beat rest. Silence is composed time.\n\n"
            "Experiment 4 — Beat grid and syncopation\n"
            "Tempo: 120 BPM    Meter: 4/4\n"
            "Beat:   1   &   2   &   3   &   4   &\n"
            "Onbeat: C4      E4      G4      C5\n"
            "Offbeat:    C4      E4      G4      C5\n"
            "A simplified 4/4 weight is strong–weak–medium–weak; it is not universal.\n\n"
            f"Sequential starts for long-short: {sequential_starts(CHAPTER_02_RHYTHMS['long_short'])}\n\n"
            "Created:\n" + "\n".join(str(path) for path in paths) +
            "\n\nPitch, starts, and durations still live in parallel lists. Chapter 3 will address that limitation."
        )
    else:
        paths = run_chapter_03(args.output_directory)
        shaped = tuple(
            NoteEvent(event.pitch, event.start, event.duration, velocity)
            for event, velocity in zip(CHAPTER_03_MELODY, (60, 80, 105, 75), strict=True)
        )
        print(
            "Chapter 3 — The Musical Event\n\n"
            "A musical event answers four questions:\n\n"
            "WHAT?        pitch\nWHEN?        start\nHOW LONG?    duration\nHOW STRONG?  velocity\n\n"
            "Score:\n\n" + inspect_events(shaped) +
            f"\n\nComposition duration:\n{composition_duration(shaped):.2f} beats\n\n"
            "Experiments:\nstructured melody\nvelocity shaping\n"
            "sequential vs simultaneous\ntransposition\n\n"
            "Can intensity alone create a sense of direction?\n"
            "The pitches are identical. Why does simultaneity change the result?\n\n"
            "Created:\n" + "\n".join(str(path) for path in paths)
        )
    return 0
