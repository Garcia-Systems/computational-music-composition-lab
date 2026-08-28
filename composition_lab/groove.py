"""Transparent, beat-relative structures for Chapter 13 groove experiments."""

from __future__ import annotations

from collections.abc import Iterable, Sequence
from dataclasses import dataclass
from math import ceil, isclose

from .events import NoteEvent


def subdivision_positions(
    beats_per_cycle: int, subdivisions_per_beat: int
) -> tuple[float, ...]:
    """Return grid onsets, excluding the cycle's end boundary."""
    if isinstance(beats_per_cycle, bool) or not isinstance(beats_per_cycle, int) or beats_per_cycle <= 0:
        raise ValueError("beats_per_cycle must be a positive integer")
    if (isinstance(subdivisions_per_beat, bool)
            or not isinstance(subdivisions_per_beat, int)
            or subdivisions_per_beat <= 0):
        raise ValueError("subdivisions_per_beat must be a positive integer")
    return tuple(step / subdivisions_per_beat
                 for step in range(beats_per_cycle * subdivisions_per_beat))


@dataclass(frozen=True)
class GroovePattern:
    """One inspectable groove cycle: grid, selected steps, and optional accents."""

    cycle_beats: float
    subdivisions_per_beat: int
    active_steps: tuple[int, ...]
    velocities: tuple[int, ...] | None = None

    def __post_init__(self) -> None:
        if isinstance(self.cycle_beats, bool) or not isinstance(self.cycle_beats, (int, float)) or self.cycle_beats <= 0:
            raise ValueError("cycle_beats must be greater than zero")
        if (isinstance(self.subdivisions_per_beat, bool)
                or not isinstance(self.subdivisions_per_beat, int)
                or self.subdivisions_per_beat <= 0):
            raise ValueError("subdivisions_per_beat must be a positive integer")
        step_count = self.cycle_beats * self.subdivisions_per_beat
        if not float(step_count).is_integer():
            raise ValueError("cycle_beats must contain a whole number of subdivisions")
        if any(isinstance(step, bool) or not isinstance(step, int)
               or step < 0 or step >= int(step_count) for step in self.active_steps):
            raise ValueError("active steps must be integer indices inside the cycle")
        if len(set(self.active_steps)) != len(self.active_steps):
            raise ValueError("active steps must not repeat")
        if self.velocities is not None:
            if len(self.velocities) != len(self.active_steps):
                raise ValueError("velocity count must match active-step count")
            if any(isinstance(value, bool) or not isinstance(value, int)
                   or not 0 <= value <= 127 for value in self.velocities):
                raise ValueError("velocities must be integers between 0 and 127")

    @property
    def step_count(self) -> int:
        return int(self.cycle_beats * self.subdivisions_per_beat)


def groove_events(
    pattern: GroovePattern, pitch: int = 60, start: float = 0.0,
    note_duration: float = 0.1, default_velocity: int = 90,
) -> tuple[NoteEvent, ...]:
    """Turn each selected grid step into a beat-based ``NoteEvent``."""
    velocities = pattern.velocities or (default_velocity,) * len(pattern.active_steps)
    return tuple(NoteEvent(pitch, start + step / pattern.subdivisions_per_beat,
                           note_duration, velocity)
                 for step, velocity in zip(pattern.active_steps, velocities, strict=True))


def repeat_groove(
    events: Sequence[NoteEvent], repetitions: int, cycle_beats: float
) -> tuple[NoteEvent, ...]:
    """Repeat already-built cycle events at exact cycle-length offsets."""
    if isinstance(repetitions, bool) or not isinstance(repetitions, int) or repetitions < 0:
        raise ValueError("repetitions must be a non-negative integer")
    if cycle_beats <= 0:
        raise ValueError("cycle_beats must be greater than zero")
    return tuple(NoteEvent(event.pitch, event.start + cycle * cycle_beats,
                           event.duration, event.velocity)
                 for cycle in range(repetitions) for event in events)


def is_on_beat(position: float) -> bool:
    """Report integer positions in the chapter's regular beat model."""
    return position >= 0 and isclose(position, round(position), abs_tol=1e-9)


def is_offbeat_eighth(position: float) -> bool:
    """Report '&' positions in the chapter's straight-eighth-note model."""
    return position >= 0 and isclose(position % 1.0, 0.5, abs_tol=1e-9)


def crosses_beat(event: NoteEvent) -> bool:
    """Report whether an event sustains through an integer beat after its onset."""
    next_beat = ceil(event.start)
    if isclose(next_beat, event.start):
        next_beat += 1
    return next_beat < event.start + event.duration


def events_per_beat(events: Sequence[NoteEvent], cycle_beats: float) -> float:
    """Return objective attack density; this is not a groove-quality score."""
    if cycle_beats <= 0:
        raise ValueError("cycle_beats must be greater than zero")
    return len(events) / cycle_beats


def combine_layers(*layers: Iterable[NoteEvent]) -> tuple[NoteEvent, ...]:
    """Combine role layers while retaining simultaneous attacks."""
    return tuple(sorted((event for layer in layers for event in layer),
                        key=lambda event: (event.start, event.pitch)))


def pattern_grid(pattern: GroovePattern) -> str:
    """Draw selected and silent positions as plain text."""
    active = set(pattern.active_steps)
    return " ".join("X" if step in active else "." for step in range(pattern.step_count))


def eighth_grid_labels(beats_per_cycle: int = 4) -> str:
    """Label the narrow straight-eighth grid used throughout Chapter 13."""
    if beats_per_cycle <= 0:
        raise ValueError("beats_per_cycle must be greater than zero")
    return " ".join(item for beat in range(1, beats_per_cycle + 1) for item in (str(beat), "&"))
