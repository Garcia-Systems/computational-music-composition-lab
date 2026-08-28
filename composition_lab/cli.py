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
from .phrases import (
    build_complete_phrase, build_flat_phrase, build_question, ending_variant,
    phrase_span, place_after,
)
from .chords import (
    MAJOR_TRIAD, MINOR_TRIAD, DIMINISHED_TRIAD, arpeggiate_chord,
    chord_events, diminished_triad, invert_chord, major_triad, minor_triad,
    triad_from_scale_degree, triad_quality,
)
from .progressions import (
    progression_chords, progression_duration, progression_events,
    progression_roman_numerals, progression_starts, repeat_progression,
    root_sequence,
)
from .harmonic_function import (
    abbreviated_functional_path, functional_path, harmonic_function,
)
from .voice_leading import (
    bass_sequence, choose_nearest_inversion, common_pitch_classes,
    extract_voice_lines, inversion_candidates, maximum_voice_motion,
    progression_motion, smooth_progression_voicings, stationary_common_tones,
    voice_movements, within_motion_budget,
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
CHAPTER_07_FILENAMES = (
    "chapter_07_flat_phrase.wav", "chapter_07_shaped_phrase.wav",
    "chapter_07_tonic_ending.wav", "chapter_07_open_ending.wav",
    "chapter_07_short_ending.wav", "chapter_07_long_ending.wav",
    "chapter_07_question.wav", "chapter_07_answer.wav",
    "chapter_07_question_answer.wav", "chapter_07_literal_repeat_pair.wav",
    "chapter_07_answer_pair.wav", "chapter_07_complete_phrase.wav",
    "chapter_07_phrase_pair_capstone.wav",
)
CHAPTER_08_FILENAMES = (
    "chapter_08_c_major.wav", "chapter_08_c_minor.wav",
    "chapter_08_c_diminished.wav", "chapter_08_c_major_root.wav",
    "chapter_08_c_major_first_inversion.wav",
    "chapter_08_c_major_second_inversion.wav",
    "chapter_08_closed_voicing.wav", "chapter_08_open_voicing.wav",
    "chapter_08_block_chord.wav", "chapter_08_broken_chord.wav",
    "chapter_08_c_major_diatonic_triads.wav", "chapter_08_harmony_preview.wav",
)
CHAPTER_09_FILENAMES = (
    "chapter_09_I_IV_V_I.wav",
    "chapter_09_open_progression.wav", "chapter_09_closed_progression.wav",
    "chapter_09_harmonic_rhythm_slow.wav",
    "chapter_09_harmonic_rhythm_medium.wav",
    "chapter_09_harmonic_rhythm_fast.wav",
    "chapter_09_I_IV_V_I_C_major.wav", "chapter_09_I_IV_V_I_F_major.wav",
    "chapter_09_I_IV_V_I_G_major.wav", "chapter_09_I_V_vi_IV.wav",
    "chapter_09_order_a.wav", "chapter_09_order_b.wav",
    "chapter_09_repeated_loop.wav", "chapter_09_harmonic_variation.wav",
    "chapter_09_melody_over_progression_preview.wav",
)
CHAPTER_10_FILENAMES = (
    "chapter_10_functional_arc.wav",
    "chapter_10_IV_predominant.wav", "chapter_10_ii_predominant.wav",
    "chapter_10_V_dominant.wav", "chapter_10_vii_dominant.wav",
    "chapter_10_V_to_I.wav",
    "chapter_10_unresolved_dominant.wav", "chapter_10_resolved_dominant.wav",
    "chapter_10_deceptive_resolution.wav",
    "chapter_10_resolution_tonic.wav", "chapter_10_resolution_deceptive.wav",
    "chapter_10_resolution_none.wav",
    "chapter_10_vi_after_I.wav", "chapter_10_vi_after_V.wav",
    "chapter_10_compact_functional_arc.wav", "chapter_10_expanded_functional_arc.wav",
    "chapter_10_short_dominant.wav", "chapter_10_long_dominant.wav",
    "chapter_10_functional_phrase.wav",
)
CHAPTER_11_FILENAMES = (
    "chapter_11_root_position_transition.wav",
    "chapter_11_smoother_transition.wav",
    "chapter_11_root_position_progression.wav",
    "chapter_11_smooth_progression.wav",
    "chapter_11_low_voice.wav", "chapter_11_middle_voice.wav",
    "chapter_11_high_voice.wav", "chapter_11_common_tones.wav",
    "chapter_11_I_V_vi_IV_smooth.wav", "chapter_11_intentional_leap.wav",
    "chapter_11_phrase_root_position.wav", "chapter_11_phrase_voice_led.wav",
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


def chapter_07_material() -> tuple[tuple[NoteEvent, ...], ...]:
    """Return every deterministic Chapter 7 comparison without rendering."""
    motif = tuple(normalize_events(CHAPTER_06_MOTIF))
    shaped, _ = build_complete_phrase(motif)
    flat = build_flat_phrase(motif)
    tonic, open_ending = ending_variant(), ending_variant(62)
    short, long = ending_variant(final_duration=.5), ending_variant(final_duration=2)
    question, answer = build_question(), build_question(True)
    question_answer = place_after(question, answer, gap=1)
    literal_pair = place_after(question, question, gap=1)
    answer_pair = question_answer
    # Preserve the complete arc while changing the paired endings: A remains
    # open on degree 2; B answers with the long tonic arrival.
    first = list(shaped)
    first[-1] = NoteEvent(62, first[-1].start, 3, 74)
    second = list(shaped)
    second[-1] = NoteEvent(60, second[-1].start, 3, 78)
    capstone = place_after(first, second, gap=2)
    return (
        flat, shaped, tonic, open_ending, short, long, question, answer,
        question_answer, literal_pair, answer_pair, shaped, capstone,
    )


def run_chapter_07(output_directory: Path = Path("outputs")) -> tuple[Path, ...]:
    """Render phrase direction, closure, response, and capstone studies."""
    paths = tuple(output_directory / name for name in CHAPTER_07_FILENAMES)
    for path, score in zip(paths, chapter_07_material(), strict=True):
        write_wav(path, render_events(score, 120))
    return paths


def chapter_08_material() -> tuple[tuple[NoteEvent, ...], ...]:
    """Return controlled chord-quality, voicing, texture, and scale studies."""
    major, minor, diminished = major_triad(60), minor_triad(60), diminished_triad(60)
    root = chord_events(major)
    first = chord_events(invert_chord(major, 1))
    second = chord_events(invert_chord(major, 2))
    closed = chord_events(major)
    open_voicing = chord_events((60, 67, 76))
    block = chord_events(major, duration=1.5)
    broken = arpeggiate_chord(major, note_duration=.5, step=.5)
    diatonic: list[NoteEvent] = []
    for degree in range(1, 8):
        diatonic.extend(chord_events(
            triad_from_scale_degree(60, MAJOR, degree), start=(degree - 1) * 1.5,
            duration=1.0,
        ))
    preview: list[NoteEvent] = []
    for index, pitches in enumerate((major_triad(60), major_triad(65), major_triad(67), major_triad(60))):
        preview.extend(chord_events(pitches, start=index * 2.0, duration=1.75))
    return (
        chord_events(major), chord_events(minor), chord_events(diminished),
        root, first, second, closed, open_voicing, block, broken,
        tuple(diatonic), tuple(preview),
    )


def run_chapter_08(output_directory: Path = Path("outputs")) -> tuple[Path, ...]:
    """Render Chapter 8's deterministic vertical-structure experiments."""
    paths = tuple(output_directory / name for name in CHAPTER_08_FILENAMES)
    for path, score in zip(paths, chapter_08_material(), strict=True):
        write_wav(path, render_events(score, 120))
    return paths


def chapter_09_material() -> tuple[tuple[NoteEvent, ...], ...]:
    """Return progression comparisons while keeping degrees separate from rhythm."""
    basic = (1, 4, 5, 1)
    medium = (2.0,) * 4
    loop = (1, 5, 6, 4)
    repeated_degrees, repeated_durations = repeat_progression(loop, medium, 2)
    chords_for_layer = progression_events(60, MAJOR, basic, medium, velocity=60)
    melody = events_from_degrees(
        (1, 2, 3, 5, 4, 3, 2, 7, 1, 3, 2, 1, 7, 2, 1, 1),
        72, MAJOR, (0.5,) * 16, velocity=90,
    )
    return (
        progression_events(60, MAJOR, basic, medium),
        progression_events(60, MAJOR, (1, 4, 5), (2.0,) * 3),
        progression_events(60, MAJOR, basic, medium),
        progression_events(60, MAJOR, basic, (4.0,) * 4),
        progression_events(60, MAJOR, basic, medium),
        progression_events(60, MAJOR, basic, (1.0,) * 4),
        progression_events(60, MAJOR, basic, medium),
        progression_events(65, MAJOR, basic, medium),
        progression_events(67, MAJOR, basic, medium),
        progression_events(60, MAJOR, loop, medium),
        progression_events(60, MAJOR, loop, medium),
        progression_events(60, MAJOR, (1, 4, 6, 5), medium),
        progression_events(60, MAJOR, repeated_degrees, repeated_durations),
        progression_events(60, MAJOR, (1, 5, 4, 4), medium),
        tuple(chords_for_layer) + tuple(melody),
    )


def run_chapter_09(output_directory: Path = Path("outputs")) -> tuple[Path, ...]:
    """Render Chapter 9's deterministic harmonic-motion experiments."""
    paths = tuple(output_directory / name for name in CHAPTER_09_FILENAMES)
    for path, score in zip(paths, chapter_09_material(), strict=True):
        write_wav(path, render_events(score, 120))
    return paths


def chapter_10_material() -> tuple[tuple[NoteEvent, ...], ...]:
    """Build controlled function, resolution, context, and duration comparisons."""
    def progression(degrees: Sequence[int], durations: Sequence[float] | None = None,
                    velocity: int = 76) -> tuple[NoteEvent, ...]:
        return progression_events(60, MAJOR, degrees, durations or (2.0,) * len(degrees), velocity)

    arc = (1, 4, 5, 1)
    tonic_resolution = (1, 4, 5, 1)
    deceptive = (1, 4, 5, 6)
    phrase_chords = progression(arc, (2.0,) * 4, 58)
    # One simple Chapter-7-shaped melodic line spans the same four regions.
    phrase_melody = events_from_degrees(
        (1, 3, 2, 4, 4, 6, 5, 7, 1), 72, MAJOR,
        (1, 1, 1, 1, 1, 1, 0.5, 0.5, 1), velocity=92,
    )
    return (
        progression(arc),
        progression((1, 4, 5, 1)), progression((1, 2, 5, 1)),
        progression((1, 4, 5, 1)), progression((1, 4, 7, 1)),
        progression((5, 1)),
        progression((1, 4, 5)), progression(tonic_resolution),
        progression((5, 6)),
        progression(tonic_resolution), progression(deceptive), progression((1, 4, 5)),
        progression((1, 6)), progression((5, 6)),
        progression(arc), progression((1, 6, 2, 4, 5, 7, 1)),
        progression(arc, (2, 2, 1, 2)), progression(arc, (2, 2, 4, 2)),
        tuple(phrase_chords) + tuple(phrase_melody),
    )


def run_chapter_10(output_directory: Path = Path("outputs")) -> tuple[Path, ...]:
    """Render Chapter 10's deterministic functional-harmony experiments."""
    paths = tuple(output_directory / name for name in CHAPTER_10_FILENAMES)
    for path, score in zip(paths, chapter_10_material(), strict=True):
        write_wav(path, render_events(score, 120))
    return paths


def _voicing_events(voicings: Sequence[Sequence[int]], duration: float = 2.0,
                    velocity: int = 72) -> tuple[NoteEvent, ...]:
    return tuple(
        NoteEvent(pitch, index * duration, duration, velocity)
        for index, voicing in enumerate(voicings) for pitch in voicing
    )


def chapter_11_material() -> tuple[tuple[NoteEvent, ...], ...]:
    """Build Chapter 11's controlled transitions, voices, and phrase comparisons."""
    primary = progression_chords(60, MAJOR, (1, 4, 5, 1))
    smooth = smooth_progression_voicings(primary)
    second = smooth_progression_voicings(progression_chords(60, MAJOR, (1, 5, 6, 4)))
    common = smooth_progression_voicings(progression_chords(60, MAJOR, (1, 6, 4, 5)))
    lines = extract_voice_lines(smooth)
    voice_scores = tuple(_sequential_events(line) for line in lines)
    phrase_melody = events_from_degrees(
        (1, 3, 2, 4, 4, 6, 5, 7, 1), 72, MAJOR,
        (1, 1, 1, 1, 1, 1, 0.5, 0.5, 1), velocity=92,
    )
    root_phrase = _voicing_events(primary, velocity=54) + tuple(phrase_melody)
    smooth_phrase = _voicing_events(smooth, velocity=54) + tuple(phrase_melody)
    return (
        _voicing_events(primary[:2]), _voicing_events((primary[0], smooth[1])),
        _voicing_events(primary), _voicing_events(smooth),
        *voice_scores, _voicing_events(common), _voicing_events(second),
        _voicing_events((primary[0], primary[1])), root_phrase, smooth_phrase,
    )


def run_chapter_11(output_directory: Path = Path("outputs")) -> tuple[Path, ...]:
    """Render the deterministic Chapter 11 voice-leading experiments."""
    paths = tuple(output_directory / name for name in CHAPTER_11_FILENAMES)
    for path, score in zip(paths, chapter_11_material(), strict=True):
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
        choices=("chapter-00", "chapter-01", "chapter-02", "chapter-03", "chapter-04", "chapter-05", "chapter-06", "chapter-07", "chapter-08", "chapter-09", "chapter-10", "chapter-11"),
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
    elif args.chapter == "chapter-06":
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
    elif args.chapter == "chapter-07":
        paths = run_chapter_07(args.output_directory)
        motif = tuple(normalize_events(CHAPTER_06_MOTIF))
        phrase, sections = build_complete_phrase(motif)
        question, answer = build_question(), build_question(True)
        profile = melodic_profile(pitches_from_events(phrase))
        structure = "\n".join(
            f"{section.label.title()}: beats {section.start:g}–{section.end:g}"
            for section in sections
        )
        print(
            "Chapter 7 — Phrases, Questions, and Closure\n\n"
            "A phrase is a bounded musical thought containing enough internal direction "
            "to feel like a meaningful unit.\n"
            "We now arrange transformed material to create direction over time.\n\n"
            "Roles: OPENING → CONTINUATION → CLIMAX → CLOSING\n"
            "These roles are experimental scaffolding, not universal laws.\n\n"
            f"Motif: {' '.join(pitch_to_name(event.pitch) for event in motif)}\n\n"
            "Complete phrase:\n" + structure + "\n"
            "Continuation: two-note fragments, twice the opening activity\n"
            "Designed climax: C5 at beat 9, velocity 105\n"
            "Closing: descending to tonic, final duration 3 beats\n\n"
            f"Overall range: {profile.range_semitones} semitones; "
            f"average interval: {profile.average_interval_size:.1f} semitones\n"
            "Analysis describes the construction. Listening evaluates the musical effect.\n\n"
            "Flat vs shaped: stable activity/register/velocity versus rising fragments, "
            "high point, and release. Does shaping create a destination?\n"
            f"Question: ends on degree 2 ({pitch_to_name(question[-1].pitch)})\n"
            f"Answer: ends on degree 1 ({pitch_to_name(answer[-1].pitch)})\n"
            "Repetition creates recognition. Variation can create response.\n"
            "Final pitch, final duration, and a real timeline gap are isolated comparisons.\n\n"
            "Phrase behavior differs across classical, blues, jazz, rock, folk, electronic, "
            "non-Western, through-composed, and highly repetitive music.\n\nCreated:\n"
            + "\n".join(str(path) for path in paths)
        )
    elif args.chapter == "chapter-08":
        paths = run_chapter_08(args.output_directory)
        qualities = (
            ("C major", major_triad(60), MAJOR_TRIAD),
            ("C minor", minor_triad(60), MINOR_TRIAD),
            ("C diminished", diminished_triad(60), DIMINISHED_TRIAD),
        )
        inspections = "\n\n".join(
            f"{label}:\n{' '.join(pitch_to_name(p) for p in pitches)}\n"
            f"intervals: {' '.join(map(str, intervals))}"
            for label, pitches, intervals in qualities
        )
        major = major_triad(60)
        inversions = "\n\n".join(
            f"{label}:\n{' '.join(pitch_to_name(p) for p in invert_chord(major, number))}"
            for number, label in enumerate(("root", "first", "second"))
        )
        inventory = "\n".join(
            f"{degree}  {pitch_to_name(triad[0])[:-1]:<2}  "
            f"{' '.join(pitch_to_name(p) for p in triad):<12}  {triad_quality(triad)}"
            for degree in range(1, 8)
            for triad in (triad_from_scale_degree(60, MAJOR, degree),)
        )
        print(
            "Chapter 8 — Chords and Vertical Structure\n\n"
            "A chord is a group of pitches organized to function as one harmonic sonority.\n"
            "Structure + reference pitch = absolute pitches.\n\n" + inspections +
            "\n\nC major inversions:\n\n" + inversions +
            "\n\nROOT defines the chord; BASS is its lowest sounding pitch. "
            "They differ in an inversion. Chord inversion reorders tones; Chapter 6 "
            "melodic inversion reverses interval direction.\n\n"
            "C major diatonic triads:\nDegree  Root  Notes         Quality\n" + inventory +
            "\n\nBlock chords sound together; an arpeggio presents the same tones sequentially.\n"
            "Closed and open voicings retain pitch classes while changing register and spacing.\n\n"
            "Created:\n" + "\n".join(str(path) for path in paths)
        )
    elif args.chapter == "chapter-09":
        paths = run_chapter_09(args.output_directory)
        degrees = (1, 4, 5, 1)
        durations = (2.0,) * 4
        chords = progression_chords(60, MAJOR, degrees)
        romans = progression_roman_numerals(60, MAJOR, degrees)
        starts = progression_starts(durations)
        rows = "\n".join(
            f"{start:>4.1f}–{start + duration:<4.1f}  {degree:<6}  {roman:<5}  "
            f"{pitch_to_name(chord[0])[:-1]:<4}  {' '.join(pitch_to_name(p) for p in chord)}"
            for start, duration, degree, roman, chord in zip(
                starts, durations, degrees, romans, chords, strict=True
            )
        )
        # These key-aware labels prefer B-flat in F major; the pitch module's
        # general chromatic formatter otherwise (correctly) defaults to sharps.
        key_roots = "\n".join((
            "C major: C → F → G → C",
            "F major: F → Bb → C → F",
            "G major: G → C → D → G",
        ))
        print(
            "Chapter 9 — Chord Progressions and Harmonic Motion\n\n"
            "A chord describes vertical pitch organization; a progression describes "
            "harmonic relationships over time.\n"
            "A chord has one identity in isolation and another role among other chords.\n\n"
            "Key: C major\nProgression: " + " ".join(romans) +
            "\nDegrees: " + " ".join(map(str, degrees)) +
            "\nChords:\n" + "\n".join(
                f"{pitch_to_name(chord[0])[:-1]} {triad_quality(chord)}" for chord in chords
            ) +
            "\n\nHarmonic rhythm: 2 beats per chord\n"
            f"Total span: {progression_duration(durations):g} beats\n\n"
            "Start–End  Degree  Roman  Root  Chord\n" + rows +
            "\n\nThe same I IV V I structure in different keys:\n" + key_roots +
            "\n\nHarmonic rhythm comparison: 4, 2, and 1 beat per chord "
            "produce spans of 16, 8, and 4 beats.\n"
            "Root-position bass: " + " → ".join(pitch_to_name(p) for p in root_sequence(60, MAJOR, degrees)) +
            "\nRoot position is inspectable, but its voices may jump farther than necessary; "
            "voice-leading optimization is deliberately deferred.\n\nCreated:\n" +
            "\n".join(str(path) for path in paths)
        )
    elif args.chapter == "chapter-10":
        paths = run_chapter_10(args.output_directory)
        degrees = (1, 4, 5, 1)
        durations = (2.0,) * 4
        romans = progression_roman_numerals(60, MAJOR, degrees)
        chords = progression_chords(60, MAJOR, degrees)
        rows = "\n".join(
            f"{start:>4.1f}   {roman:<5}  {pitch_to_name(chord[0])[:-1]} {triad_quality(chord):<10}  {function}"
            for start, roman, chord, function in zip(
                progression_starts(durations), romans, chords, functional_path(degrees), strict=True
            )
        )
        print(
            "Chapter 10 — Harmonic Function and Tension\n\n"
            "Why does I often feel comparatively stable while V creates stronger expectation?\n"
            "In this introductory major-key model: TONIC suggests stability/arrival; "
            "PREDOMINANT suggests departure/preparation; DOMINANT suggests tension/expectation.\n\n"
            "Key: C major\nProgression: I IV V I\n\n"
            "Start  Roman  Chord       Function\n" + rows +
            "\n\nFunctional path:\n" + " → ".join(abbreviated_functional_path(degrees)) +
            "\nStructural arc: home → departure → tension → return\n\n"
            "Resolution comparison:\nV → I: dominant → tonic\n"
            "V → vi: dominant → tonic-like deceptive destination\nV → stop: unresolved\n\n"
            "IV and ii share a broad predominant region but have different color.\n"
            "V and vii° share a dominant region but create expectation differently.\n"
            "A minor after I and after V keeps its identity while its contextual meaning changes.\n"
            "Holding V for four beats delays arrival; duration affects expectation, not function itself.\n\n"
            "A chord does not contain one universal numeric amount of tension. Function is relational.\n"
            "These labels describe a common tonal model, not emotion, quality, beauty, historical "
            "style, or listener response. Modal, blues-based, chromatic, nonfunctional, pedal-based, "
            "static, planed, quartal, rhythmically driven, and ambiguous harmony need other accounts.\n"
            "Root-position voicings remain intentionally plain; voice leading belongs to Chapter 11.\n\n"
            "Created:\n" + "\n".join(str(path) for path in paths)
        )
    else:
        paths = run_chapter_11(args.output_directory)
        degrees = (1, 4, 5, 1)
        roots = progression_chords(60, MAJOR, degrees)
        smooth = smooth_progression_voicings(roots)
        root_steps, root_total = progression_motion(roots)
        smooth_steps, smooth_total = progression_motion(smooth)
        candidates = inversion_candidates(roots[1])
        selected = choose_nearest_inversion(roots[0], roots[1])

        def notes(voicing: Sequence[int]) -> str:
            return " ".join(pitch_to_name(pitch) for pitch in voicing)

        candidate_rows = "\n".join(
            f"{notes(candidate):<14} movement: "
            f"{' '.join(f'{move:+d}' for move in voice_movements(roots[0], candidate))}  "
            f"total={sum(abs(move) for move in voice_movements(roots[0], candidate))}  "
            f"max={maximum_voice_motion(roots[0], candidate)}"
            for candidate in candidates
        )
        smooth_rows = "\n".join(
            f"{roman}: {notes(voicing)}" + (
                "" if index == 0 else
                f"  movement {' '.join(f'{move:+d}' for move in voice_movements(smooth[index - 1], voicing))}"
            )
            for index, (roman, voicing) in enumerate(zip(
                progression_roman_numerals(60, MAJOR, degrees), smooth, strict=True
            ))
        )
        voice_rows = []
        for label, line in zip(("Low", "Middle", "High"), extract_voice_lines(smooth), strict=True):
            profile = melodic_profile(line)
            intervals = interval_sequence(line)
            voice_rows.append(
                f"{label} voice: {notes(line)}\n"
                f"intervals: {' '.join(f'{value:+d}' for value in intervals)}; "
                f"range={profile.range_semitones}; average={profile.average_interval_size:.1f}; "
                f"maximum leap={max((abs(value) for value in intervals), default=0)}"
            )
        print(
            "Chapter 11 — Voice Leading and Efficient Motion\n\n"
            "A progression names available harmonies; it does not uniquely determine register.\n"
            "Here a voice is one sorted low/middle/high position through equal three-note voicings.\n"
            "Real voice identity can be more nuanced than preserving sorted positions.\n\n"
            "Experiment 1 — I → IV candidate inspector\nPrevious: " + notes(roots[0]) +
            "\nCandidates (inversion × whole-voicing shifts -12/0/+12, range C3–C6):\n" +
            candidate_rows + "\nSelected: " + notes(selected) +
            f"\nWithin five-semitone budget: {'yes' if within_motion_budget(roots[0], selected, 5) else 'no'}\n\n"
            "VOICE LEADING\nProgression: I IV V I\nFunction: " +
            " → ".join(abbreviated_functional_path(degrees)) +
            "\n\nRoot-position voicings:\n" + "\n".join(notes(chord) for chord in roots) +
            f"\nTransition motion: {root_steps}\nTotal motion: {root_total}\n\n"
            "Smoothed voicings:\n" + smooth_rows +
            f"\nTransition motion: {smooth_steps}\nTotal motion: {smooth_total}\n\n" +
            "\n\n".join(voice_rows) +
            "\n\nChord roots: " + " → ".join(pitch_to_name(chord[0]) for chord in roots) +
            "\nActual bass: " + " → ".join(pitch_to_name(pitch) for pitch in bass_sequence(smooth)) +
            "\nHarmonic root motion and sounding bass motion are separate layers.\n\n"
            "I→vi common pitch classes: " + " ".join(
                pitch_to_name(pc + 60)[:-1] for pc in common_pitch_classes(roots[0], progression_chords(60, MAJOR, (6,))[0])
            ) + "\nStationary tones in I→IV selection: " +
            (" ".join(pitch_to_name(p) for p in stationary_common_tones(roots[0], selected)) or "none") +
            "\nG4 and G5 share a pitch class, but only an unchanged absolute pitch in the same voice is stationary.\n\n"
            "Lower motion measures less displacement, not better music. The intentional-leap file "
            "uses the same harmony for registral contrast. The search is greedy and local, not globally optimal.\n"
            "Similar, contrary, and oblique motion are descriptive previews, not counterpoint rules.\n\n"
            "Created:\n" + "\n".join(str(path) for path in paths)
        )
    return 0
