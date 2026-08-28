"""Chapter 21 controlled evaluation experiments and listening artifacts."""
from __future__ import annotations

from collections import Counter
from pathlib import Path
import random

from .chapter19 import degrees_to_c_major, random_walk_degrees
from .chapter20 import TRAINING_PHRASES, degrees_to_events
from .constraints import maximum_leap_at_most, melody_from_pitches_and_durations
from .evaluation import (aggregate_melodies, generation_profile,
                         harmonic_alignment_profile, melody_profile,
                         ngram_overlap, repetition_profile, rhythm_profile,
                         transition_coverage)
from .event_rendering import render_events
from .events import NoteEvent
from .markov import build_transition_counts_from_sequences, generate_markov_sequence
from .melody_harmony import HarmonicSpan
from .waveform import write_wav

CHAPTER_21_FILENAMES = (
    "chapter_21_stepwise.wav", "chapter_21_leaping.wav",
    "chapter_21_sparse_rhythm.wav", "chapter_21_dense_rhythm.wav",
    "chapter_21_harmonic_alignment_chord_tones.wav",
    "chapter_21_harmonic_alignment_non_chord_tones.wav",
    "chapter_21_loose_constraints.wav", "chapter_21_tight_constraints.wav",
    "chapter_21_capstone_constraint.wav", "chapter_21_capstone_random.wav",
    "chapter_21_capstone_weighted.wav", "chapter_21_capstone_walk.wav",
    "chapter_21_capstone_markov.wav",
)

POOL = (60, 62, 64, 65, 67, 69, 71, 72)
TRAINING = tuple(value for phrase in TRAINING_PHRASES for value in phrase)


def _events(pitches, duration=.5):
    return melody_from_pitches_and_durations(tuple(pitches), (duration,) * len(pitches))


def capstone_sequences(seed: int = 21) -> dict[str, tuple[int, ...]]:
    """Five strategies in the same C-major register, length, and rhythm."""
    model = build_transition_counts_from_sequences(TRAINING_PHRASES, cyclic=True)
    degrees = generate_markov_sequence(model, 1, 16, random.Random(seed))
    rng = random.Random(seed)
    random_sequence = tuple(rng.choice(POOL) for _ in range(16))
    rng = random.Random(seed)
    return {
        "Constraint": (60, 62, 64, 65, 67, 65, 64, 62) * 2,
        "Random": random_sequence,
        "Weighted": tuple(rng.choices(POOL, (4, 1, 2, 1, 3, 1, 1, 2), k=16)),
        "Walk": degrees_to_c_major(random_walk_degrees(1, 16, (-2, -1, 1, 2), 1, 8,
                                                        random.Random(seed))),
        "Markov": degrees_to_c_major(degrees),
    }


def seed_sweep() -> tuple[tuple[int, ...], ...]:
    return tuple(tuple(random.Random(seed).choice(POOL) for _ in range(16))
                 for seed in range(10))


def render_chapter_21(output_directory: Path = Path("outputs")) -> tuple[Path, ...]:
    stepwise, leaping = (60, 62, 64, 65, 67, 65, 64, 62), (60, 67, 62, 69, 64, 71, 65, 72)
    sparse = melody_from_pitches_and_durations((60, 64, 67, 60), (1, 1, 1, 1))
    dense = _events((60, 64, 67, 60, 60, 64, 67, 60), .5)
    aligned = _events((60, 64, 67, 60, 64, 67, 60, 64), .5)
    unaligned = _events((62, 65, 69, 62, 65, 69, 62, 65), .5)
    loose, tight = (60, 72, 62, 71, 64, 69, 65, 67), stepwise
    capstone = capstone_sequences()
    scores = [_events(stepwise), _events(leaping), sparse, dense, aligned, unaligned,
              _events(loose), _events(tight)] + [_events(sequence) for sequence in capstone.values()]
    paths = tuple(output_directory / name for name in CHAPTER_21_FILENAMES)
    for path, score in zip(paths, scores, strict=True):
        write_wav(path, render_events(score, 108))
    return paths


