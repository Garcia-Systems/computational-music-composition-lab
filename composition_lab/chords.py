"""Transparent triad and voicing operations for Chapter 8."""

from __future__ import annotations

from collections.abc import Sequence

from .events import NoteEvent
from .pitch import _validate_pitch

MAJOR_TRIAD = (0, 4, 7)
MINOR_TRIAD = (0, 3, 7)
DIMINISHED_TRIAD = (0, 3, 6)
DOMINANT_SEVENTH = (0, 4, 7, 10)


def build_chord(root: int, intervals: tuple[int, ...]) -> tuple[int, ...]:
    """Apply a nondecreasing interval pattern to a root pitch."""
    _validate_pitch(root)
    if not isinstance(intervals, tuple) or not intervals:
        raise ValueError("intervals must be a non-empty tuple")
    if any(isinstance(value, bool) or not isinstance(value, int) for value in intervals):
        raise TypeError("chord intervals must be integers")
    if intervals[0] != 0 or any(a > b for a, b in zip(intervals, intervals[1:])):
        raise ValueError("intervals must start at zero and be nondecreasing")
    pitches = tuple(root + value for value in intervals)
    if any(pitch > 127 for pitch in pitches):
        raise ValueError("the resulting chord pitches must be between 0 and 127")
    return pitches


def major_triad(root: int) -> tuple[int, ...]:
    return build_chord(root, MAJOR_TRIAD)


def minor_triad(root: int) -> tuple[int, ...]:
    return build_chord(root, MINOR_TRIAD)


def diminished_triad(root: int) -> tuple[int, ...]:
    return build_chord(root, DIMINISHED_TRIAD)


def dominant_seventh(root: int) -> tuple[int, ...]:
    """Build the narrowly defined root-position dominant seventh used in Chapter 29."""
    return build_chord(root, DOMINANT_SEVENTH)


def invert_chord(pitches: tuple[int, ...], inversion: int) -> tuple[int, ...]:
    """Move the lowest pitch up octaves; input must be ascending root position."""
    if not pitches:
        raise ValueError("pitches must not be empty")
    for pitch in pitches:
        _validate_pitch(pitch)
    if tuple(sorted(pitches)) != pitches:
        raise ValueError("pitches must be sorted in ascending root position")
    if isinstance(inversion, bool) or not isinstance(inversion, int):
        raise TypeError("inversion must be an integer")
    if not 0 <= inversion < len(pitches):
        raise ValueError("inversion must identify a chord member")
    result = list(pitches)
    for _ in range(inversion):
        raised = result.pop(0) + 12
        if raised > 127:
            raise ValueError("inversion would exceed pitch 127")
        result.append(raised)
    return tuple(result)


def chord_pitch_classes(pitches: Sequence[int]) -> tuple[int, ...]:
    """Return unique pitch classes in ascending pitch-class order."""
    for pitch in pitches:
        _validate_pitch(pitch)
    return tuple(sorted({pitch % 12 for pitch in pitches}))


def triad_quality(pitches: tuple[int, ...]) -> str:
    """Classify an ascending, root-position triad (not arbitrary inversions)."""
    if len(pitches) != 3:
        return "unknown"
    for pitch in pitches:
        _validate_pitch(pitch)
    if tuple(sorted(pitches)) != pitches:
        raise ValueError("pitches must be sorted in ascending root position")
    pattern = tuple(pitch - pitches[0] for pitch in pitches)
    return {
        MAJOR_TRIAD: "major", MINOR_TRIAD: "minor",
        DIMINISHED_TRIAD: "diminished",
    }.get(pattern, "unknown")


def chord_events(
    pitches: Sequence[int], start: float = 0.0, duration: float = 2.0,
    velocity: int = 80,
) -> tuple[NoteEvent, ...]:
    """Place every chord pitch at one shared onset."""
    return tuple(NoteEvent(pitch, start, duration, velocity) for pitch in pitches)


def arpeggiate_chord(
    pitches: Sequence[int], start: float = 0.0, note_duration: float = 0.5,
    step: float = 0.5, velocity: int = 80,
) -> tuple[NoteEvent, ...]:
    """Place chord tones sequentially at a fixed onset step."""
    if step <= 0:
        raise ValueError("step must be greater than zero")
    return tuple(
        NoteEvent(pitch, start + index * step, note_duration, velocity)
        for index, pitch in enumerate(pitches)
    )


def triad_from_scale_degree(
    tonic: int, scale_intervals: tuple[int, ...], degree: int,
) -> tuple[int, int, int]:
    """Stack degree, degree+2, and degree+4 into an ascending diatonic triad."""
    _validate_pitch(tonic)
    if len(scale_intervals) not in (7, 8):
        raise ValueError("scale intervals must describe seven degrees")
    degrees = scale_intervals[:7]
    if degrees[0] != 0 or any(a >= b for a, b in zip(degrees, degrees[1:])):
        raise ValueError("scale intervals must be strictly ascending from zero")
    if isinstance(degree, bool) or not isinstance(degree, int):
        raise TypeError("degree must be an integer")
    if not 1 <= degree <= 7:
        raise ValueError("degree must be between 1 and 7")
    pitches = []
    for offset in (0, 2, 4):
        index = degree - 1 + offset
        pitch = tonic + degrees[index % 7] + 12 * (index // 7)
        _validate_pitch(pitch)
        pitches.append(pitch)
    return tuple(pitches)  # type: ignore[return-value]
