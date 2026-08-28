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
from .rhythm import beats_to_seconds, sequential_starts, write_beat_sequence
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
from .melody_harmony import (
    HarmonicSpan, analyze_melody, chord_tone_duration_percentage,
    chord_tone_percentage, harmonies_during_event, is_chord_tone,
    is_suspension_like,
)
from .groove import (
    GroovePattern, combine_layers, eighth_grid_labels, events_per_beat,
    groove_events, is_offbeat_eighth, is_on_beat, pattern_grid, repeat_groove,
    subdivision_positions,
)
from .bass import (
    bass_chord_role, bass_from_progression,
    connect_bass_targets, harmonic_root_pitch_classes, nearest_bass_pitch,
    root_in_register,
)
from .texture import (
    MusicalLayer, arpeggiate_voicing, arrangement_timeline, attack_density,
    attack_overlap, combine_event_layers, layer_metrics, repeated_chord_events,
)
from .chapter16 import chapter_16_passages, chapter_16_scores
from .chapter17 import BLUES_CHORDS, BLUES_DEGREES, chapter_17_forms
from .forms import form_timeline, section_proportions
from .passages import compare_events, passage_duration, variation_matrix
from .chapter18 import (
    build_chapter_18_study, failure_counts, pitch_constraints,
    rejected_example, render_chapter_18, selected_candidates,
)
from .constraints import (
    candidate_is_valid, evaluate_candidate, find_valid_candidates,
)
from .chapter19 import (
    build_seeded_composition, degrees_to_c_major, generate_valid_random_candidate,
    random_valid_candidate, random_walk_degrees, render_chapter_19, weighted_choice,
)
import random
from collections import Counter

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
CHAPTER_12_FILENAMES = (
    "chapter_12_all_chord_tones.wav",
    "chapter_12_chord_tone_melody.wav", "chapter_12_non_chord_tone_melody.wav",
    "chapter_12_direct_motion.wav", "chapter_12_passing_tone.wav",
    "chapter_12_static_chord_tone.wav", "chapter_12_neighbor_tone.wav",
    "chapter_12_diatonic_approach.wav", "chapter_12_chromatic_approach.wav",
    "chapter_12_without_suspension.wav", "chapter_12_with_suspension.wav",
    "chapter_12_same_melody_harmony_a.wav", "chapter_12_same_melody_harmony_b.wav",
    "chapter_12_same_harmony_melody_a.wav", "chapter_12_same_harmony_melody_b.wav",
    "chapter_12_resolved_nct.wav", "chapter_12_unresolved_nct.wav",
    "chapter_12_phrase_root_position.wav", "chapter_12_phrase_voice_led.wav",
    "chapter_12_melody_harmony_phrase.wav",
)
CHAPTER_13_FILENAMES = (
    "chapter_13_quarter_note_pulse.wav", "chapter_13_eighth_note_pulse.wav",
    "chapter_13_backbeat.wav", "chapter_13_downbeat_accent.wav",
    "chapter_13_backbeat_accent.wav", "chapter_13_onbeat_pattern.wav",
    "chapter_13_offbeat_pattern.wav", "chapter_13_syncopated_pattern.wav",
    "chapter_13_short_offbeat.wav", "chapter_13_tied_offbeat.wav",
    "chapter_13_one_cycle.wav", "chapter_13_four_cycles.wav",
    "chapter_13_pattern_mutation.wav", "chapter_13_accent_mutation.wav",
    "chapter_13_single_layer.wav", "chapter_13_layered_groove.wav",
    "chapter_13_groove_70_bpm.wav", "chapter_13_groove_100_bpm.wav",
    "chapter_13_groove_130_bpm.wav", "chapter_13_phrase_over_groove.wav",
)
CHAPTER_14_FILENAMES = (
    "chapter_14_root_bass.wav", "chapter_14_one_root_per_chord.wav",
    "chapter_14_sustained_roots.wav", "chapter_14_repeated_roots.wav",
    "chapter_14_root_groove.wav", "chapter_14_roots_only.wav",
    "chapter_14_roots_and_fifths.wav", "chapter_14_direct_bass_motion.wav",
    "chapter_14_passing_bass_motion.wav", "chapter_14_diatonic_approach.wav",
    "chapter_14_chromatic_approach.wav", "chapter_14_tonic_pedal.wav",
    "chapter_14_root_motion_vs_pedal.wav", "chapter_14_root_bass_vs_voiced_bass.wav",
    "chapter_14_c_major_root_bass.wav", "chapter_14_c_major_third_bass.wav",
    "chapter_14_c_major_fifth_bass.wav", "chapter_14_straight_bass.wav",
    "chapter_14_syncopated_bass.wav", "chapter_14_root_only_pattern.wav",
    "chapter_14_melodic_bass_pattern.wav", "chapter_14_fixed_register_roots.wav",
    "chapter_14_nearest_register_roots.wav", "chapter_14_static_harmony_static_bass.wav",
    "chapter_14_static_harmony_active_bass.wav", "chapter_14_phrase_bass_shape.wav",
    "chapter_14_bass_in_context.wav",
)
CHAPTER_15_FILENAMES = (
    "chapter_15_register_collision.wav", "chapter_15_register_separation.wav",
    "chapter_15_block_chords.wav", "chapter_15_block_accompaniment.wav",
    "chapter_15_broken_accompaniment.wav", "chapter_15_sustained_chords.wav",
    "chapter_15_repeated_chords.wav", "chapter_15_rhythmic_chords.wav",
    "chapter_15_busy_accompaniment.wav", "chapter_15_sparse_accompaniment.wav",
    "chapter_15_equal_velocity_layers.wav", "chapter_15_role_velocity_layers.wav",
    "chapter_15_melody_only.wav", "chapter_15_melody_bass.wav",
    "chapter_15_melody_bass_harmony.wav", "chapter_15_full_texture.wav",
    "chapter_15_melody_with_accompaniment.wav",
    "chapter_15_parallel_rhythm_texture.wav", "chapter_15_independent_rhythm_texture.wav",
    "chapter_15_low_chord_register.wav", "chapter_15_mid_chord_register.wav",
    "chapter_15_closed_voicing_texture.wav", "chapter_15_open_voicing_texture.wav",
    "chapter_15_root_position_accompaniment.wav", "chapter_15_voice_led_accompaniment.wav",
    "chapter_15_texture_arc.wav", "chapter_15_arrangement_capstone.wav",
)
CHAPTER_16_FILENAMES = tuple(f"chapter_16_{name}.wav" for name in (
    "literal_repetition", "A_A_prime_ending", "pitch_variation", "rhythm_variation",
    "register_variation", "texture_variation", "harmony_variation", "bass_variation",
    "groove_variation", "A_B_contrast", "A_B_A_return", "literal_return", "varied_return",
    "three_repeats_then_variation", "early_variation", "late_variation",
    "contrast_with_motif_link", "texture_continuity", "texture_contrast",
    "return_with_new_texture", "A_A_prime_study", "A_B_study", "A_B_A_study",
    "A_B_A_prime_study", "development_capstone",
))
CHAPTER_17_FILENAMES = tuple(f"chapter_17_{name}.wav" for name in chapter_17_forms())


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


def chapter_12_spans(degrees: Sequence[int] = (1, 4, 5, 1),
                     durations: Sequence[float] = (2.0, 2.0, 2.0, 2.0)) -> tuple[HarmonicSpan, ...]:
    """Adapt the existing degree/chord progression to inspectable harmonic spans."""
    return tuple(
        HarmonicSpan(start, duration, chord, degree)
        for start, duration, chord, degree in zip(
            progression_starts(durations), durations,
            progression_chords(60, MAJOR, degrees), degrees, strict=True)
    )


