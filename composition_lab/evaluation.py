"""Transparent structural descriptions for Chapter 21.

These pure functions observe music; none assigns an aesthetic score or mutates
the supplied events.  Undefined means are represented by ``None``.
"""
from __future__ import annotations

from collections import Counter
from collections.abc import Callable, Hashable, Sequence
from dataclasses import asdict, dataclass
from statistics import mean
from typing import TypeVar

from .events import NoteEvent, composition_duration
from .melody import contour_directions, interval_sequence, melodic_profile
from .melody_harmony import HarmonicSpan, active_harmony_at, is_chord_tone

T = TypeVar("T", bound=Hashable)


@dataclass(frozen=True)
class MelodyEvaluation:
    note_count: int
    lowest_pitch: int | None
    highest_pitch: int | None
    pitch_range: int
    intervals: tuple[int, ...]
    interval_distribution: dict[int, int]
    average_absolute_interval: float | None
    maximum_leap: int | None
    step_count: int
    leap_count: int
    repeat_count: int
    ascending: int
    descending: int
    unique_pitches: int
    unique_pitch_classes: int
    pitch_class_distribution: dict[int, int]
    contour: tuple[str, ...]


def melody_profile(pitches: Sequence[int]) -> MelodyEvaluation:
    """Wrap Chapter 5 analysis and add distributions useful for comparison."""
    base = melodic_profile(pitches)
    intervals = interval_sequence(pitches)
    return MelodyEvaluation(
        base.notes, base.lowest, base.highest, base.range_semitones, intervals,
        dict(sorted(Counter(abs(value) for value in intervals).items())),
        mean(map(abs, intervals)) if intervals else None,
        max(map(abs, intervals)) if intervals else None,
        base.steps, base.leaps, base.repeats, base.ascending, base.descending,
        len(set(pitches)), len({pitch % 12 for pitch in pitches}),
        dict(sorted(Counter(pitch % 12 for pitch in pitches).items())),
        contour_directions(pitches),
    )


@dataclass(frozen=True)
class RhythmProfile:
    beat_span: float
    attack_count: int
    attacks_per_beat: float | None
    unique_duration_count: int
    shortest_duration: float | None
    longest_duration: float | None
    average_duration: float | None
    duration_distribution: dict[float, int]
    onbeat_attacks: int
    offbeat_attacks: int


def rhythm_profile(events: Sequence[NoteEvent]) -> RhythmProfile:
    durations = [event.duration for event in events]
    span = composition_duration(events)
    onbeat = sum(event.start == int(event.start) for event in events)
    return RhythmProfile(span, len(events), len(events) / span if span else None,
                         len(set(durations)), min(durations, default=None),
                         max(durations, default=None), mean(durations) if durations else None,
                         dict(sorted(Counter(durations).items())), onbeat,
                         len(events) - onbeat)


def count_ngrams(sequence: Sequence[T], n: int) -> Counter[tuple[T, ...]]:
    if n <= 0:
        raise ValueError("n must be positive")
    return Counter(tuple(sequence[index:index + n])
                   for index in range(max(0, len(sequence) - n + 1)))


def repetition_profile(sequence: Sequence[T]) -> dict[str, object]:
    def details(n: int) -> dict[str, object]:
        counts = count_ngrams(sequence, n)
        repeated = {gram: count for gram, count in counts.items() if count > 1}
        common = min(counts, key=lambda gram: (-counts[gram], gram)) if counts else None
        return {"counts": dict(counts), "repeated": repeated,
                "most_common": common, "most_common_count": counts[common] if common else 0,
                "unique_ratio": len(counts) / sum(counts.values()) if counts else None}
    intervals = interval_sequence(sequence)  # symbolic integers in chapter examples
    return {"immediate_pitch_repeats": sum(a == b for a, b in zip(sequence, sequence[1:])),
            "repeated_interval_2grams": sum(c - 1 for c in count_ngrams(intervals, 2).values() if c > 1),
            "2grams": details(2), "3grams": details(3)}


def ngram_overlap(generated: Sequence[T], training: Sequence[T], n: int) -> dict[str, object]:
    generated_grams = list(count_ngrams(generated, n).elements())
    training_set = set(count_ngrams(training, n))
    observed = sum(gram in training_set for gram in generated_grams)
    total = len(generated_grams)
    return {"generated_ngrams": total, "present_in_training": observed,
            "not_present_in_training": total - observed,
            "overlap_fraction": observed / total if total else None}


