"""Transparent monophonic bass choices for Chapter 14."""

from __future__ import annotations

from collections.abc import Sequence

from .events import NoteEvent
from .groove import GroovePattern

BASS_LOW = 28  # E1
BASS_HIGH = 60  # C4, inclusive


def _validate_range(low: int, high: int) -> None:
    if any(isinstance(value, bool) or not isinstance(value, int) for value in (low, high)):
        raise TypeError("bass range bounds must be integers")
    if not 0 <= low <= high <= 127:
        raise ValueError("bass range must be inside MIDI 0--127")


def pitches_for_class(pitch_class: int, low: int = BASS_LOW, high: int = BASS_HIGH) -> tuple[int, ...]:
    """Return every occurrence of a pitch class inside an inclusive bass range."""
    _validate_range(low, high)
    if isinstance(pitch_class, bool) or not isinstance(pitch_class, int):
        raise TypeError("pitch_class must be an integer")
    pitch_class %= 12
    return tuple(pitch for pitch in range(low, high + 1) if pitch % 12 == pitch_class)


def root_in_register(
    pitch_class: int, low: int = BASS_LOW, high: int = BASS_HIGH,
    reference: int | None = None,
) -> int:
    """Place a pitch class deterministically, lowest-first or nearest a reference."""
    candidates = pitches_for_class(pitch_class, low, high)
    if not candidates:
        raise ValueError("pitch class has no pitch in the requested bass range")
    if reference is None:
        return candidates[0]
    if isinstance(reference, bool) or not isinstance(reference, int):
        raise TypeError("reference must be an integer")
    return min(candidates, key=lambda pitch: (abs(pitch - reference), pitch))


def nearest_bass_pitch(pitch_class: int, previous: int, low: int = BASS_LOW, high: int = BASS_HIGH) -> int:
    """Choose the nearest in-range occurrence; lower pitch breaks an exact tie."""
    return root_in_register(pitch_class, low, high, previous)


def harmonic_root_pitch_classes(
    tonic: int, scale_intervals: Sequence[int], degrees: Sequence[int]
) -> tuple[int, ...]:
    """Extract roots from progression metadata rather than rendered voicings."""
    roots = []
    for degree in degrees:
        if isinstance(degree, bool) or not isinstance(degree, int) or not 1 <= degree <= 7:
            raise ValueError("degrees must be integers between 1 and 7")
        roots.append((tonic + scale_intervals[degree - 1]) % 12)
    return tuple(roots)


def bass_chord_role(pitch: int, chord_pitches: Sequence[int], root_pitch_class: int) -> str:
    """Classify a bass note in the chapter's narrow root/third/fifth triad model."""
    pcs = tuple(value % 12 for value in chord_pitches)
    pc, root = pitch % 12, root_pitch_class % 12
    if pc not in pcs:
        return "non-chord-tone"
    ordered = sorted(set(pcs), key=lambda value: (value - root) % 12)
    if pc == root:
        return "root"
    if len(ordered) > 1 and pc == ordered[1]:
        return "third"
    if len(ordered) > 2 and pc == ordered[2]:
        return "fifth"
    return "non-chord-tone"


def bass_from_progression(
    tonic: int, scale_intervals: Sequence[int], degrees: Sequence[int],
    durations: Sequence[float], pattern: GroovePattern | None = None,
    register: tuple[int, int] = (BASS_LOW, BASS_HIGH), strategy: str = "roots",
) -> tuple[NoteEvent, ...]:
    """Create root or alternating root/fifth attacks with explicit beat placement."""
    if len(degrees) != len(durations) or not degrees:
        raise ValueError("degrees and durations must be equally sized and non-empty")
    if strategy not in {"roots", "roots_and_fifths"}:
        raise ValueError("strategy must be roots or roots_and_fifths")
    low, high = register
    roots = harmonic_root_pitch_classes(tonic, scale_intervals, degrees)
    events: list[NoteEvent] = []
    elapsed = 0.0
    for root, duration in zip(roots, durations, strict=True):
        if duration <= 0:
            raise ValueError("durations must be positive")
        root_pitch = root_in_register(root, low, high, 40)
        if pattern is None:
            onsets = (0.0,)
        else:
            onsets = tuple(step / pattern.subdivisions_per_beat for step in pattern.active_steps
                           if step / pattern.subdivisions_per_beat < duration)
        for index, onset in enumerate(onsets):
            pc = (root + 7) % 12 if strategy == "roots_and_fifths" and index % 2 else root
            pitch = root_in_register(pc, low, high, root_pitch)
            note_duration = duration if pattern is None else min(.4, duration - onset)
            events.append(NoteEvent(pitch, elapsed + onset, note_duration, 88))
        elapsed += duration
    return tuple(events)


def connect_bass_targets(start_pitch: int, end_pitch: int, scale_pitch_classes: Sequence[int]) -> tuple[int, ...]:
    """Fill one ascending diatonic path, including both structural targets."""
    if end_pitch < start_pitch:
        raise ValueError("this narrow helper supports ascending connections only")
    pcs = {value % 12 for value in scale_pitch_classes}
    return tuple(pitch for pitch in range(start_pitch, end_pitch + 1) if pitch % 12 in pcs)