def _melody(pitches: Sequence[int], starts: Sequence[float] | None = None,
            durations: Sequence[float] | None = None) -> tuple[NoteEvent, ...]:
    starts = starts or tuple(float(i) for i in range(len(pitches)))
    durations = durations or (1.0,) * len(pitches)
    return tuple(NoteEvent(p, s, d, 94) for p, s, d in zip(pitches, starts, durations, strict=True))


def _with_harmony(melody: Sequence[NoteEvent], degrees: Sequence[int] = (1, 4, 5, 1),
                  durations: Sequence[float] = (2.0,) * 4, *, smooth: bool = True) -> tuple[NoteEvent, ...]:
    chords = progression_chords(60, MAJOR, degrees)
    voicings = smooth_progression_voicings(chords) if smooth else chords
    harmony = tuple(
        NoteEvent(pitch, start, duration, 48)
        for start, duration, chord in zip(progression_starts(durations), durations, voicings, strict=True)
        for pitch in chord
    )
    return harmony + tuple(melody)


def chapter_12_material() -> tuple[tuple[NoteEvent, ...], ...]:
    """Build audible controlled comparisons for melody/harmony relationships."""
    all_tones = _melody((64, 67, 65, 69, 67, 71, 64, 60))
    nct = _melody((64, 62, 65, 69, 69, 67, 64, 60))
    direct = _melody((60, 64), (0, 1), (1, 1))
    passing = _melody((60, 62, 64), (0, .5, 1), (.5, .5, 1))
    static = _melody((64, 64), (0, 1), (1, 1))
    neighbor = _melody((64, 65, 64), (0, .5, 1), (.5, .5, 1))
    diatonic = _melody((62, 64), (0, 1), (1, 1))
    chromatic = _melody((63, 64), (0, 1), (1, 1))
    without = _melody((67, 65), (1, 2), (1, 1))
    held = _melody((67, 65), (1, 3), (2, 1))
    fixed = _melody((60, 62, 64, 67), (0, 1, 2, 3), (1,) * 4)
    active = _melody((64, 62, 65, 69, 69, 67, 64, 60))
    resolved = _melody((62, 64), (0, 1), (1, 1))
    unresolved = _melody((62, 65), (0, 1), (1, 1))
    phrase = _melody((60, 64, 62, 64, 65, 69, 68, 67, 64, 60),
                      (0, 1, 2, 2.5, 3, 4, 4.5, 5, 6, 7),
                      (1, 1, .5, .5, 1, .5, .5, 1, 1, 1))
    root_phrase = _with_harmony(phrase, smooth=False)
    voice_led_phrase = _with_harmony(phrase)
    return (
        _with_harmony(all_tones), _with_harmony(all_tones), _with_harmony(nct),
        _with_harmony(direct, (1,), (2,)), _with_harmony(passing, (1,), (2,)),
        _with_harmony(static, (1,), (2,)), _with_harmony(neighbor, (1,), (2,)),
        _with_harmony(diatonic, (1,), (2,)), _with_harmony(chromatic, (1,), (2,)),
        _with_harmony(without, (1, 4), (2, 2)), _with_harmony(held, (1, 4), (2, 2)),
        _with_harmony(fixed, (1, 1), (2, 2)), _with_harmony(fixed, (2, 2), (2, 2)),
        _with_harmony(all_tones), _with_harmony(active),
        _with_harmony(resolved, (1,), (2,)), _with_harmony(unresolved, (1,), (2,)),
        root_phrase, voice_led_phrase, voice_led_phrase,
    )


def run_chapter_12(output_directory: Path = Path("outputs")) -> tuple[Path, ...]:
    """Render Chapter 12's deterministic alignment and context experiments."""
    paths = tuple(output_directory / name for name in CHAPTER_12_FILENAMES)
    for path, score in zip(paths, chapter_12_material(), strict=True):
        write_wav(path, render_events(score, 120))
    return paths


def chapter_13_patterns() -> dict[str, GroovePattern]:
    """Return the small named patterns used by the Chapter 13 comparisons."""
    return {
        "quarters": GroovePattern(4, 2, (0, 2, 4, 6)),
        "eighths": GroovePattern(4, 2, tuple(range(8))),
        "downbeat": GroovePattern(4, 2, tuple(range(8)), (110, 55, 70, 55, 100, 55, 70, 55)),
        "backbeat": GroovePattern(4, 2, tuple(range(8)), (65, 55, 110, 55, 65, 55, 110, 55)),
        "onbeat": GroovePattern(4, 2, (0, 2, 4, 6)),
        "offbeat": GroovePattern(4, 2, (1, 3, 5, 7)),
        "syncopated": GroovePattern(4, 2, (0, 2, 3, 5, 7), (90, 75, 105, 80, 95)),
        "low": GroovePattern(4, 2, (0, 4), (105, 95)),
        "mid": GroovePattern(4, 2, (2, 6), (110, 110)),
        "high": GroovePattern(4, 2, tuple(range(8)), (72, 55, 65, 55, 72, 55, 65, 55)),
    }


def chapter_13_layered_cycle() -> tuple[NoteEvent, ...]:
    """Build LOW/MID/HIGH roles using pitches as deliberately simple timbral proxies."""
    patterns = chapter_13_patterns()
    return combine_layers(groove_events(patterns["low"], 48, note_duration=.16),
                          groove_events(patterns["mid"], 60, note_duration=.12),
                          groove_events(patterns["high"], 72, note_duration=.08))


def chapter_13_material() -> tuple[tuple[NoteEvent, ...], ...]:
    """Build deterministic pulse, syncopation, repetition, layering, and phrase scores."""
    p = chapter_13_patterns()
    quarters = groove_events(p["quarters"], note_duration=.12)
    eighths = groove_events(p["eighths"], note_duration=.12)
    downbeat = groove_events(p["downbeat"], note_duration=.12)
    backbeat = groove_events(p["backbeat"], note_duration=.12)
    onbeat = groove_events(p["onbeat"], note_duration=.14)
    offbeat = groove_events(p["offbeat"], note_duration=.14)
    syncopated = groove_events(p["syncopated"], note_duration=.14)
    short = (NoteEvent(60, 1.5, .2, 100),)
    tied = (NoteEvent(60, 1.5, 1.0, 100),)
    four = repeat_groove(syncopated, 4, 4)
    mutated = repeat_groove(onbeat, 3, 4) + groove_events(
        GroovePattern(4, 2, (0, 2, 3, 4, 6)), start=12, note_duration=.14)
    accent_mutated = repeat_groove(groove_events(p["eighths"], note_duration=.1), 3, 4) + groove_events(
        GroovePattern(4, 2, tuple(range(8)), (90, 90, 90, 90, 90, 90, 90, 120)),
        start=12, note_duration=.1)
    high = groove_events(p["high"], 72, note_duration=.08)
    layered = chapter_13_layered_cycle()
    repeated_layered = repeat_groove(layered, 4, 4)
    phrase = (
        NoteEvent(67, 0, 1, 82), NoteEvent(69, 1, .5, 86), NoteEvent(71, 1.5, .5, 90),
        NoteEvent(72, 2, 1, 98), NoteEvent(69, 3, 1, 84), NoteEvent(67, 4, 1, 82),
        NoteEvent(64, 5, 1, 78), NoteEvent(62, 6, 1, 76), NoteEvent(60, 7, 1, 88),
    )
    phrase_score = repeat_groove(layered, 2, 4) + phrase
    return (quarters, eighths, groove_events(GroovePattern(4, 2, (2, 6), (110, 110)), note_duration=.14),
            downbeat, backbeat, onbeat, offbeat, syncopated, short, tied,
            syncopated, four, mutated, accent_mutated, high, repeated_layered,
            repeated_layered, repeated_layered, repeated_layered, phrase_score)


def run_chapter_13(output_directory: Path = Path("outputs")) -> tuple[Path, ...]:
    """Render Chapter 13 while preserving all structural positions in beats."""
    paths = tuple(output_directory / name for name in CHAPTER_13_FILENAMES)
    bpms = (100,) * 16 + (70, 100, 130, 100)
    for path, score, bpm in zip(paths, chapter_13_material(), bpms, strict=True):
        write_wav(path, render_events(score, bpm))
    return paths