def exact_copy(generated: Sequence[T], training: Sequence[T]) -> bool:
    return tuple(generated) == tuple(training)


def longest_shared_run(left: Sequence[T], right: Sequence[T]) -> tuple[T, ...]:
    best: tuple[T, ...] = ()
    for i in range(len(left)):
        for j in range(len(right)):
            length = 0
            while i + length < len(left) and j + length < len(right) and left[i + length] == right[j + length]:
                length += 1
            if length > len(best):
                best = tuple(left[i:i + length])
    return best


def scale_degree_distribution(pitches: Sequence[int], tonic: int,
                              scale_intervals: Sequence[int]) -> dict[int, int]:
    degrees = {interval % 12: index + 1 for index, interval in enumerate(scale_intervals)}
    return dict(sorted(Counter(degrees[(pitch - tonic) % 12] for pitch in pitches
                               if (pitch - tonic) % 12 in degrees).items()))


def harmonic_alignment_profile(events: Sequence[NoteEvent], spans: Sequence[HarmonicSpan],
                               strong_beat: Callable[[float], bool] = lambda beat: beat % 2 == 0
                               ) -> dict[str, int | float | None]:
    aligned: list[tuple[NoteEvent, bool]] = []
    for event in events:
        harmony = active_harmony_at(event.start, spans)
        if harmony is None:
            raise ValueError(f"no active harmony at beat {event.start}")
        aligned.append((event, is_chord_tone(event.pitch, harmony.pitches)))
    tones = sum(tone for _, tone in aligned)
    duration = sum(event.duration for event, _ in aligned)
    strong = [(event, tone) for event, tone in aligned if strong_beat(event.start)]
    return {"note_count": len(events), "chord_tone_count": tones,
            "non_chord_tone_count": len(events) - tones,
            "chord_tone_fraction": tones / len(events) if events else None,
            "duration_weighted_chord_tone_fraction":
                sum(event.duration for event, tone in aligned if tone) / duration if duration else None,
            "strong_beat_note_count": len(strong),
            "strong_beat_chord_tone_count": sum(tone for _, tone in strong),
            "strong_beat_chord_tone_fraction": sum(tone for _, tone in strong) / len(strong) if strong else None}


def constraint_pass_profile(candidates: Sequence[T], valid: Callable[[T], bool]) -> dict[str, int | float | None]:
    passing = sum(valid(candidate) for candidate in candidates)
    return {"generated": len(candidates), "valid": passing, "invalid": len(candidates) - passing,
            "pass_rate": passing / len(candidates) if candidates else None}


def generation_profile(sequences: Sequence[Sequence[T]]) -> dict[str, int | float | None]:
    total, unique = len(sequences), len({tuple(sequence) for sequence in sequences})
    return {"total": total, "unique": unique, "duplicate_outputs": total - unique,
            "unique_ratio": unique / total if total else None}


def aggregate_melodies(sequences: Sequence[Sequence[int]]) -> dict[str, object]:
    profiles = [melody_profile(sequence) for sequence in sequences]
    def summary(values: list[float]) -> dict[str, float] | None:
        return {"min": min(values), "mean": mean(values), "max": max(values)} if values else None
    return {"count": len(profiles), "pitch_range": summary([p.pitch_range for p in profiles]),
            "average_interval": summary([p.average_absolute_interval for p in profiles
                                         if p.average_absolute_interval is not None]),
            "diversity": generation_profile(sequences)}


def compare_profiles(left: MelodyEvaluation, right: MelodyEvaluation) -> dict[str, tuple[object, object]]:
    """Return side-by-side facts; deliberately do not collapse them to a score."""
    a, b = asdict(left), asdict(right)
    return {key: (a[key], b[key]) for key in a}


def transition_coverage(generated: Sequence[T], training: Sequence[Sequence[T]]) -> dict[str, object]:
    trained = {pair for sequence in training for pair in zip(sequence, sequence[1:])}
    produced = set(zip(generated, generated[1:]))
    return {"training_transitions": len(trained), "generated_transitions": len(produced),
            "generated_not_in_training": tuple(sorted(produced - trained))}
