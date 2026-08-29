"""Selected, transparent blues vocabularies and recipes for Chapter 29.

These helpers model computable features; they do not define or authenticate a
musical tradition.  General event, chord, rendering, and OSC machinery remains
elsewhere in the package.
"""
from __future__ import annotations

from dataclasses import replace
import random

from .chords import dominant_seventh
from .events import NoteEvent

MINOR_BLUES = (0, 3, 5, 6, 7, 10, 12)
BASELINE_DEGREES = (1, 1, 1, 1, 4, 4, 1, 1, 5, 4, 1, 1)
QUICK_CHANGE_DEGREES = (1, 4, 1, 1, 4, 4, 1, 1, 5, 4, 1, 5)
DEGREE_ROOT_OFFSETS = {1: 0, 4: 5, 5: 7}
MOVING_BASS_INTERVALS = (0, 4, 7, 9, 9, 7, 4, 0)


def bar_start_beat(bar_number: int, beats_per_bar: int = 4) -> int:
    """Map a reader-facing, one-indexed bar number to a zero-indexed beat."""
    if isinstance(bar_number, bool) or not isinstance(bar_number, int) or bar_number < 1:
        raise ValueError("bar_number must be a positive one-indexed integer")
    if isinstance(beats_per_bar, bool) or not isinstance(beats_per_bar, int) or beats_per_bar < 1:
        raise ValueError("beats_per_bar must be a positive integer")
    return (bar_number - 1) * beats_per_bar


def twelve_bar_degrees(*, quick_change: bool = False, turnaround: bool = False) -> tuple[int, ...]:
    degrees = list(QUICK_CHANGE_DEGREES if quick_change else BASELINE_DEGREES)
    if turnaround:
        degrees[-1] = 5
    return tuple(degrees)


def harmony_timeline(tonic: int = 60, *, quick_change: bool = False,
                     turnaround: bool = False, beats_per_bar: int = 4) -> tuple[tuple[int, int, int, tuple[int, ...]], ...]:
    """Return (bar, beat, degree, dominant-seventh pitches) per bar."""
    return tuple((bar, bar_start_beat(bar, beats_per_bar), degree,
                  dominant_seventh(tonic + DEGREE_ROOT_OFFSETS[degree]))
                 for bar, degree in enumerate(twelve_bar_degrees(
                     quick_change=quick_change, turnaround=turnaround), 1))


def straight_eighth_onsets(start: float = 0.0) -> tuple[float, float]:
    return (start, start + .5)


def shuffle_eighth_onsets(start: float = 0.0) -> tuple[float, float]:
    """Exact pedagogical triplet-grid approximation: first and third thirds."""
    return (start, start + 2 / 3)


def blues_bass_pitches(root: int) -> tuple[int, ...]:
    return tuple(root + interval for interval in MOVING_BASS_INTERVALS)


def generate_blues_phrase(*, tonic: int = 60, seed: int = 2026,
                          start: float = 0.0, duration: float = 8.0,
                          pitch_range: tuple[int, int] = (60, 72),
                          maximum_leap: int = 7) -> tuple[NoteEvent, ...]:
    """Generate one bounded phrase from the discrete minor-blues approximation."""
    if duration <= 0 or maximum_leap < 0 or pitch_range[0] > pitch_range[1]:
        raise ValueError("invalid phrase constraints")
    vocabulary = tuple(p for p in range(pitch_range[0], pitch_range[1] + 1)
                       if (p - tonic) % 12 in set(MINOR_BLUES[:-1]))
    if not vocabulary:
        raise ValueError("pitch range contains no vocabulary pitches")
    rng, pitches, previous = random.Random(seed), [], None
    # Six attacks occupy the first 3.5 beats; the remaining duration is structural space.
    local_onsets = (0.0, 2 / 3, 1.5, 2.0, 8 / 3, 3.5)
    for _ in local_onsets:
        candidates = tuple(p for p in vocabulary if previous is None or abs(p - previous) <= maximum_leap)
        if not candidates:
            raise ValueError("maximum leap leaves no candidate")
        previous = rng.choice(candidates); pitches.append(previous)
    ending = min((p for p in vocabulary if p % 12 == tonic % 12),
                 key=lambda p: abs(p - pitches[-1]), default=pitches[-1])
    pitches[-1] = ending
    return tuple(NoteEvent(pitch, start + onset, min(.45, duration - onset), 92)
                 for pitch, onset in zip(pitches, local_onsets, strict=True) if onset < duration)


def ending_variation(events: tuple[NoteEvent, ...], semitones: int = 3) -> tuple[NoteEvent, ...]:
    """Derive A' by changing only its final pitch (when MIDI bounds permit)."""
    if not events:
        return events
    pitch = events[-1].pitch + semitones
    if not 0 <= pitch <= 127:
        raise ValueError("variation exceeds MIDI pitch range")
    return events[:-1] + (replace(events[-1], pitch=pitch),)