def chapter_14_material() -> tuple[tuple[NoteEvent, ...], ...]:
    """Build controlled bass comparisons without an accompaniment abstraction."""
    basic, loop = (1, 4, 5, 1), (1, 5, 6, 4)
    durations = (4.0,) * 4
    harmony = progression_events(60, MAJOR, basic, durations, 40)
    loop_harmony = progression_events(60, MAJOR, loop, durations, 40)
    sustained = bass_from_progression(60, MAJOR, basic, durations)
    quarters = bass_from_progression(60, MAJOR, basic, durations, GroovePattern(4, 1, (0, 1, 2, 3)))
    groove = GroovePattern(4, 2, (0, 4, 6))
    root_groove = bass_from_progression(60, MAJOR, loop, durations, groove)
    roots_fifths = bass_from_progression(60, MAJOR, basic, durations, GroovePattern(4, 1, (0, 1)), strategy="roots_and_fifths")
    direct = _melody((36, 41), (0, 3), (1, 1))
    passing_pitches = connect_bass_targets(36, 41, tuple((60 + x) % 12 for x in MAJOR))
    passing = _melody(passing_pitches, (0, 1, 2, 3), (1,) * 4)
    diatonic, chromatic = _melody((41, 43)), _melody((42, 43))
    pedal = _melody((36,) * 4, (0, 4, 8, 12), (4,) * 4)
    root_voice = _melody((36, 41, 43, 36), (0, 4, 8, 12), (4,) * 4)
    voiced = _melody((36, 36, 35, 36), (0, 4, 8, 12), (4,) * 4)
    upper_c = chord_events((60, 64, 67), duration=4, velocity=48)
    inversions = tuple(tuple(upper_c) + (NoteEvent(pitch, 0, 4, 88),) for pitch in (36, 40, 43))
    sync_pattern = GroovePattern(4, 2, (0, 2, 3, 5, 7))
    sync = bass_from_progression(60, MAJOR, basic, durations, sync_pattern)
    melodic = bass_from_progression(60, MAJOR, basic, durations, sync_pattern, strategy="roots_and_fifths")
    root_pcs = harmonic_root_pitch_classes(60, MAJOR, loop)
    fixed_pitches = tuple(root_in_register(pc, 36, 47) for pc in root_pcs)
    nearest = [root_in_register(root_pcs[0], 28, 60, 40)]
    for pc in root_pcs[1:]:
        nearest.append(nearest_bass_pitch(pc, nearest[-1], 28, 60))
    fixed = _melody(fixed_pitches, (0, 4, 8, 12), (4,) * 4)
    nearby = _melody(tuple(nearest), (0, 4, 8, 12), (4,) * 4)
    static_harmony = chord_events((60, 64, 67), duration=4, velocity=45)
    static_bass = (NoteEvent(36, 0, 4, 88),)
    active_bass = _melody((36, 43, 48, 43), (0, 1, 2, 3), (1,) * 4)
    phrase_bass = _melody((36, 43, 43, 45, 41, 43, 48, 47, 43, 36),
                           (0, 2, 4, 5, 6, 8, 9, 10, 12, 14),
                           (2, 2, 1, 1, 2, 1, 1, 2, 2, 2))
    context_bass = bass_from_progression(60, MAJOR, loop, durations, sync_pattern,
                                         strategy="roots_and_fifths")
    context_melody = events_from_degrees((1, 3, 5, 3, 7, 5, 6, 5, 4, 3, 2, 1), 72, MAJOR,
                                         (1, 1, 1, 1, 1, 1, 2, 1, 1, 1, 1, 4), velocity=90)
    groove_layer = repeat_groove(groove_events(GroovePattern(4, 2, (2, 6)), 60, note_duration=.1, default_velocity=45), 4, 4)
    context = tuple(loop_harmony) + context_bass + tuple(context_melody) + groove_layer
    return (
        tuple(harmony) + sustained, tuple(harmony) + sustained,
        tuple(harmony) + sustained, tuple(harmony) + quarters,
        tuple(loop_harmony) + root_groove, tuple(harmony) + sustained,
        tuple(harmony) + roots_fifths, direct, passing, diatonic, chromatic,
        tuple(harmony) + pedal, tuple(harmony) + root_voice + pedal,
        tuple(harmony) + root_voice + voiced, *inversions,
        tuple(harmony) + sustained, tuple(harmony) + sync,
        tuple(harmony) + sync, tuple(harmony) + melodic,
        tuple(loop_harmony) + fixed, tuple(loop_harmony) + nearby,
        tuple(static_harmony) + static_bass, tuple(static_harmony) + active_bass,
        phrase_bass, context,
    )


def run_chapter_14(output_directory: Path = Path("outputs")) -> tuple[Path, ...]:
    """Render Chapter 14's deterministic harmony/rhythm/melody bass studies."""
    paths = tuple(output_directory / name for name in CHAPTER_14_FILENAMES)
    for path, score in zip(paths, chapter_14_material(), strict=True):
        write_wav(path, render_events(score, 100))
    return paths


def _with_velocity(events: Sequence[NoteEvent], velocity: int) -> tuple[NoteEvent, ...]:
    return tuple(NoteEvent(e.pitch, e.start, e.duration, velocity) for e in events)


def chapter_15_layers() -> tuple[MusicalLayer, MusicalLayer, MusicalLayer, MusicalLayer]:
    """Build one transparent 16-beat homophonic arrangement by role."""
    degrees, durations = (1, 5, 6, 4), (4.0,) * 4
    melody = events_from_degrees(
        (1, 2, 3, 5, 7, 6, 5, 3, 6, 5, 3, 2, 4, 3, 2, 1),
        72, MAJOR, (1.0,) * 16, velocity=95)
    bass = bass_from_progression(60, MAJOR, degrees, durations,
                                 GroovePattern(4, 1, (0, 2)))
    voiced = smooth_progression_voicings(progression_chords(60, MAJOR, degrees))
    harmony = tuple(event for start, chord in zip((0, 4, 8, 12), voiced, strict=True)
                    for event in chord_events(chord, start, 4, 65))
    groove = repeat_groove(groove_events(
        GroovePattern(4, 2, tuple(range(8)), (70, 55, 60, 55, 70, 55, 60, 55)),
        84, note_duration=.08), 4, 4)
    return (MusicalLayer("melody", tuple(melody)), MusicalLayer("bass", bass),
            MusicalLayer("harmony", harmony), MusicalLayer("groove", groove))


