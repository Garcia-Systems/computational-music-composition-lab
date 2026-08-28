"""Structured musical events and small, immutable transformations."""

from __future__ import annotations

from collections.abc import Iterable, Sequence
from dataclasses import dataclass, replace

from .pitch import pitch_to_name, transpose_pitch


@dataclass(frozen=True)
class NoteEvent:
    """A pitched event positioned on a beat-based composition timeline."""

    pitch: int
    start: float
    duration: float
    velocity: int = 90

    def __post_init__(self) -> None:
        if isinstance(self.pitch, bool) or not isinstance(self.pitch, int):
            raise ValueError("pitch must be an integer between 0 and 127")
        if not 0 <= self.pitch <= 127:
            raise ValueError("pitch must be between 0 and 127")
        if not isinstance(self.start, (int, float)) or isinstance(self.start, bool):
            raise ValueError("start must be a number greater than or equal to zero")
        if self.start < 0:
            raise ValueError("start must be greater than or equal to zero")
        if not isinstance(self.duration, (int, float)) or isinstance(self.duration, bool):
            raise ValueError("duration must be a number greater than zero")
        if self.duration <= 0:
            raise ValueError("duration must be greater than zero")
        if isinstance(self.velocity, bool) or not isinstance(self.velocity, int):
            raise ValueError("velocity must be an integer between 0 and 127")
        if not 0 <= self.velocity <= 127:
            raise ValueError("velocity must be between 0 and 127")


def transpose_event(event: NoteEvent, semitones: int) -> NoteEvent:
    """Return a new event moved in pitch."""
    return replace(event, pitch=transpose_pitch(event.pitch, semitones))


def shift_event(event: NoteEvent, beats: float) -> NoteEvent:
    """Return a new event moved on the timeline."""
    return replace(event, start=event.start + beats)


def scale_velocity(event: NoteEvent, factor: float) -> NoteEvent:
    """Return a new event with velocity scaled and limited to 0--127."""
    if factor < 0:
        raise ValueError("velocity factor must be greater than or equal to zero")
    return replace(event, velocity=min(127, round(event.velocity * factor)))


def transpose_events(events: Iterable[NoteEvent], semitones: int) -> list[NoteEvent]:
    """Transpose a score without changing its original events."""
    return [transpose_event(event, semitones) for event in events]


def shift_events(events: Iterable[NoteEvent], beats: float) -> list[NoteEvent]:
    """Shift a score without changing its original events."""
    return [shift_event(event, beats) for event in events]


def composition_duration(events: Iterable[NoteEvent]) -> float:
    """Return the latest event end in beats, or zero for an empty score."""
    return max((event.start + event.duration for event in events), default=0.0)


def inspect_events(events: Sequence[NoteEvent]) -> str:
    """Format a score as a small, human-readable data table."""
    rows = ["Pitch  Name  Start  Duration  Velocity"]
    rows.extend(
        f"{event.pitch:<5}  {pitch_to_name(event.pitch):<4}  "
        f"{event.start:>5.2f}  {event.duration:>8.2f}  {event.velocity:>8}"
        for event in events
    )
    return "\n".join(rows)