def run_chapter_21(output_directory: Path = Path("outputs")) -> None:
    paths = render_chapter_21(output_directory)
    basic = melody_profile((60, 62, 64, 67, 72))
    stepwise, leaping = melody_profile((60, 62, 64, 65, 67, 65, 64, 62)), melody_profile((60, 67, 62, 69, 64, 71, 65, 72))
    sparse = rhythm_profile(melody_from_pitches_and_durations((60, 64, 67, 60), (1, 1, 1, 1)))
    dense = rhythm_profile(_events((60, 64, 67, 60, 60, 64, 67, 60), .5))
    harmony = (HarmonicSpan(0, 4, (60, 64, 67)),)
    aligned = harmonic_alignment_profile(_events((60, 64, 67, 60, 64, 67, 60, 64), .5), harmony)
    unaligned = harmonic_alignment_profile(_events((62, 65, 69, 62, 65, 69, 62, 65), .5), harmony)
    loose, tight = (60, 72, 62, 71, 64, 69, 65, 67), (60, 62, 64, 65, 67, 65, 64, 62)
    independent = tuple(random.Random(19).choice(POOL) for _ in range(16))
    walk = degrees_to_c_major(random_walk_degrees(1, 16, (-2, -1, 1, 2), 1, 8, random.Random(19)))
    model = build_transition_counts_from_sequences(TRAINING_PHRASES, cyclic=True)
    markov_degrees = generate_markov_sequence(model, 1, 16, random.Random(20))
    frequency = tuple(random.Random(20).choices(tuple(sorted(Counter(TRAINING))),
                      tuple(Counter(TRAINING)[x] for x in sorted(Counter(TRAINING))), k=16))
    sweep = seed_sweep()
    capstone = capstone_sequences()
    rows = []
    for name, sequence in capstone.items():
        p = melody_profile(sequence)
        rows.append(f"{name:<11} {p.pitch_range:>5} {p.average_absolute_interval:>8.2f} {p.maximum_leap:>8} {p.step_count:>6} {p.repeat_count:>7} {p.unique_pitch_classes:>10}")
    print(f"""Chapter 21 — Evaluation: Describing Generated Music

Metrics describe. Listeners judge. DESCRIPTIVE METRIC ≠ AESTHETIC SCORE.
A wide range is computable; “exciting” depends on context, listener, performance, and intention.

Experiment 1 — Basic melody profile
notes: {basic.note_count}; lowest/highest: {basic.lowest_pitch}/{basic.highest_pitch}; range: {basic.pitch_range} semitones
intervals: {basic.intervals}; average absolute interval: {basic.average_absolute_interval:.2f}; maximum leap: {basic.maximum_leap}
steps/leaps/repeats: {basic.step_count}/{basic.leap_count}/{basic.repeat_count}; pitch classes: {basic.pitch_class_distribution}

Experiment 2 — Stepwise versus leaping (same rhythm)
Metric                 Stepwise   Leaping
range                  {stepwise.pitch_range:>8} {leaping.pitch_range:>9}
average interval       {stepwise.average_absolute_interval:>8.2f} {leaping.average_absolute_interval:>9.2f}
maximum leap           {stepwise.maximum_leap:>8} {leaping.maximum_leap:>9}
steps                   {stepwise.step_count:>8} {leaping.step_count:>9}

Experiment 3 — Sparse versus dense rhythm
attacks                 {sparse.attack_count:>8} {dense.attack_count:>9}
beat span               {sparse.beat_span:>8.1f} {dense.beat_span:>9.1f}
attacks/beat            {sparse.attacks_per_beat:>8.2f} {dense.attacks_per_beat:>9.2f}

Experiment 4 — Harmonic alignment under one simplified C-major chord
chord tones             {aligned['chord_tone_count']}/8       {unaligned['chord_tone_count']}/8
strong-beat chord tones {aligned['strong_beat_chord_tone_count']}/{aligned['strong_beat_note_count']}       {unaligned['strong_beat_chord_tone_count']}/{unaligned['strong_beat_note_count']}
More chord tones does not mean better: passing tones, suspensions, neighbors, and chromaticism may be intentional.

Experiment 5 — Chapter 18 constraint visibility
loose maximum configured 12; observed {melody_profile(loose).maximum_leap}; passes: {maximum_leap_at_most(loose, 12).passed}
tight maximum configured 3; observed {melody_profile(tight).maximum_leap}; passes: {maximum_leap_at_most(tight, 3).passed}

Experiment 6 — Chapter 19 independent choice versus random walk
independent: range {melody_profile(independent).pitch_range}, average interval {melody_profile(independent).average_absolute_interval:.2f}, maximum {melody_profile(independent).maximum_leap}, steps {melody_profile(independent).step_count}
walk:        range {melody_profile(walk).pitch_range}, average interval {melody_profile(walk).average_absolute_interval:.2f}, maximum {melody_profile(walk).maximum_leap}, steps {melody_profile(walk).step_count}

Experiment 7 — Chapter 20 frequency versus first-order Markov
frequency degrees: {frequency}
Markov degrees:    {markov_degrees}
Markov 3-gram overlap: {ngram_overlap(markov_degrees, TRAINING, 3)}
Markov transition coverage: {transition_coverage(markov_degrees, TRAINING_PHRASES)}
Exact full training copy: {markov_degrees == TRAINING}

Experiment 8 — seeds 0 through 9
{aggregate_melodies(sweep)}
same seed and parameters identical: {seed_sweep() == sweep}

Experiment 9 — A / A' / B
A and literal return can share pitch, rhythm, and contour; A' and B must be compared fact by fact, not by one similarity score.
Repeated-sequence facts for A: {repetition_profile((60, 62, 64, 62, 60, 62, 64, 62))}

Experiment 10 — generator comparison capstone (fixed C major, 16 attacks, 0.5-beat rhythm)
Strategy    Range Avg int Max leap  Steps Repeats Unique PCs
{chr(10).join(rows)}
Training overlap is n/a except for Markov: {ngram_overlap(markov_degrees, TRAINING, 3)}

Which melody did you prefer? What did you hear? Did a metric miss something you cared about?
Summary statistics compress information: equal histograms can hide different order and contour.
Evaluation can expose bugs (for example, a 12-semitone leap in a promised stepwise generator), but tests should enforce explicit requirements—not taste.
No overall quality score is computed. Diversity ≠ quality; unobserved training n-grams ≠ artistic originality.

Created:
{chr(10).join(map(str, paths))}""")
