"""Small, explicit constraint and exhaustive-search tools for Chapter 18.

These functions describe membership in a caller-chosen search space.  They do
not measure musical quality: a failed result means only that a stated rule was
not met.
"""

from __future__ import annotations

from collections.abc import Callable, Iterable, Sequence
from dataclasses import dataclass
from itertools import product
from math import isclose

from .events import NoteEvent
from .melody import interval_sequence, melodic_range
from .melody_harmony import HarmonicSpan, active_harmony_at, is_chord_tone
from .pitch import pitch_to_name
from .scales import pitch_in_scale

PitchCandidate = tuple[int, ...]


@dataclass(frozen=True)
class ConstraintResult:
    """One inspectable pass/fail fact."""

    name: str
    passed: bool
    detail: str


@dataclass(frozen=True)
class Constraint:
    """A readable name paired with a function that checks one candidate."""

    name: str
    check: Callable[[PitchCandidate], ConstraintResult]


@dataclass(frozen=True)
class CandidateEvaluation:
    candidate: PitchCandidate
    results: tuple[ConstraintResult, ...]


@dataclass(frozen=True)
class SearchResult:
    """Preserve both accepted and rejected candidates for inspection."""

    valid: tuple[PitchCandidate, ...]
    rejected: tuple[CandidateEvaluation, ...]


def _result(name: str, passed: bool, success: str, failure: str) -> ConstraintResult:
    return ConstraintResult(name, passed, success if passed else failure)


def within_pitch_range(pitches: Sequence[int], low: int, high: int) -> ConstraintResult:
    if low > high:
        raise ValueError("low pitch must not exceed high pitch")
    for pitch in pitches:
        if pitch < low:
            return ConstraintResult("pitch range", False, f"pitch {pitch} is below minimum {low}")
        if pitch > high:
            return ConstraintResult("pitch range", False, f"pitch {pitch} exceeds maximum {high}")
    return ConstraintResult("pitch range", True, f"all pitches between {low} and {high}")


def all_pitches_in_scale(pitches: Sequence[int], tonic: int,
                         scale_intervals: tuple[int, ...]) -> ConstraintResult:
    for pitch in pitches:
        if not pitch_in_scale(pitch, tonic, scale_intervals):
            return ConstraintResult("scale membership", False,
                                    f"{pitch_to_name(pitch)} ({pitch}) is outside the chosen scale")
    return ConstraintResult("scale membership", True, "all pitches belong to the chosen scale")


def maximum_leap_at_most(pitches: Sequence[int], max_semitones: int) -> ConstraintResult:
    if max_semitones < 0:
        raise ValueError("maximum leap must be nonnegative")
    for first, second in zip(pitches, pitches[1:]):
        distance = abs(second - first)
        if distance > max_semitones:
            return ConstraintResult(
                "maximum leap", False,
                f"{pitch_to_name(first)} -> {pitch_to_name(second)} = {distance} semitones; maximum allowed = {max_semitones}",
            )
    return ConstraintResult("maximum leap", True,
                            f"every adjacent movement is at most {max_semitones} semitones")


def starts_on_pitch_class(pitches: Sequence[int], pitch_class: int) -> ConstraintResult:
    passed = bool(pitches) and pitches[0] % 12 == pitch_class % 12
    actual = "empty candidate" if not pitches else f"starts on {pitch_to_name(pitches[0])}"
    return _result("starting note", passed, actual, f"{actual}; required pitch class {pitch_class % 12}")


def ends_on_pitch_class(pitches: Sequence[int], pitch_class: int) -> ConstraintResult:
    passed = bool(pitches) and pitches[-1] % 12 == pitch_class % 12
    actual = "empty candidate" if not pitches else f"ends on {pitch_to_name(pitches[-1])}"
    return _result("ending note", passed, actual, f"{actual}; required pitch class {pitch_class % 12}")


def has_note_count(pitches: Sequence[int], required_count: int) -> ConstraintResult:
    passed = len(pitches) == required_count
    return _result("note count", passed, f"contains {required_count} notes",
                   f"contains {len(pitches)} notes; required {required_count}")


def no_immediate_repeated_pitches(pitches: Sequence[int]) -> ConstraintResult:
    for index, (first, second) in enumerate(zip(pitches, pitches[1:]), 1):
        if first == second:
            return ConstraintResult("no immediate repeats", False,
                                    f"positions {index} and {index + 1} both contain {pitch_to_name(first)}")
    return ConstraintResult("no immediate repeats", True, "no neighboring pitches repeat")


def minimum_stepwise_fraction(pitches: Sequence[int], minimum_fraction: float) -> ConstraintResult:
    if not 0 <= minimum_fraction <= 1:
        raise ValueError("minimum fraction must be between zero and one")
    movements = interval_sequence(pitches)
    steps = sum(1 for movement in movements if 1 <= abs(movement) <= 2)
    fraction = 1.0 if not movements else steps / len(movements)
    passed = fraction >= minimum_fraction
    detail = f"{steps} of {len(movements)} movements are steps ({fraction:.1%}); required {minimum_fraction:.1%}"
    return ConstraintResult("stepwise fraction", passed, detail)


