"""Small, pure motif transformations for Chapter 6."""

from __future__ import annotations

from collections.abc import Iterable, Sequence
from dataclasses import dataclass, replace

from .events import NoteEvent, shift_events, transpose_events


def _events(events: Iterable[NoteEvent]) -> tuple[NoteEvent, ...]:
    """Materialize an iterable once while retaining its supplied order."""
    return tuple(events)


def normalize_events(events: Iterable[NoteEvent]) -> list[NoteEvent]:
    """Return new events with the earliest onset at beat zero."""
    source = _events(events)
    if not source:
        return []
    earliest = min(event.start for event in source)
    return [replace(event, start=event.start - earliest) for event in source]


def motif_duration(events: Iterable[NoteEvent]) -> float:
    """Return latest end minus earliest onset, or zero for an empty motif."""
    source = _events(events)
    if not source:
        return 0.0
    earliest = min(event.start for event in source)
    latest_end = max(event.start + event.duration for event in source)
    return latest_end - earliest


def repeat_motif(motif: Iterable[NoteEvent], repetitions: int) -> list[NoteEvent]:
    """Place normalized, unchanged copies one motif span apart."""
    if isinstance(repetitions, bool) or not isinstance(repetitions, int) or repetitions < 0:
        raise ValueError("repetitions must be a non-negative integer")
    normalized = normalize_events(motif)
    span = motif_duration(normalized)
    return [
        replace(event, start=event.start + repetition * span)
        for repetition in range(repetitions)
        for event in normalized
    ]


def transpose_motif(motif: Iterable[NoteEvent], semitones: int) -> list[NoteEvent]:
    """Reuse score transposition to move a motif without changing its rhythm."""
    return transpose_events(motif, semitones)


def sequence_motif(
    motif: Iterable[NoteEvent], transpositions: Sequence[int]
) -> list[NoteEvent]:
    """Place chromatically transposed motif copies successively in time."""
    normalized = normalize_events(motif)
    span = motif_duration(normalized)
    return [
        replace(event, start=event.start + index * span)
        for index, semitones in enumerate(transpositions)
        for event in transpose_motif(normalized, semitones)
    ]


def retrograde_motif(motif: Iterable[NoteEvent]) -> list[NoteEvent]:
    """Reflect every event in the motif span, producing true temporal reversal."""
    normalized = normalize_events(motif)
    span = motif_duration(normalized)
    reflected = [
        replace(event, start=span - (event.start + event.duration))
        for event in normalized
    ]
    return sorted(reflected, key=lambda event: event.start)


def invert_motif(motif: Iterable[NoteEvent], axis_pitch: int) -> list[NoteEvent]:
    """Reflect pitches around an axis while leaving all performance data intact."""
    if isinstance(axis_pitch, bool) or not isinstance(axis_pitch, int):
        raise ValueError("axis_pitch must be an integer")
    return [replace(event, pitch=2 * axis_pitch - event.pitch) for event in motif]


def scale_motif_time(motif: Iterable[NoteEvent], factor: float) -> list[NoteEvent]:
    """Scale normalized starts and durations as one temporal structure."""
    if isinstance(factor, bool) or not isinstance(factor, (int, float)) or factor <= 0:
        raise ValueError("time factor must be greater than zero")
    return [
        replace(event, start=event.start * factor, duration=event.duration * factor)
        for event in normalize_events(motif)
    ]


def augment_motif(motif: Iterable[NoteEvent], factor: float = 2.0) -> list[NoteEvent]:
    """Expand a motif's complete temporal structure."""
    return scale_motif_time(motif, factor)


def diminish_motif(motif: Iterable[NoteEvent], factor: float = 0.5) -> list[NoteEvent]:
    """Contract a motif's complete temporal structure."""
    return scale_motif_time(motif, factor)


def displace_motif(motif: Iterable[NoteEvent], beats: float = 0.5) -> list[NoteEvent]:
    """Move a normalized motif relative to the beat grid."""
    if beats < 0:
        raise ValueError("displacement must keep starts non-negative")
    return shift_events(normalize_events(motif), beats)


@dataclass(frozen=True)
class DevelopmentSection:
    """An audible label and its exact location in the development study."""

    label: str
    start: float
    end: float


def build_development_study(
    motif: Iterable[NoteEvent],
) -> tuple[list[NoteEvent], tuple[DevelopmentSection, ...]]:
    """Combine related transformations into a transparent 33-beat study."""
    original = normalize_events(motif)
    units: tuple[tuple[str, list[NoteEvent]], ...] = (
        ("original", original),
        ("repeat", original),
        ("sequence 0, +2, +4, +5", sequence_motif(original, (0, 2, 4, 5))),
        ("retrograde twice", repeat_motif(retrograde_motif(original), 2)),
        ("augmentation ×2", augment_motif(original)),
        ("return", original),
    )
    cursor = 0.0
    score: list[NoteEvent] = []
    sections: list[DevelopmentSection] = []
    for label, events in units:
        span = motif_duration(events)
        score.extend(shift_events(events, cursor))
        sections.append(DevelopmentSection(label, cursor, cursor + span))
        cursor += span
    return score, tuple(sections)