def chapter_15_material() -> tuple[tuple[NoteEvent, ...], ...]:
    """Create controlled Chapter 15 comparisons from shared source material."""
    melody, bass, harmony, groove = chapter_15_layers()
    chords = progression_chords(60, MAJOR, (1, 5, 6, 4))
    voiced = smooth_progression_voicings(chords)
    block = harmony.events
    broken = tuple(event for start, chord in zip((0, 4, 8, 12), voiced, strict=True)
                   for event in arpeggiate_voicing(chord, start, 4, (0, 1, 2, 1), 4, 65))
    repeated = tuple(event for start, chord in zip((0, 4, 8, 12), voiced, strict=True)
                     for event in repeated_chord_events(chord, start, 4, 1, 65))
    rhythmic_steps = (0, 2, 5, 6)
    rhythmic = tuple(NoteEvent(pitch, start + step / 2, .35, 65)
                     for start, chord in zip((0, 4, 8, 12), voiced, strict=True)
                     for step in rhythmic_steps for pitch in chord)
    busy = tuple(event for start, chord in zip((0, 4, 8, 12), voiced, strict=True)
                 for event in repeated_chord_events(chord, start, 4, 2, 65))
    collision_bass = tuple(NoteEvent(e.pitch + 12, e.start, e.duration, e.velocity) for e in bass.events)
    collision_harmony = tuple(NoteEvent(e.pitch - 12, e.start, e.duration, e.velocity) for e in block)
    collision_melody = tuple(NoteEvent(e.pitch - 12, e.start, e.duration, e.velocity) for e in melody.events)
    equal = tuple(_with_velocity(layer.events, 80) for layer in (melody, bass, harmony, groove))
    parallel_melody = tuple(NoteEvent(p, i * 2, 1, 95) for i, p in enumerate((72, 74, 76, 79, 77, 76, 74, 72)))
    parallel_bass = tuple(NoteEvent(p, i * 2, 1, 80) for i, p in enumerate((36, 36, 43, 43, 45, 45, 41, 41)))
    parallel_chords = tuple(NoteEvent(p, start, 1, 65) for start, chord in zip(range(0, 16, 4), chords, strict=True)
                            for beat in (0, 2) for p in chord for start in (start + beat,))
    low = tuple(NoteEvent(e.pitch - 12, e.start, e.duration, e.velocity) for e in block)
    closed = tuple(event for start, chord in zip((0, 4, 8, 12), chords, strict=True)
                   for event in chord_events(chord, start, 4, 65))
    opened_chords = tuple((chord[0], chord[2], chord[1] + 12) for chord in chords)
    opened = tuple(event for start, chord in zip((0, 4, 8, 12), opened_chords, strict=True)
                   for event in chord_events(chord, start, 4, 65))
    root = closed
    full = combine_event_layers(melody, bass, harmony, groove)
    independent = combine_event_layers(melody, bass, MusicalLayer("harmony", broken), groove)
    # Entrances are encoded directly on the timeline: no section/form state machine.
    arc_harmony = tuple(e for e in block if 4 <= e.start < 8) + tuple(e for e in broken if 8 <= e.start < 12) + tuple(e for e in block if e.start >= 12)
    arc_groove = tuple(e for e in groove.events if 8 <= e.start < 12)
    arc = combine_event_layers(melody, bass, arc_harmony, arc_groove)
    # A 24-beat return is only a texture demonstration: material is shifted, not labeled as form.
    capstone = arc + tuple(NoteEvent(e.pitch, e.start + 16, e.duration, e.velocity)
                            for e in combine_event_layers(melody, bass, MusicalLayer("harmony", broken), groove)
                            if e.start < 8)
    return (
        combine_event_layers(collision_melody, collision_bass, collision_harmony, groove), full,
        combine_event_layers(melody, harmony), combine_event_layers(melody, harmony),
        combine_event_layers(melody, broken), combine_event_layers(melody, block),
        combine_event_layers(melody, repeated), combine_event_layers(melody, rhythmic),
        combine_event_layers(melody, busy), combine_event_layers(melody, block),
        combine_event_layers(*equal), full, melody.events,
        combine_event_layers(melody, bass), combine_event_layers(melody, bass, harmony), full,
        full, combine_event_layers(parallel_melody, parallel_bass, parallel_chords, groove), independent,
        combine_event_layers(melody, bass, low), combine_event_layers(melody, bass, harmony),
        combine_event_layers(melody, bass, closed), combine_event_layers(melody, bass, opened),
        combine_event_layers(melody, bass, root), combine_event_layers(melody, bass, harmony),
        arc, capstone,
    )


def run_chapter_15(output_directory: Path = Path("outputs")) -> tuple[Path, ...]:
    """Render deterministic layer, register, activity, and texture comparisons."""
    paths = tuple(output_directory / name for name in CHAPTER_15_FILENAMES)
    for path, score in zip(paths, chapter_15_material(), strict=True):
        write_wav(path, render_events(score, 100))
    return paths


def run_chapter_16(output_directory: Path = Path("outputs")) -> tuple[Path, ...]:
    """Render repetition, controlled variation, contrast, and return studies."""
    paths = tuple(output_directory / name for name in CHAPTER_16_FILENAMES)
    for path, score in zip(paths, chapter_16_scores().values(), strict=True):
        write_wav(path, render_events(score, 108))
    return paths


