"""Small, transparent measurements of melodic motion for Chapter 5."""

from __future__ import annotations

from collections.abc import Sequence
from dataclasses import dataclass

from .events import NoteEvent
from .pitch import interval_semitones


def interval_between(first: int, second: int) -> int:
    """Return signed semitone motion from ``first`` to ``second``."""
    return interval_semitones(first, second)


def interval_size(interval: int) -> int:
    """Return interval magnitude without its direction."""
    if isinstance(interval, bool) or not isinstance(interval, int):
        raise TypeError("interval must be an integer")
    return abs(interval)


def classify_motion(interval: int) -> str:
    """Classify 0 as repeat, 1--2 semitones as step, and 3+ as leap."""
    size = interval_size(interval)
    if size == 0:
        return "repeat"
    if size <= 2:
        return "step"
    return "leap"


def motion_direction(interval: int) -> str:
    """Describe the sign of an interval independently of its size."""
    interval_size(interval)  # validate while leaving the comparison visible
    if interval > 0:
        return "ascending"
    if interval < 0:
        return "descending"
    return "stationary"


def interval_sequence(pitches: Sequence[int]) -> tuple[int, ...]:
    """Return motion between adjacent pitches in the supplied order."""
    return tuple(
        interval_between(first, second)
        for first, second in zip(pitches, pitches[1:])
    )


def pitches_from_events(events: Sequence[NoteEvent]) -> tuple[int, ...]:
    """Extract pitches in sequence order; event start times are not re-sorted."""
    return tuple(event.pitch for event in events)


def melodic_range(pitches: Sequence[int]) -> int:
    """Return highest minus lowest pitch, or zero when there are no pitches."""
    if not pitches:
        return 0
    # interval_between validates the extrema as pitch values.
    return interval_between(min(pitches), max(pitches))


def contour_directions(pitches: Sequence[int]) -> tuple[str, ...]:
    """Return ascending, descending, or stationary for each adjacent pair."""
    return tuple(motion_direction(interval) for interval in interval_sequence(pitches))


def average_interval_size(intervals: Sequence[int]) -> float:
    """Return mean absolute semitone distance, or 0.0 for no movements."""
    if not intervals:
        return 0.0
    return sum(interval_size(interval) for interval in intervals) / len(intervals)


@dataclass(frozen=True)
class MelodicProfile:
    """A compact description of movement, not a judgment of musical quality."""

    notes: int
    lowest: int | None
    highest: int | None
    range_semitones: int
    movements: int
    repeats: int
    steps: int
    leaps: int
    ascending: int
    descending: int
    stationary: int
    repeat_percentage: float
    stepwise_percentage: float
    leap_percentage: float
    ascending_percentage: float
    descending_percentage: float
    stationary_percentage: float
    average_interval_size: float


def melodic_profile(pitches: Sequence[int]) -> MelodicProfile:
    """Measure range, motion types, directions, and average movement size."""
    intervals = interval_sequence(pitches)
    motions = tuple(classify_motion(interval) for interval in intervals)
    directions = tuple(motion_direction(interval) for interval in intervals)
    movements = len(intervals)

    def count(values: tuple[str, ...], value: str) -> int:
        return values.count(value)

    def percentage(amount: int) -> float:
        return amount / movements * 100 if movements else 0.0

    repeats, steps, leaps = (count(motions, value) for value in ("repeat", "step", "leap"))
    ascending, descending, stationary = (
        count(directions, value) for value in ("ascending", "descending", "stationary")
    )
    return MelodicProfile(
        notes=len(pitches),
        lowest=min(pitches) if pitches else None,
        highest=max(pitches) if pitches else None,
        range_semitones=melodic_range(pitches),
        movements=movements,
        repeats=repeats,
        steps=steps,
        leaps=leaps,
        ascending=ascending,
        descending=descending,
        stationary=stationary,
        repeat_percentage=percentage(repeats),
        stepwise_percentage=percentage(steps),
        leap_percentage=percentage(leaps),
        ascending_percentage=percentage(ascending),
        descending_percentage=percentage(descending),
        stationary_percentage=percentage(stationary),
        average_interval_size=average_interval_size(intervals),
    )
