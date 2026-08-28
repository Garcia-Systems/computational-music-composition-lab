"""Small, inspectable chord-progression operations for Chapter 9."""

from __future__ import annotations

from collections.abc import Sequence

from .chords import chord_events, triad_from_scale_degree, triad_quality
from .events import NoteEvent

MAJOR_ROMAN_NUMERALS = ("I", "ii", "iii", "IV", "V", "vi", "vii°")
NATURAL_MINOR_ROMAN_NUMERALS = ("i", "ii°", "III", "iv", "v", "VI", "VII")


def _validate_progression(degrees: Sequence[int], durations: Sequence[float]) -> None:
    if len(degrees) != len(durations):
        raise ValueError("degrees and durations must have the same length")
    if not degrees:
        raise ValueError("a progression must contain at least one chord")
    for degree in degrees:
        if isinstance(degree, bool) or not isinstance(degree, int):
            raise TypeError("progression degrees must be integers")
        if not 1 <= degree <= 7:
            raise ValueError("progression degrees must be between 1 and 7")
    for duration in durations:
        if isinstance(duration, bool) or not isinstance(duration, (int, float)):
            raise TypeError("chord durations must be numbers")
        if duration <= 0:
            raise ValueError("chord durations must be greater than zero")


def progression_starts(durations: Sequence[float]) -> tuple[float, ...]:
    """Return sequential chord onsets, measured in beats."""
    starts: list[float] = []
    elapsed = 0.0
    for duration in durations:
        if isinstance(duration, bool) or not isinstance(duration, (int, float)):
            raise TypeError("chord durations must be numbers")
        if duration <= 0:
            raise ValueError("chord durations must be greater than zero")
        starts.append(elapsed)
        elapsed += duration
    return tuple(starts)


def progression_duration(durations: Sequence[float]) -> float:
    """Return the total progression span in beats."""
    progression_starts(durations)  # share the duration validation contract
    return float(sum(durations))


def roman_numeral_for_degree(degree: int, quality: str) -> str:
    """Label one diatonic triad; this intentionally is not a numeral parser."""
    if isinstance(degree, bool) or not isinstance(degree, int):
        raise TypeError("degree must be an integer")
    if not 1 <= degree <= 7:
        raise ValueError("degree must be between 1 and 7")
    base = ("I", "II", "III", "IV", "V", "VI", "VII")[degree - 1]
    if quality == "major":
        return base
    if quality == "minor":
        return base.lower()
    if quality == "diminished":
        return base.lower() + "°"
    raise ValueError("quality must be major, minor, or diminished")


def progression_chords(
    tonic: int, scale_intervals: tuple[int, ...], degrees: Sequence[int],
) -> tuple[tuple[int, int, int], ...]:
    """Resolve a scale-degree pattern as ascending root-position triads."""
    # Use dummy valid durations so degree validation stays in one place.
    _validate_progression(degrees, (1.0,) * len(degrees))
    return tuple(triad_from_scale_degree(tonic, scale_intervals, degree) for degree in degrees)


def progression_events(
    tonic: int,
    scale_intervals: tuple[int, ...],
    degrees: Sequence[int],
    durations: Sequence[float],
    velocity: int = 80,
) -> tuple[NoteEvent, ...]:
    """Place each diatonic triad simultaneously on a sequential beat timeline."""
    _validate_progression(degrees, durations)
    events: list[NoteEvent] = []
    for degree, start, duration in zip(
        degrees, progression_starts(durations), durations, strict=True
    ):
        triad = triad_from_scale_degree(tonic, scale_intervals, degree)
        events.extend(chord_events(triad, start, duration, velocity))
    return tuple(events)


def repeat_progression(
    degrees: Sequence[int], durations: Sequence[float], repetitions: int,
) -> tuple[tuple[int, ...], tuple[float, ...]]:
    """Repeat progression structure without resolving it to a particular key."""
    _validate_progression(degrees, durations)
    if isinstance(repetitions, bool) or not isinstance(repetitions, int):
        raise TypeError("repetitions must be an integer")
    if repetitions < 1:
        raise ValueError("repetitions must be at least one")
    return tuple(degrees) * repetitions, tuple(durations) * repetitions


def root_sequence(
    tonic: int, scale_intervals: tuple[int, ...], degrees: Sequence[int],
) -> tuple[int, ...]:
    """Return the bass pitches of the chapter's root-position triads."""
    return tuple(chord[0] for chord in progression_chords(tonic, scale_intervals, degrees))


def progression_roman_numerals(
    tonic: int, scale_intervals: tuple[int, ...], degrees: Sequence[int],
) -> tuple[str, ...]:
    """Derive narrow Roman-numeral labels from each triad's audible quality."""
    return tuple(
        roman_numeral_for_degree(degree, triad_quality(chord))
        for degree, chord in zip(degrees, progression_chords(tonic, scale_intervals, degrees), strict=True)
    )