def run_chapter_17(output_directory: Path = Path("outputs")) -> tuple[Path, ...]:
    """Render named forms and controlled large-scale comparisons."""
    forms = chapter_17_forms()
    paths = tuple(output_directory / name for name in CHAPTER_17_FILENAMES)
    for path, assembly in zip(paths, forms.values(), strict=True):
        write_wav(path, render_events(assembly.events, 120))
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
        choices=("chapter-00", "chapter-01", "chapter-02", "chapter-03", "chapter-04", "chapter-05", "chapter-06", "chapter-07", "chapter-08", "chapter-09", "chapter-10", "chapter-11", "chapter-12", "chapter-13", "chapter-14", "chapter-15", "chapter-16", "chapter-17", "chapter-18", "chapter-19"),
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
    elif args.chapter == "chapter-11":
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
    elif args.chapter == "chapter-12":
        paths = run_chapter_12(args.output_directory)
        spans = chapter_12_spans()
        melody = _melody(
            (60, 62, 64, 65, 64, 67, 69, 67, 71, 64, 60),
            (0, .5, 1, 1.25, 1.5, 2, 2.5, 4, 5, 6, 7),
            (.5, .5, .25, .25, .5, .5, 1.5, 1, 1, 1, 1),
        )
        relations = analyze_melody(melody, spans)
        romans = progression_roman_numerals(60, MAJOR, (1, 4, 5, 1))
        timeline = "\n".join(
            f"{span.start:>3.1f}–{span.end:<3.1f}  {roman:<3}  "
            + " ".join(pitch_to_name(p)[:-1] for p in span.pitches)
            for span, roman in zip(spans, romans, strict=True)
        )
        rows = "\n".join(
            f"{relation.event.start:>4.1f}  {pitch_to_name(relation.event.pitch):<5}  "
            f"{romans[spans.index(relation.harmony)]:<7}  "
            f"{' '.join(pitch_to_name(p)[:-1] for p in relation.harmony.pitches):<11}  "
            f"{relation.relation}"
            for relation in relations
        )
        counts = {name: sum(r.relation == name for r in relations)
                  for name in ("passing", "neighbor", "approach", "other-non-chord-tone")}
        held, resolution = _melody((67, 65), (1, 3), (2, 1))
        crossed = harmonies_during_event(held, chapter_12_spans((1, 4), (2, 2)))
        same_pitch = 64
        print(
            "Chapter 12 — Melody Against Harmony\n\n"
            "Previous chapters could create melody and harmony independently. Now each melody onset "
            "is aligned with the active half-open harmonic span.\n\n"
            "Progression: I IV V I\nStart–End  Chord tones\n" + timeline +
            "\n\nMelody analysis:\nBeat  Pitch  Harmony  Chord tones  Relation\n" + rows +
            f"\n\nChord-tone events: {sum(r.chord_tone for r in relations)} / {len(relations)} "
            f"({chord_tone_percentage(relations):.1f}%)\n"
            f"Chord-tone duration: {chord_tone_duration_percentage(relations):.1f}%\n"
            f"Non-chord-tone events: {sum(not r.chord_tone for r in relations)} / {len(relations)}\n"
            "Relationship types: " + ", ".join(f"{key}: {value}" for key, value in counts.items()) +
            "\nThese percentages measure alignment, not melody quality. A non-chord tone is not "
            "automatically wrong, ugly, or universally dissonant.\n\n"
            "Passing: C4 → D4 → E4 fills a gap in one direction.\n"
            "Neighbor: E4 → F4 → E4 decorates a stable pitch.\n"
            "Approach: D4 (diatonic) or D#4 (chromatic) moves by step to E4.\n"
            "Ambiguous patterns remain other-non-chord-tone. These local names are conservative descriptions.\n\n"
            f"Suspension-like timeline: G4 overlaps {len(crossed)} chords; before change "
            f"{'chord tone' if is_chord_tone(held.pitch, crossed[0].pitches) else 'non-chord tone'}, "
            f"after change {'chord tone' if is_chord_tone(held.pitch, crossed[1].pitches) else 'non-chord tone'}, "
            f"then step-resolution to F4: {'yes' if is_suspension_like(held, resolution, chapter_12_spans((1, 4), (2, 2))) else 'no'}.\n"
            "The pitch does not move at the chord boundary, but its relationship changes. Not every held "
            "non-chord tone is a suspension.\n\n"
            f"Same pitch, different harmony: {pitch_to_name(same_pitch)} over C major is "
            f"{'chord tone' if is_chord_tone(same_pitch, (60, 64, 67)) else 'non-chord tone'}; "
            f"over D minor it is {'chord tone' if is_chord_tone(same_pitch, (62, 65, 69)) else 'non-chord tone'}.\n"
            "The same I–IV–V–I chord identities retain membership under root-position or smooth voicing.\n\n"
            "Function remains another layer: I/tonic, IV/predominant, V/dominant, I/tonic. "
            "Chord identity, voicing, and melodic relationship are distinct.\n\n"
            "This narrow tonal model does not classify appoggiaturas, anticipations, escape tones, pedal "
            "points, extensions, modal or nonfunctional harmony, blues and jazz tensions, or polytonality.\n\n"
            "Created:\n" + "\n".join(str(path) for path in paths)
        )
    elif args.chapter == "chapter-13":
        paths = run_chapter_13(args.output_directory)
        patterns = chapter_13_patterns()
        syncopated = groove_events(patterns["syncopated"])
        onbeats = tuple(event.start for event in syncopated if is_on_beat(event.start))
        offbeats = tuple(event.start for event in syncopated if is_offbeat_eighth(event.start))
        print(
            "Chapter 13 — Groove, Pulse, and Syncopation\n\n"
            "What recurring temporal framework turns a duration list into a pattern?\n"
            "TIME → PULSE → SUBDIVISION → PATTERN → ACCENT → SYNCOPATION → GROOVE\n\n"
            f"Pulse is a recurring temporal reference. At 120 BPM, one beat is {beats_to_seconds(1, 120):g} seconds.\n"
            "Meter model: 4/4\nSubdivision: straight eighth notes\n"
            "Grid:       " + eighth_grid_labels() + "\n"
            "Positions:  " + " ".join(f"{value:g}" for value in subdivision_positions(4, 2)) + "\n"
            "Sixteenths may be labeled 1 e & a, but are not this chapter's primary grid.\n\n"
            "GRID means every available onset; PATTERN means selected positions.\n"
            "Backbeat:   " + pattern_grid(GroovePattern(4, 2, (2, 6))) + "\n"
            "Syncopated: " + pattern_grid(patterns["syncopated"]) + "\n"
            f"Active steps: {', '.join(map(str, patterns['syncopated'].active_steps))}\n"
            f"Velocities: {', '.join(map(str, patterns['syncopated'].velocities or ()))}\n"
            f"On-beat attacks: {onbeats}\nOffbeat attacks: {offbeats}\n"
            f"Density: {events_per_beat(syncopated, 4):.2f} attacks per beat\n\n"
            "Accent is relative emphasis, represented here by velocity independently of onset. "
            "Duration, register, articulation, timbre, density, and context can also create accent.\n"
            "The downbeat/backbeat files keep timing fixed while moving emphasis. Backbeats on 2 and 4 "
            "are characteristic of many rock, pop, blues, funk, and related traditions—not a universal rule.\n\n"
            "Syncopation here is a constructed conflict with expected metric emphasis: offbeat attacks, "
            "an omitted expected beat, or an offbeat duration crossing a beat. It is described, not scored.\n\n"
            "Layered groove (simple pitched proxies, not synthesized drums):\n"
            "      " + eighth_grid_labels() + "\n"
            "LOW   " + pattern_grid(patterns["low"]) + "\n"
            "MID   " + pattern_grid(patterns["mid"]) + "\n"
            "HIGH  " + pattern_grid(patterns["high"]) + "\n\n"
            "Four exact repetitions establish expectation; the mutation files change one final cycle "
            "by onset or accent. Tempo files preserve beat-relative structure at 70, 100, and 130 BPM.\n\n"
            "This deliberately narrow model does not implement swing, shuffle, microtiming, polymeter, "
            "polyrhythm, clave, tuplets, asymmetric meter, rubato, or culturally specific rhythmic systems. "
            "This groove chapter stops before bass-line design; Chapter 14 implements it separately.\n\nCreated:\n" +
            "\n".join(str(path) for path in paths)
        )
    elif args.chapter == "chapter-14":
        paths = run_chapter_14(args.output_directory)
        degrees, durations = (1, 5, 6, 4), (4.0,) * 4
        romans = progression_roman_numerals(60, MAJOR, degrees)
        chords = progression_chords(60, MAJOR, degrees)
        pattern = GroovePattern(4, 2, (0, 2, 3, 5, 7))
        bass = bass_from_progression(60, MAJOR, degrees, durations, pattern,
                                     strategy="roots_and_fifths")
        rows = []
        for event in bass:
            index = min(int(event.start // 4), len(chords) - 1)
            rows.append(f"{event.start:>4.1f}  {pitch_to_name(event.pitch):<5}  "
                        f"{romans[index]:<7}  "
                        f"{bass_chord_role(event.pitch, chords[index], chords[index][0] % 12)}")
        profile = melodic_profile(tuple(event.pitch for event in bass))
        intervals = interval_sequence(tuple(event.pitch for event in bass))
        print(
            "Chapter 14 — Bass as Harmony, Rhythm, and Melody\n\n"
            "How can a bass line connect harmony and groove while remaining melodic?\n"
            "HARMONIC ROOT → BASS PITCH → RHYTHMIC PLACEMENT → BASS LINE\n\n"
            "Progression: I V vi IV\nBass strategy: roots + fifths\n"
            "Beat  Bass   Harmony  Role\n" + "\n".join(rows) +
            "\n\nGroove: " + pattern_grid(pattern) +
            f"\nBass density: {events_per_beat(bass, 16):.2f} attacks per beat\n"
            f"Intervals: {' '.join(f'{value:+d}' for value in intervals)}\n"
            f"Bass melodic profile: range={profile.range_semitones}; "
            f"average interval={profile.average_interval_size:.2f}; "
            f"largest leap={max((abs(value) for value in intervals), default=0)}; "
            f"repeated notes={profile.repeats}\n\n"
            "The root is an obvious option, not the only option. Harmonic root is metadata; "
            "it is not necessarily the lowest current voicing pitch. Root/fifth choices, "
            "C–D–E–F passing motion, F/F# approaches to G, and a tonic pedal are controlled "
            "possibilities rather than quality rankings. A C pedal is root under I but a "
            "non-chord tone under V; that intentional relationship is not automatically an error.\n"
            "Fixed-octave roots and nearest-register roots create different contours; minimum "
            "motion is not always preferable. Harmonic rhythm names chord changes, while bass "
            "rhythm names bass attacks. Locking means related positions, not mandatory unison.\n\n"
            "Reader experiments: replace a root with a fifth; double or remove attacks; add a "
            "passing or chromatic approach note; hold C as a pedal; change octave; force nearest "
            "roots; syncopate one onset; finally listen to bass alone. Does its contour cohere?\n\n"
            "This narrow triadic, regular-grid, monophonic model stops before accompaniment and "
            "texture. Walking bass, ostinatos, riffs, drones, slap, chromatic and contrapuntal "
            "lines, figured bass, extended harmony, and style-specific articulation remain outside it.\n\n"
            "Created:\n" + "\n".join(str(path) for path in paths)
        )
    elif args.chapter == "chapter-15":
        paths = run_chapter_15(args.output_directory)
        melody, bass, harmony, groove = chapter_15_layers()
        broken = arpeggiate_voicing((60, 64, 67), 0, 4, (0, 1, 2, 1), 4, 65)
        shared, distinct = attack_overlap(melody.events, harmony.events)
        metrics = "\n".join(
            f"{layer.name.title():<8} events={layer_metrics(layer)['events']:<3} "
            f"range={layer_metrics(layer)['register']} "
            f"density={layer_metrics(layer)['attacks_per_beat']:.2f} attacks/beat "
            f"average velocity={layer_metrics(layer)['average_velocity']:.1f}"
            for layer in (melody, bass, harmony, groove))
        print(
            "Chapter 15 — Accompaniment and Texture\n\n"
            "Once melody, harmony, groove, and bass exist, how can each layer have a clear role?\n"
            "MUSICAL MATERIAL → LAYER → REGISTER → RHYTHMIC ACTIVITY → TEXTURE → ARRANGEMENT\n\n"
            "Texture describes how simultaneous musical layers are distributed and how independently they behave.\n"
            "THIN means fewer active layers; THICK means more; ACTIVE means many attacks and moving parts. "
            "None is automatically better or louder. Roles are not instruments: one piano can perform several.\n\n"
            "Register plan (pedagogical, not universal):\nbass: C2–C3\nharmony: C3–C5\nmelody: C4–C6\n\n"
            "Layer inspector:\n" + metrics +
            "\n\nBlock accompaniment: chord tones share an onset at each harmonic change.\n"
            "Broken accompaniment: CHORD + pattern 0 1 2 1 → timed notes " +
            " ".join(f"{pitch_to_name(e.pitch)}@{e.start:g}" for e in broken) +
            "\nHarmonic rhythm changes chord identity; accompaniment rhythm re-attacks it. "
            "The same four-beat C harmony can have one or eight accompaniment attacks.\n"
            f"Busy density: 2.00; sparse density: 0.25 attacks/beat. "
            f"Melody/harmony shared attacks: {shared} of {distinct} distinct positions.\n\n"
            "If every layer is equally active, what is the listener supposed to focus on? "
            "Foreground/background can be shaped here through activity, register, and velocity. "
            "The 95/80/65/55–75 role hierarchy is a demonstration, not a mixing recipe. "
            "Compositional velocity remains event data; the renderer independently peak-normalizes only if the sum clips.\n\n"
            "Layer timeline:\n" + arrangement_timeline((melody, bass, harmony, groove), (0, 4, 8, 12, 16)) +
            "\n\nThe texture arc uses event entrances and behavior changes, not a formal-section system. "
            "How much clarity comes from register alone? Can sustained harmony support without continual attacks? "
            "What changes when rhythms are parallel rather than complementary?\n\n"
            "Reader experiments: remove chords; remove bass; raise chords an octave; align every attack; "
            "halve chord attacks; switch blocks to arpeggios; change open/closed voicing; delay groove; "
            "thin the climax; and render each role alone before combining it. Does each layer have a clear job?\n\n"
            "This simplified model stops at triads, monophonic bass, a pitched groove proxy, deterministic patterns, "
            "register, density, and timeline entrances. Polyphony, heterophony, contrapuntal independence, orchestration, "
            "doubling, call and response, countermelodies, timbral layering, unison, and spatial arrangement are acknowledged, "
            "not implemented. Chapter 16 repetition/contrast/form structures are deliberately absent.\n\nCreated:\n" +
            "\n".join(str(path) for path in paths))
    elif args.chapter == "chapter-16":
        paths = run_chapter_16(args.output_directory)
        p = chapter_16_passages()
        ending = compare_events(p["A"].events, p["A_ending"].events)
        matrix = variation_matrix((("A'", ("pitch",)), ("B", ("pitch", "rhythm", "harmony", "bass", "texture", "register")), ("A''", ("pitch", "texture"))))
        print(
            "Chapter 16 — Repetition, Contrast, and Variation\n\n"
            "How can a composer repeat enough material to create identity while changing enough to create direction?\n"
            "IDEA → REPETITION → VARIATION → CONTRAST → RETURN → DEVELOPMENT\n\n"
            "Original passage: A (8 beats)\nLiteral repetition: A A\n"
            "Repetition creates recognition, memory, expectation, and reinforcement; it is not inherently boring.\n\n"
            "A' is a compositional label—not a special data type—meaning A changed in some way.\n"
            f"A/A' ending facts: pitches equal={ending.pitch_sequence_equal}; onsets equal={ending.onset_sequence_equal}; durations equal={ending.duration_sequence_equal}.\n"
            "How much can the ending change while the phrase remains related?\n\n"
            "One-variable laboratory:\npitch: rhythm retained\nrhythm: pitch sequence retained\ntexture: core melody/harmony retained\n"
            "harmony: diatonic IV becomes ii\nbass: roots become melodic\ngroove: one offbeat added\nregister: melody raised an octave.\n"
            "Variation need not happen inside melody: any layer can carry it.\n\n"
            "Contrast: A B\nB deliberately uses leaps, faster activity, high register, changed harmony, bass, and thick texture. "
            "Its opening G–A–B–D transposes A's C–D–E–G motif, preserving family resemblance beneath contrast.\n\n"
            "Return timeline:\nBeats     0–8    8–16   16–24\nLabel       A      B       A\nRelation original contrast return\n"
            "Compare literal A B A with A B A': context can change perception even when return events do not.\n\n"
            "Variation matrix (X = changed; . = retained):\n" + matrix + "\n\n"
            f"Development inspector:\nA    {passage_duration(p['A_thin']):g} beats; original\n"
            f"A'   {passage_duration(p['A_rhythm']):g} beats; rhythm changed\n"
            f"B    {passage_duration(p['B_thick']):g} beats; pitch, contour, rhythm, harmony, bass, register, texture changed\n"
            f"A''  {passage_duration(p['A_double']):g} beats; return with fuller texture and changed ending\n"
            "Development: A A' B A'' (32 beats)\n\n"
            "Code reuse avoids duplicate implementation; musical repetition deliberately repeats audible material. "
            "Three identical A passages establish expectation before a fourth mutation; compare early and late placement.\n\n"
            "Reader experiments: alter only final note, rhythm, or texture; transpose one fragment; construct contrasting B; preserve motif or groove; "
            "return literally or differently; mutate repetition four; make A' so large you must ask when it feels like B.\n\n"
            "This limited study acknowledges thematic transformation, fragmentation, saturation, sequence, augmentation/diminution, reharmonization, "
            "counterpoint, orchestration, and developmental harmony. It adds no recognizability score, randomness, named form, or form engine. "
            "Chapter 17 will organize these patterns into named forms.\n\nCreated:\n" + "\n".join(str(path) for path in paths))
    elif args.chapter == "chapter-17":
        paths = run_chapter_17(args.output_directory)
        forms = chapter_17_forms()
        binary, ternary, capstone = forms["binary_form"], forms["ternary_form"], forms["form_capstone"]
        blues_rows = "\n".join(
            f"{bar:<4} {('C' if degree == 'I' else 'F' if degree == 'IV' else 'G'):<5} {degree}"
            for bar, degree in enumerate(BLUES_DEGREES, 1)
        )
        cap_relations = ("original", "varied repeat", "contrast", "varied return")
        cap_rows = "\n".join(
            f"{display:<8} {p.start:>5g} {p.end:>5g}  {relation}"
            for display, p, relation in zip(("A", "A'", "B", "A''"), capstone.placements, cap_relations, strict=True)
        )
        proportions = "  ".join(
            f"{label} {percent:.0f}%" for label, percent in section_proportions(capstone)
        ).replace("B_capstone", "B")
        print(
            "Chapter 17 — Musical Form\n\n"
            "How can repetition, contrast, and return be organized into larger musical structures?\n"
            "PASSAGE → SECTION → SECTION RELATIONSHIPS → FORM → LARGE-SCALE MUSICAL SHAPE\n\n"
            "A Section stores a label separately from locally normalized immutable NoteEvents. A form plan is only a template; "
            "FORM PLAN + SECTIONS → MUSICAL TIMELINE. Labels describe roles and do not generate musical behavior.\n\n"
            "Binary:\nA B\nFORM: A B\n" + form_timeline(binary) +
            "\nBinary can contain internal repeats and tonal relationships beyond this executable two-block model.\n\n"
            "Ternary:\nA B A\nA establishes identity, B contrasts, and A literally returns.\n"
            "What does the return change about the large-scale sense of closure?\n\n"
            "AABA:\nA A B A\nVaried AABA:\nA A' B A''\n"
            "A' changes texture; A'' changes ending and texture. Repetition and variation can coexist.\n\n"
            "Verse/Chorus:\nVerse Chorus Verse Chorus\n"
            "Here the verse is thinner/lower and chorus thicker/higher as experimental choices, not universal rules. "
            "Section roles make these labels more informative than merely A/B.\n\n"
            "12-Bar Blues (simplified triadic approximation):\nI I I I\nIV IV I I\nV IV I I\n\n"
            "Bar  Chord Degree\n" + blues_rows +
            "\nThe 48-beat harmonic cycle uses one chord per four-beat bar, straight eighth-note groove, root/fifth bass, and motif melody. "
            "A second chorus retains harmony while varying surface melody; this does not capture the blues' full stylistic richness.\n\n"
            "Through-Composed:\nA B C D\nSuccessive sections introduce distinct material, without implying that motifs never repeat. "
            "Compare A B A with A B C: what changes when known material returns versus new material?\n\n"
            "FORM CAPSTONE\nSection  Start   End  Relation\n" + cap_rows +
            f"\nTotal beats: {capstone.duration:g}\nSection proportions: {proportions}\n"
            "Active layers: A 2; A' 4; B 5; A'' 4\n"
            "0        8        16                32       40\n"
            "|--- A ---|--- A' ---|------ B ------|--- A'' ---|\n\n"
            "Formal comparison (actual study durations):\n"
            "Binary A B: 16; Ternary A B A: 24; AABA A A B A: 32; Verse/Chorus V C V C: 32; "
            "12-bar blues: 48; Through-composed A B C D: 32 beats.\n\n"
            "Immediate and one-beat-gap transitions ask how silence marks boundaries. Symmetric 8+8+8 and asymmetric 8+12+8 "
            "studies ask how duration changes pacing. Texture, register, and harmony are compositional markers, not automatic formal rules.\n\n"
            "Reader experiments: turn A B into A B A; vary the return; shorten or lengthen B; repeat A A B B; make AABA; "
            "change only verse/chorus texture; repeat blues and vary melody; replace a return with C; remove texture differences. "
            "Are boundaries still obvious?\n\n"
            "These simplified models do not implement rounded binary, compound ternary, strophic, rondo, sonata, variation, developmental, "
            "hybrid, or ambiguous forms. No parser, form detector, random plan, constraint solver, candidate search, or Chapter 18 system is added.\n\n"
            "Created:\n" + "\n".join(str(path) for path in paths))
    elif args.chapter == "chapter-18":
        study = build_chapter_18_study()
        paths = render_chapter_18(args.output_directory)
        funnel = "\n↓\n".join(f"{name:<30} {count:>7,}" for name, count in study.pitch_funnel)
        impossible = "\n↓\n".join(f"{name:<30} {count:>7,}" for name, count in study.impossible_funnel)
        failures = "\n".join(f"{name:<24} {count:>4}" for name, count in failure_counts(study.pitch_search))
        rejected = rejected_example(study)
        rejection_rows = "\n".join(
            f"{result.name:<22} {'PASS' if result.passed else 'FAIL'}  {result.detail}"
            for result in rejected.results
        )
        sensitivity = []
        for threshold in (2, 4, 7, 12):
            sensitivity.append((threshold, len(find_valid_candidates(
                study.pitch_candidates, pitch_constraints(threshold)).valid)))
        sensitivity_rows = "\n".join(f"{limit:<9} {count}" for limit, count in sensitivity)
        manual = {"A": (60, 62, 64, 60), "B": (60, 66, 67, 60),
                  "C": (60, 67, 62, 60), "D": (60, 62, 64, 67)}
        manual_rows = ["Candidate Range Scale Leap Start End Valid"]
        for label, candidate in manual.items():
            results = evaluate_candidate(candidate, pitch_constraints())
            # omit fixed length and no-repeat columns in this introductory table
            shown = (results[1], results[2], results[5], results[3], results[4])
            manual_rows.append(
                f"{label:<9} " + " ".join(f"{'PASS' if r.passed else 'FAIL':<5}" for r in shown) +
                f" {'YES' if candidate_is_valid(results) else 'NO'}")
        profiles = []
        for label, candidate in zip("ABC", selected_candidates(study.capstone_candidates), strict=True):
            profile = melodic_profile(candidate)
            profiles.append(
                f"Candidate {label}\n"
                f"pitches: {candidate}\n"
                f"names: {' '.join(pitch_to_name(p) for p in candidate)}\n"
                f"intervals: {_intervals(candidate)}\n"
                f"range: {profile.range_semitones}; steps: {profile.steps}; leaps: {profile.leaps}; "
                f"stepwise: {profile.stepwise_percentage:.1f}%; ending: {pitch_to_name(candidate[-1])}"
            )
        cap_funnel = "\n↓\n".join(f"{name:<30} {count:>7,}" for name, count in study.capstone_funnel)
        print(
            "Chapter 18 — Constraint-Based Composition\n\n"
            "If we specify musical rules and limits, how can a computer generate candidates without pretending the rules define good music?\n"
            "MUSICAL GOAL → CONSTRAINT → CANDIDATE → VALIDATION → SEARCH → VALID SOLUTION SET → HUMAN CHOICE\n\n"
            "OBJECTIVE CONSTRAINT\n“All pitches must remain between C4 and C5.” This can be checked exactly.\n\n"
            "SUBJECTIVE JUDGMENT\n“The melody should be beautiful.” This cannot honestly become a simple boolean rule.\n\n"
            "A candidate begins as an immutable pitch tuple such as (60, 62, 64, 67); only accepted candidates later become timed NoteEvents.\n\n"
            "Manual candidate comparison (failures are facts about this rule set):\n" +
            "\n".join(manual_rows) + "\n\n"
            f"Search space: 5 possible pitches ^ 4 positions = {len(study.pitch_candidates)} candidates\n"
            "Enumeration order: lexicographic and reproducible.\n\nConstraint funnel:\n" + funnel +
            f"\n\nValid: {len(study.pitch_search.valid)}\nRejected: {len(study.pitch_search.rejected)}\n"
            "Passing the same constraints does not make two melodies equivalent. First/middle/last selection below is an implementation choice, not artistic judgment.\n\n"
            "Failure reasons (overlapping counts; a candidate may fail several rules):\n" + failures +
            f"\n\nRejected candidate: {rejected.candidate}\n" + rejection_rows +
            "\n\nConstraint sensitivity:\nThreshold Valid candidates\n" + sensitivity_rows +
            "\n\nUnsatisfiable constraints:\n" + impossible +
            "\nSEARCH RESULT:\n0 valid candidates\n"
            "Zero results does not mean the program failed; rules may be mutually incompatible or too restrictive.\n\n"
            f"Rhythm search: generated {3 ** 4} four-attack rhythms; {len(study.rhythm_candidates)} total exactly 4 beats with at most one 2-beat note.\n"
            "Pitch and rhythm searches remain separate; three rhythms use the same pitch sequence.\n\n"
            "Harmony-aware filtering: integer-beat onsets are checked against the active I–IV–V–I chord. "
            "One failing and one passing melody are rendered; this is an experimental rule, not a universal melodic law.\n\n"
            f"Capstone search: 7 pitches ^ 6 positions = {7 ** 6:,}\n" + cap_funnel +
            f"\nFinal valid capstone candidates: {len(study.capstone_candidates)}\n\n" +
            "\n\n".join(profiles) +
            "\n\nAll three satisfy the same rules. Which would you keep, alter, combine, or reject after listening?\n\n"
            "CONSTRAINTS do not produce one correct melody; they define a set of permitted melodies.\n"
            "COMPUTER searches systematically; HUMAN chooses rules, listens, judges, edits, and revises.\n"
            "The rules do not assert that scale membership, small leaps, tonic endings, steps, repeats, or chord tones make good music.\n\n"
            "Search-space growth: 5^4 = 625; 7^8 = 5,764,801; "
            f"12^16 = {12 ** 16:,}. This chapter refuses impractical exhaustive searches rather than solving that later problem.\n\n"
            "Recipe: define space; define objective rules; enumerate; evaluate; retain; inspect rejection; listen; revise.\n\n"
            "Reader experiments: change range; tighten leap 7/5/2; remove tonic ending; require a repeat or motif; use natural minor; "
            "change rhythm; add chord-tone rules; create an impossible set; listen to five legal candidates. "
            "What artistic criteria did you use that the program did not know about?\n\n"
            "No randomness, probability, quality score, optimization, or Chapter 19 behavior is used.\n\nCreated:\n" +
            "\n".join(str(path) for path in paths)
        )
    else:
        study = build_chapter_18_study()
        paths = render_chapter_19(args.output_directory)
        repeated_a = tuple(random_valid_candidate(study.pitch_search.valid, random.Random(42))
                           for _ in range(4))
        repeated_b = tuple(random_valid_candidate(study.pitch_search.valid, random.Random(42))
                           for _ in range(4))
        frequencies = Counter(random_valid_candidate(tuple((letter,) for letter in "ABCDE"),
                                                      random.Random(1900 + draw))[0]
                              for draw in range(100))
        pitch_rng = random.Random(10)
        uniform = Counter(pitch_rng.choice("CDEFGAB") for _ in range(100))
        weighted_rng = random.Random(10)
        weighted = Counter(weighted_choice(tuple("CDEFGAB"), (4, 1, 2, 1, 3, 1, 1),
                                           weighted_rng) for _ in range(100))
        rejection = generate_valid_random_candidate(
            lambda rng: tuple(rng.choice((60, 62, 64, 65, 67)) for _ in range(4)),
            (lambda candidate: candidate_is_valid(evaluate_candidate(candidate, pitch_constraints())),),
            random.Random(90), 1000)
        walk = random_walk_degrees(1, 12, (-2, -1, 1, 2), 1, 8, random.Random(91))
        walk_pitches = degrees_to_c_major(walk)
        capstone = build_seeded_composition(2026)
        alternate = build_seeded_composition(2027)
        print(
            "Chapter 19 — Controlled Randomness\n\n"
            "If many valid musical possibilities exist, how can randomness help us explore them while preserving reproducibility and compositional control?\n"
            "VALID POSSIBILITY SPACE → RANDOM CHOICE → SEED → BOUNDED RANDOMNESS → WEIGHTED CHOICE → RANDOM WALK → CONSTRAINT-AWARE GENERATION\n\n"
            "The constraint system decides what is allowed. Randomness decides which allowed possibility we explore. Randomness helps explore alternatives that satisfy a compositional system; it is not a quality judgment or a theory of creativity.\n\n"
            "Python's random generator is pseudo-random. Given the same algorithm, initial state, and seed, it produces the same sequence of choices. Explicit random.Random instances keep state local.\n"
            f"Seed 42: {repeated_a}\nSeed 42 again: {repeated_b}\nStructurally identical: {'PASS' if repeated_a == repeated_b else 'FAIL'}\n"
            "Seeds 10, 20, and 30 render the same constrained experiment with only seed changed.\n\n"
            "UNIFORM SAMPLE (100 draws; small counts need not be equal)\nCandidate  Count\n" +
            "\n".join(f"{key:<9} {frequencies[key]}" for key in "ABCDE") +
            "\n\nChoice Weight Uniform-count Weighted-count\n" +
            "\n".join(f"{pitch:<6} {weight:<6} {uniform[pitch]:<13} {weighted[pitch]}"
                      for pitch, weight in zip("CDEFGAB", (4, 1, 2, 1, 3, 1, 1), strict=True)) +
            "\nA CONSTRAINT forbids or requires; a WEIGHT changes likelihood. C and G are more likely here, not mandatory or optimal.\n\n"
            "Independent RNG streams isolate pitch, rhythm, bass, motif, and texture so an added rhythm draw does not move the pitch stream. Every stream is derived reproducibly from one master seed.\n\n"
            f"REJECTION SAMPLING\nattempts: {rejection.attempts}\nrejected: {rejection.rejected}\naccepted: {int(rejection.candidate is not None)}\n"
            "Enumeration gives complete knowledge for a small space; rejection sampling avoids enumeration but can waste proposals when solutions are rare. Both terminate explicitly.\n\n"
            f"RANDOM WALK\nStart degree: 1\nAllowed steps: -2 -1 +1 +2\nDegrees: {' '.join(map(str, walk))}\nPitches: {' '.join(pitch_to_name(p) for p in walk_pitches)}\n"
            "Only currently valid moves are selected at boundaries. Weighted walks alter local likelihood without guaranteeing contour.\n\n"
            "Bounded velocity uses base 80 plus an integer offset from -5 through +5, clamped to MIDI range. This is bounded velocity variation, not realistic humanization. Bass keeps every chord-change event on the root; later events choose root/fifth with 4:1 weights. Form A A' B A stays deterministic.\n\n"
            f"RANDOMNESS INSPECTOR\nMaster seed: {capstone.manifest.master}\nSubsystem seeds: melody={capstone.manifest.melody} rhythm={capstone.manifest.rhythm} bass={capstone.manifest.bass} motif={capstone.manifest.motif} texture={capstone.manifest.texture}\n"
            "Fixed: key C major; form A A' B A; harmony; tempo; constraints\nRandomized: melody candidate; rhythm candidate; bass choices; motif variation; texture\nDecisions:\n" +
            "\n".join(capstone.decisions) +
            f"\nConstraint validation: {'PASS' if capstone.valid else 'FAIL'}\nAlternate master seed: {alternate.manifest.master}\nAlternate decisions:\n" +
            "\n".join(alternate.decisions) +
            "\n\nFORM, HARMONY, and CONSTRAINTS can remain deterministic while RANDOMNESS explores local choices. A probability of 25% does not guarantee exactly one mutation in four trials; use deterministic form when a count is required.\n\n"
            "Recipe: fix context; fix invariants; name variable dimensions; define valid choices; optionally assign weights; set and print a seed; generate; validate; log; listen; change one parameter; compare.\n\n"
            "Search strategies: EXHAUSTIVE SEARCH enumerates; RANDOM VALID SELECTION samples a known valid set; REJECTION SAMPLING rejects proposals; RANDOM WALK produces locally related sequences. None is universally preferable.\n\n"
            "Reader experiments: try seeds 1/2/3/100/2026; remove the seed and observe lost replay; change tonic weight; weight walk steps; add step 0; narrow transpositions; try mutation probabilities .10/.50/.90; tighten constraints; hold melody seed while changing rhythm seed; listen to several seeds and ask what you heard that the generator did not understand.\n\n"
            "This chapter specifies simple probabilities directly. It does not implement stochastic-process theory, noise, cellular automata, chaos, grammars, evolutionary systems, learned models, Markov chains, machine learning, an AI composer, SuperCollider, OSC, or Chapter 20 musical memory.\n\nCreated:\n" +
            "\n".join(str(path) for path in paths)
        )
    return 0
