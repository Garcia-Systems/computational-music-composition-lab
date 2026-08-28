"""Transparent tonal arithmetic for Chapter 4.

A scale is stored as semitone offsets from a tonic.  The helpers deliberately
keep that small calculation visible instead of delegating it to a theory
library.
"""

from __future__ import annotations

from collections.abc import Sequence

from .events import NoteEvent

MAJOR = (0, 2, 4, 5, 7, 9, 11, 12)
NATURAL_MINOR = (0, 2, 3, 5, 7, 8, 10, 12)


def _validate_tonic(tonic: int) -> None:
    if isinstance(tonic, bool) or not isinstance(tonic, int):
        raise TypeError("tonic must be an integer")
    if not 0 <= tonic <= 127:
        raise ValueError("tonic must be between 0 and 127")


def _validate_intervals(intervals: tuple[int, ...]) -> None:
    if not isinstance(intervals, tuple) or not intervals:
        raise ValueError("intervals must be a non-empty tuple")
    if any(isinstance(interval, bool) or not isinstance(interval, int) for interval in intervals):
        raise TypeError("scale intervals must be integers")


def build_scale(tonic: int, intervals: tuple[int, ...]) -> tuple[int, ...]:
    """Apply each semitone offset in ``intervals`` to ``tonic``."""
    _validate_tonic(tonic)
    _validate_intervals(intervals)
    pitches = tuple(tonic + interval for interval in intervals)
    if any(not 0 <= pitch <= 127 for pitch in pitches):
        raise ValueError("the resulting scale pitches must be between 0 and 127")
    return pitches


def major_scale(tonic: int) -> tuple[int, ...]:
    """Build one ascending octave of the major scale from ``tonic``."""
    return build_scale(tonic, MAJOR)


def natural_minor_scale(tonic: int) -> tuple[int, ...]:
    """Build one ascending octave of the natural-minor scale from ``tonic``."""
    return build_scale(tonic, NATURAL_MINOR)


def scale_degree(scale: tuple[int, ...], degree: int) -> int:
    """Return a pitch using the musician-facing degree range 1 through 8."""
    if isinstance(degree, bool) or not isinstance(degree, int):
        raise TypeError("degree must be an integer")
    if not 1 <= degree <= 8:
        raise ValueError("degree must be between 1 and 8")
    if len(scale) < 8:
        raise ValueError("scale must contain at least eight pitches")
    return scale[degree - 1]


def pitch_from_degree(tonic: int, intervals: tuple[int, ...], degree: int) -> int:
    """Resolve degree 1--8 to an absolute pitch in a tonal collection."""
    return scale_degree(build_scale(tonic, intervals), degree)


def pitch_in_scale(pitch: int, tonic: int, intervals: tuple[int, ...]) -> bool:
    """Report pitch-class membership, independent of the pitch's octave."""
    _validate_tonic(tonic)
    if isinstance(pitch, bool) or not isinstance(pitch, int):
        raise TypeError("pitch must be an integer")
    if not 0 <= pitch <= 127:
        raise ValueError("pitch must be between 0 and 127")
    _validate_intervals(intervals)
    scale_pitch_classes = {(tonic + interval) % 12 for interval in intervals}
    return pitch % 12 in scale_pitch_classes


def events_from_degrees(
    degrees: Sequence[int],
    tonic: int,
    intervals: tuple[int, ...],
    durations: Sequence[float],
    *,
    velocity: int = 90,
) -> tuple[NoteEvent, ...]:
    """Resolve degrees to sequential ``NoteEvent`` values on a beat timeline."""
    if len(degrees) != len(durations):
        raise ValueError("degrees and durations must have the same length")
    events: list[NoteEvent] = []
    start = 0.0
    for degree, duration in zip(degrees, durations, strict=True):
        pitch = pitch_from_degree(tonic, intervals, degree)
        event = NoteEvent(pitch, start, duration, velocity)
        events.append(event)
        start += duration
    return tuple(events)
