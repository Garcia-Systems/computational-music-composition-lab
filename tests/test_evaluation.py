import random

import pytest

from composition_lab.chapter20 import TRAINING_PHRASES
from composition_lab.chapter21 import CHAPTER_21_FILENAMES, seed_sweep
from composition_lab.evaluation import (constraint_pass_profile, count_ngrams,
    exact_copy, generation_profile, harmonic_alignment_profile, melody_profile,
    ngram_overlap, rhythm_profile, transition_coverage)
from composition_lab.events import NoteEvent, transpose_events
from composition_lab.markov import build_transition_counts_from_sequences, generate_markov_sequence
from composition_lab.melody_harmony import HarmonicSpan


def test_empty_and_one_note_profiles():
    empty, one = melody_profile(()), melody_profile((60,))
    assert empty.lowest_pitch is None and empty.average_absolute_interval is None
    assert one.pitch_range == 0 and one.maximum_leap is None
    assert one.unique_pitches == one.unique_pitch_classes == 1


def test_melody_measurements_and_transposition_invariants():
    original = melody_profile((60, 62, 64, 67))
    shifted = melody_profile((72, 74, 76, 79))
    assert original.intervals == shifted.intervals == (2, 2, 3)
    assert original.pitch_range == shifted.pitch_range == 7
    assert original.average_absolute_interval == shifted.average_absolute_interval == pytest.approx(7 / 3)
    assert original.maximum_leap == shifted.maximum_leap == 3
    assert shifted.lowest_pitch - original.lowest_pitch == 12


def test_direction_distribution_and_pitch_class_diversity():
    profile = melody_profile((60, 62, 62, 59, 72))
    assert (profile.ascending, profile.descending, profile.repeat_count) == (2, 1, 1)
    assert profile.interval_distribution == {0: 1, 2: 1, 3: 1, 13: 1}
    assert profile.unique_pitches == 4 and profile.unique_pitch_classes == 3


def test_rhythm_profile_and_pitch_invariance():
    a = (NoteEvent(60, 0, 1), NoteEvent(62, 1, 1))
    b = (NoteEvent(60, 0, .5), NoteEvent(62, .5, .5))
    assert melody_profile(tuple(e.pitch for e in a)).intervals == melody_profile(tuple(e.pitch for e in b)).intervals
    assert rhythm_profile(a).attacks_per_beat == 1
    assert rhythm_profile(b).attacks_per_beat == 2
    assert rhythm_profile(b).duration_distribution == {.5: 2}


def test_ngram_counts_overlap_and_copy():
    sequence = (1, 2, 3, 1, 2, 3)
    assert count_ngrams(sequence, 2) == {(1, 2): 2, (2, 3): 2, (3, 1): 1}
    assert count_ngrams(sequence, 3) == {(1, 2, 3): 2, (2, 3, 1): 1, (3, 1, 2): 1}
    assert ngram_overlap((1, 2, 4), (1, 2, 3), 2)["overlap_fraction"] == .5
    assert exact_copy(sequence, sequence)


def test_harmonic_alignment_and_strong_beats():
    span = (HarmonicSpan(0, 4, (60, 64, 67)),)
    tones = tuple(NoteEvent(p, i, 1) for i, p in enumerate((60, 64, 67)))
    others = tuple(NoteEvent(p, i, 1) for i, p in enumerate((62, 65, 69)))
    assert harmonic_alignment_profile(tones, span)["chord_tone_fraction"] == 1
    assert harmonic_alignment_profile(others, span)["chord_tone_fraction"] == 0
    assert harmonic_alignment_profile(tones, span)["strong_beat_chord_tone_fraction"] == 1


def test_constraint_pass_rate_and_diversity():
    assert constraint_pass_profile((1, 2, 3, 4), lambda x: x < 4)["pass_rate"] == .75
    assert generation_profile(((1,), (1,), (2,), (3,), (3,))) == {
        "total": 5, "unique": 3, "duplicate_outputs": 2, "unique_ratio": .6}


def test_markov_transition_coverage_and_seed_sweep():
    model = build_transition_counts_from_sequences(TRAINING_PHRASES, cyclic=True)
    generated = generate_markov_sequence(model, 1, 20, random.Random(21))
    # Cyclic training adds phrase-boundary last->first transitions explicitly.
    cyclic_training = tuple(phrase + (phrase[0],) for phrase in TRAINING_PHRASES)
    assert transition_coverage(generated, cyclic_training)["generated_not_in_training"] == ()
    assert seed_sweep() == seed_sweep()
    assert len(seed_sweep()) == 10
    assert len(CHAPTER_21_FILENAMES) == 13