def melodic_range_at_most(pitches: Sequence[int], max_semitones: int) -> ConstraintResult:
    actual = melodic_range(pitches)
    passed = actual <= max_semitones
    return ConstraintResult("melodic range", passed,
                            f"melodic range is {actual} semitones; maximum is {max_semitones}")


def contains_pitch_pattern(pitches: Sequence[int], motif: Sequence[int]) -> ConstraintResult:
    motif_tuple = tuple(motif)
    if not motif_tuple:
        raise ValueError("motif must not be empty")
    passed = any(tuple(pitches[i:i + len(motif_tuple)]) == motif_tuple
                 for i in range(len(pitches) - len(motif_tuple) + 1))
    return _result("pitch motif", passed, f"contains literal motif {motif_tuple}",
                   f"does not contain literal motif {motif_tuple}")


def contains_interval_pattern(pitches: Sequence[int], pattern: Sequence[int]) -> ConstraintResult:
    wanted = tuple(pattern)
    if not wanted:
        raise ValueError("interval pattern must not be empty")
    intervals = interval_sequence(pitches)
    passed = any(intervals[i:i + len(wanted)] == wanted
                 for i in range(len(intervals) - len(wanted) + 1))
    return _result("interval motif", passed, f"contains interval pattern {wanted}",
                   f"does not contain interval pattern {wanted}")


def evaluate_candidate(pitches: Sequence[int], constraints: Sequence[Constraint]) -> tuple[ConstraintResult, ...]:
    candidate = tuple(pitches)
    return tuple(constraint.check(candidate) for constraint in constraints)


def candidate_is_valid(results: Sequence[ConstraintResult]) -> bool:
    return all(result.passed for result in results)


def enumerate_pitch_candidates(allowed_pitches: Sequence[int], length: int,
                               *, limit: int = 1_000_000) -> tuple[PitchCandidate, ...]:
    """Enumerate lexicographically, refusing accidentally impractical spaces."""
    if length < 0:
        raise ValueError("length must be nonnegative")
    pool = tuple(allowed_pitches)
    size = len(pool) ** length
    if size > limit:
        raise ValueError(f"search space has {size:,} candidates; limit is {limit:,}")
    return tuple(product(pool, repeat=length))


def find_valid_candidates(candidates: Iterable[Sequence[int]],
                          constraints: Sequence[Constraint]) -> SearchResult:
    valid: list[PitchCandidate] = []
    rejected: list[CandidateEvaluation] = []
    for pitches in candidates:
        candidate = tuple(pitches)
        results = evaluate_candidate(candidate, constraints)
        if candidate_is_valid(results):
            valid.append(candidate)
        else:
            rejected.append(CandidateEvaluation(candidate, results))
    return SearchResult(tuple(valid), tuple(rejected))


def constraint_funnel(candidates: Iterable[PitchCandidate], constraints: Sequence[Constraint]) -> tuple[tuple[str, int], ...]:
    survivors = tuple(candidates)
    rows: list[tuple[str, int]] = [("All candidates", len(survivors))]
    for constraint in constraints:
        survivors = tuple(candidate for candidate in survivors if constraint.check(candidate).passed)
        rows.append((constraint.name, len(survivors)))
    return tuple(rows)


def total_duration_equals(durations: Sequence[float], target_beats: float,
                          *, tolerance: float = 1e-9) -> ConstraintResult:
    actual = sum(durations)
    passed = isclose(actual, target_beats, abs_tol=tolerance, rel_tol=0.0)
    return ConstraintResult("total duration", passed,
                            f"total is {actual:g} beats; target is {target_beats:g}")


def at_most_n_long_notes(durations: Sequence[float], maximum: int,
                         *, long_at_least: float = 2.0) -> ConstraintResult:
    count = sum(duration >= long_at_least for duration in durations)
    return ConstraintResult("long-note limit", count <= maximum,
                            f"{count} notes are at least {long_at_least:g} beats; maximum is {maximum}")


def melody_from_pitches_and_durations(pitches: Sequence[int], durations: Sequence[float],
                                      *, start: float = 0.0, velocity: int = 90) -> tuple[NoteEvent, ...]:
    if len(pitches) != len(durations):
        raise ValueError("pitches and durations must have the same length")
    events: list[NoteEvent] = []
    onset = start
    for pitch, duration in zip(pitches, durations, strict=True):
        events.append(NoteEvent(pitch, onset, duration, velocity))
        onset += duration
    return tuple(events)


def strong_beat_chord_tones(events: Sequence[NoteEvent], harmonies: Sequence[HarmonicSpan],
                            *, tolerance: float = 1e-9) -> ConstraintResult:
    for event in events:
        if isclose(event.start, round(event.start), abs_tol=tolerance):
            harmony = active_harmony_at(event.start, harmonies)
            if harmony is None:
                return ConstraintResult("strong-beat chord tones", False,
                                        f"no harmony exists at beat {event.start:g}")
            if not is_chord_tone(event.pitch, harmony.pitches):
                return ConstraintResult(
                    "strong-beat chord tones", False,
                    f"{pitch_to_name(event.pitch)} at beat {event.start:g} is not a chord tone",
                )
    return ConstraintResult("strong-beat chord tones", True,
                            "every integer-beat onset belongs to its active chord")
