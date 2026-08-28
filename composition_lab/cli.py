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
from .scales import (
    MAJOR,
    NATURAL_MINOR,
    events_from_degrees,
    major_scale,
    natural_minor_scale,
)
from .melody import (
    classify_motion,
    contour_directions,
    interval_sequence,
    melodic_profile,
    motion_direction,
    pitches_from_events,
)
from .motifs import (
    augment_motif,
    build_development_study,
    diminish_motif,
    displace_motif,
    invert_motif,
    normalize_events,
    repeat_motif,
    retrograde_motif,
    sequence_motif,
    transpose_motif,
)

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
CHAPTER_04_FILENAMES = (
    "chapter_04_c_major.wav",
    "chapter_04_c_natural_minor.wav",
    "chapter_04_d_major.wav",
    "chapter_04_f_major.wav",
    "chapter_04_degree_melody_c_major.wav",
    "chapter_04_degree_melody_f_major.wav",
    "chapter_04_diatonic.wav",
    "chapter_04_chromatic.wav",
    "chapter_04_tonic_resolution.wav",
    "chapter_04_degree_7_ending.wav",
)
CHAPTER_04_DEGREES = (1, 2, 3, 5, 3, 2, 1)
CHAPTER_05_FILENAMES = (
    "chapter_05_stepwise.wav",
    "chapter_05_leaping.wav",
    "chapter_05_continuous_motion.wav",
    "chapter_05_repeated_notes.wav",
    "chapter_05_narrow_range.wav",
    "chapter_05_wide_range.wav",
    "chapter_05_arch.wav",
    "chapter_05_inverted_arch.wav",
)
CHAPTER_05_MELODIES = {
    "stepwise": (60, 62, 64, 65, 67, 65, 64, 62, 60),
    "leaping": (60, 67, 62, 69, 64, 71, 65, 67, 60),
    "continuous_motion": (60, 62, 64, 65, 67, 65, 62, 60),
    "repeated_notes": (60, 60, 62, 62, 64, 64, 62, 60),
    "narrow_range": (60, 62, 64, 62, 60, 62, 64, 62, 60),
    "wide_range": (60, 64, 69, 64, 60, 64, 69, 64, 60),
    "arch": (60, 62, 64, 67, 69, 67, 64, 62, 60),
    "inverted_arch": (69, 67, 64, 62, 60, 62, 64, 67, 69),
}
CHAPTER_06_MOTIF = (
    NoteEvent(60, 0.0, 0.5, 84),
    NoteEvent(62, 0.5, 0.5, 88),
    NoteEvent(64, 1.0, 1.0, 94),
    NoteEvent(67, 2.0, 1.0, 100),
)
CHAPTER_06_FILENAMES = (
    "chapter_06_original.wav",
    "chapter_06_repeated.wav",
    "chapter_06_transposed.wav",
    "chapter_06_sequence.wav",
    "chapter_06_retrograde.wav",
    "chapter_06_inversion.wav",
    "chapter_06_augmented.wav",
    "chapter_06_diminished.wav",
    "chapter_06_displaced.wav",
    "chapter_06_development_study.wav",
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


def run_chapter_04(output_directory: Path = Path("outputs")) -> tuple[Path, ...]:
    """Render scale, key, chromatic-note, and tonal-ending comparisons."""
    eighths = (0.5,) * 8
    melody_rhythm = (0.5,) * len(CHAPTER_04_DEGREES)
    diatonic = events_from_degrees(CHAPTER_04_DEGREES, 60, MAJOR, melody_rhythm)
    chromatic = tuple(
        NoteEvent(event.pitch - 1 if index == 2 else event.pitch,
                  event.start, event.duration, event.velocity)
        for index, event in enumerate(diatonic)
    )
    tonic_ending = events_from_degrees((1, 2, 3, 2, 1), 60, MAJOR, (0.5,) * 5)
    degree_7_ending = events_from_degrees((1, 2, 3, 2, 7), 60, MAJOR, (0.5,) * 5)
    jobs = (
        events_from_degrees(tuple(range(1, 9)), 60, MAJOR, eighths),
        events_from_degrees(tuple(range(1, 9)), 60, NATURAL_MINOR, eighths),
        events_from_degrees(tuple(range(1, 9)), 62, MAJOR, eighths),
        events_from_degrees(tuple(range(1, 9)), 65, MAJOR, eighths),
        diatonic,
        events_from_degrees(CHAPTER_04_DEGREES, 65, MAJOR, melody_rhythm),
        diatonic,
        chromatic,
        tonic_ending,
        degree_7_ending,
    )
    paths = tuple(output_directory / name for name in CHAPTER_04_FILENAMES)
    for path, score in zip(paths, jobs, strict=True):
        write_wav(path, render_events(score, 120))
    return paths


def _sequential_events(pitches: Sequence[int]) -> tuple[NoteEvent, ...]:
    """Put Chapter 5 pitch material on one shared half-beat rhythm."""
    return tuple(NoteEvent(pitch, index * 0.5, 0.5, 90) for index, pitch in enumerate(pitches))


def run_chapter_05(output_directory: Path = Path("outputs")) -> tuple[Path, ...]:
    """Render controlled interval, repetition, range, and contour comparisons."""
    paths = tuple(output_directory / name for name in CHAPTER_05_FILENAMES)
    scores = tuple(_sequential_events(pitches) for pitches in CHAPTER_05_MELODIES.values())
    for path, score in zip(paths, scores, strict=True):
        write_wav(path, render_events(score, 120))
    return paths


def chapter_06_material() -> tuple[tuple[NoteEvent, ...], tuple[tuple[NoteEvent, ...], ...]]:
    """Return the fixed motif and every listening comparison without rendering."""
    motif = tuple(normalize_events(CHAPTER_06_MOTIF))
    development, _ = build_development_study(motif)
    transformations = (
        motif,
        tuple(repeat_motif(motif, 4)),
        tuple(transpose_motif(motif, 5)),
        tuple(sequence_motif(motif, (0, 2, 4, 5))),
        tuple(retrograde_motif(motif)),
        tuple(invert_motif(motif, 60)),
        tuple(augment_motif(motif)),
        tuple(diminish_motif(motif)),
        tuple(displace_motif(motif, 0.5)),
        tuple(development),
    )
    return motif, transformations


def run_chapter_06(output_directory: Path = Path("outputs")) -> tuple[Path, ...]:
    """Render motif transformations and the longer development study."""
    _, scores = chapter_06_material()
    paths = tuple(output_directory / name for name in CHAPTER_06_FILENAMES)
    for path, score in zip(paths, scores, strict=True):
        write_wav(path, render_events(score, 120))
    return paths


def _profile_text(label: str, pitches: Sequence[int]) -> str:
    profile = melodic_profile(pitches)
    lowest = pitch_to_name(profile.lowest) if profile.lowest is not None else "—"
    highest = pitch_to_name(profile.highest) if profile.highest is not None else "—"
    return (
        f"{label}\n"
        f"notes: {profile.notes}    movements: {profile.movements}\n"
        f"lowest: {lowest}    highest: {highest}    range: {profile.range_semitones} semitones\n"
        f"repeats: {profile.repeats} ({profile.repeat_percentage:.1f}%)    "
        f"steps: {profile.steps} ({profile.stepwise_percentage:.1f}%)    "
        f"leaps: {profile.leaps} ({profile.leap_percentage:.1f}%)\n"
        f"ascending: {profile.ascending} ({profile.ascending_percentage:.1f}%)    "
        f"descending: {profile.descending} ({profile.descending_percentage:.1f}%)    "
        f"stationary: {profile.stationary} ({profile.stationary_percentage:.1f}%)\n"
        f"average interval size: {profile.average_interval_size:.1f} semitones"
    )


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
    parser.add_argument(
        "chapter",
        choices=("chapter-00", "chapter-01", "chapter-02", "chapter-03", "chapter-04", "chapter-05", "chapter-06"),
        help="experiment to run",
    )
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
    elif args.chapter == "chapter-03":
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
    elif args.chapter == "chapter-04":
        paths = run_chapter_04(args.output_directory)
        c_major = major_scale(60)
        c_minor = natural_minor_scale(60)
        f_melody = tuple(major_scale(65)[degree - 1] for degree in CHAPTER_04_DEGREES)
        rows = "\n".join(
            f"{degree:<6}  {pitch:<5}  {pitch_to_name(pitch):<4}  "
            f"{pitch_to_frequency(pitch):>9.2f}"
            for degree, pitch in enumerate(c_major, 1)
        )
        print(
            "Chapter 4 — Scales, Keys, and Tonality\n\n"
            "A NoteEvent stores a pitch, but it does not say how that pitch relates to a key.\n"
            "If the piece is in C major, which pitch classes are expected?\n\n"
            f"Major offsets:        {' '.join(map(str, MAJOR))}\n"
            f"Natural-minor offsets: {' '.join(map(str, NATURAL_MINOR))}\n"
            "Major steps: W W H W W W H   (W = 2 semitones, H = 1)\n"
            "Natural-minor steps: W H W W H W W\n\n"
            "Key: C major\n\nDegree  Pitch  Name  Frequency\n" + rows +
            f"\n\nC natural minor pitches: {' '.join(map(str, c_minor))}\n\n"
            f"Degree melody: {' '.join(map(str, CHAPTER_04_DEGREES))}\n"
            f"C major: {' '.join(pitch_to_name(pitch) for pitch in c_major[:3] + (c_major[4],) + c_major[1:3][::-1] + (c_major[0],))}\n"
            f"F major: {' '.join(pitch_to_name(pitch) for pitch in f_melody)}\n\n"
            "A key is a tonal reference system: pitches inside and outside its scale have\n"
            "different relationships, but a chromatic pitch is not musically invalid.\n"
            "Listen: what changes with one chromatic note? Which ending feels more settled?\n"
            "These responses can depend on listener and style.\n\nCreated:\n" +
            "\n".join(str(path) for path in paths)
        )
    elif args.chapter == "chapter-05":
        paths = run_chapter_05(args.output_directory)
        example_events = _sequential_events((60, 62, 64, 67, 64, 62, 60))
        example = pitches_from_events(example_events)
        intervals = interval_sequence(example)
        print(
            "Chapter 5 — Intervals and Melodic Motion\n\n"
            "A melody is not only a sequence of pitches. It is also a sequence of movements.\n\n"
            f"Melody:\n{' '.join(pitch_to_name(pitch) for pitch in example)}\n\n"
            f"Intervals:\n{' '.join(f'{interval:+d}' for interval in intervals)}\n\n"
            f"Motion:\n{' '.join(classify_motion(interval) for interval in intervals)}\n\n"
            f"Direction:\n{' '.join(motion_direction(interval) for interval in intervals)}\n"
            f"Compact contour: {' '.join(contour_directions(example))}\n\n"
            + _profile_text("STEPWISE MELODY", CHAPTER_05_MELODIES["stepwise"])
            + "\n\n"
            + _profile_text("LEAPING MELODY", CHAPTER_05_MELODIES["leaping"])
            + "\n\nScale degree is not semitone distance: in C major, 1→2 is +2, while 3→4 is +1.\n\n"
            "Analysis explains how melodies differ structurally. Listening tells us what those differences mean musically.\n"
            "Measurements describe movement; they do not determine beauty, emotion, memorability, quality, or meaning.\n\n"
            "Created:\n" + "\n".join(str(path) for path in paths) +
            "\n\nListen: how do interval size, repeated pitch, range, and contour change the character?"
        )
    else:
        paths = run_chapter_06(args.output_directory)
        motif, scores = chapter_06_material()
        transposed, retrograde, inversion = scores[2], scores[4], scores[5]
        _, sections = build_development_study(motif)

        def summary(label: str, events: Sequence[NoteEvent]) -> str:
            pitches = pitches_from_events(events)
            return (
                f"{label}\n"
                f"pitches: {' '.join(pitch_to_name(pitch) for pitch in pitches)}\n"
                f"starts: {' '.join(f'{event.start:.2f}' for event in events)}\n"
                f"durations: {' '.join(f'{event.duration:.2f}' for event in events)}\n"
                f"intervals: {' '.join(f'{value:+d}' for value in interval_sequence(pitches))}"
            )

        structure = "\n".join(
            f"Section {index}: beats {section.start:.1f}–{section.end:.1f}  {section.label}"
            for index, section in enumerate(sections, 1)
        )
        print(
            "Chapter 6 — Motifs and Transformation\n\n"
            "A motif is a short musical idea recognizable enough to repeat, vary, or develop.\n"
            "What has to remain the same for us to recognize it?\n\n"
            + summary("ORIGINAL", motif) + "\n\n"
            + summary("TRANSPOSE +5", transposed) + "\n\n"
            + summary("RETROGRADE", retrograde) + "\n\n"
            + summary("INVERSION AROUND C4", inversion) + "\n\n"
            "AUGMENTATION: starts and durations ×2\n"
            "DIMINUTION: starts and durations ×0.5\n"
            "DISPLACEMENT: internal relationships preserved, onset +0.5 beat\n\n"
            "Transposition preserves intervals and rhythm. Retrograde reflects events in time.\n"
            "Inversion preserves interval magnitudes but reverses signs. Temporal scaling preserves proportions.\n"
            "Every operation returns new immutable events; the original remains unchanged.\n\n"
            "Development study:\n" + structure + "\n\nCreated:\n"
            + "\n".join(str(path) for path in paths)
            + "\n\nHow can repetition remain recognizable without being literal?"
        )
    return 0
