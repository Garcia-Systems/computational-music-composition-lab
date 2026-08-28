"""Small, immutable passage tools for repetition and variation studies."""

from __future__ import annotations

from collections.abc import Iterable, Sequence
from dataclasses import dataclass, replace

from .events import NoteEvent
from .motifs import motif_duration, normalize_events


@dataclass(frozen=True)
class Passage:
    """A display label and an immutable collection of musical events."""

    name: str
    events: tuple[NoteEvent, ...]

    def __post_init__(self) -> None:
        if not self.name.strip():
            raise ValueError("passage name must not be empty")


@dataclass(frozen=True)
class EventComparison:
    """Directly observable facts, with no aesthetic similarity judgment."""

    event_count_equal: bool
    duration_equal: bool
    pitch_sequence_equal: bool
    onset_sequence_equal: bool
    duration_sequence_equal: bool
    velocity_sequence_equal: bool


VARIATION_DIMENSIONS = ("pitch", "rhythm", "harmony", "bass", "groove", "texture", "register")


def passage_duration(events: Iterable[NoteEvent] | Passage) -> float:
    """Return latest end minus earliest onset, including simultaneous layers."""
    source = events.events if isinstance(events, Passage) else events
    return motif_duration(source)


def place_after(
    first: Iterable[NoteEvent] | Passage,
    second: Iterable[NoteEvent] | Passage,
    gap: float = 0.0,
) -> tuple[NoteEvent, ...]:
    """Append normalized second material after normalized first, immutably."""
    if gap < 0:
        raise ValueError("gap must be non-negative")
    a = tuple(normalize_events(first.events if isinstance(first, Passage) else first))
    b = normalize_events(second.events if isinstance(second, Passage) else second)
    return a + tuple(replace(event, start=event.start + passage_duration(a) + gap) for event in b)


def append_passages(*passages: Iterable[NoteEvent] | Passage, gap: float = 0.0) -> tuple[NoteEvent, ...]:
    """Place any number of normalized passages successively."""
    if gap < 0:
        raise ValueError("gap must be non-negative")
    score: tuple[NoteEvent, ...] = ()
    cursor = 0.0
    for index, passage in enumerate(passages):
        source = passage.events if isinstance(passage, Passage) else passage
        normalized = tuple(normalize_events(source))
        score += tuple(replace(event, start=event.start + cursor) for event in normalized)
        cursor += passage_duration(normalized)
        if index < len(passages) - 1:
            cursor += gap
    return score


def repeat_passage(events: Iterable[NoteEvent] | Passage, repetitions: int) -> tuple[NoteEvent, ...]:
    """Repeat a complete event collection, preserving every event property."""
    if isinstance(repetitions, bool) or not isinstance(repetitions, int) or repetitions < 0:
        raise ValueError("repetitions must be a non-negative integer")
    source = events.events if isinstance(events, Passage) else events
    return append_passages(*(tuple(source) for _ in range(repetitions)))


def compare_events(first: Sequence[NoteEvent], second: Sequence[NoteEvent]) -> EventComparison:
    """Compare normalized event collections using factual sequence equalities."""
    a, b = tuple(normalize_events(first)), tuple(normalize_events(second))
    return EventComparison(
        len(a) == len(b), passage_duration(a) == passage_duration(b),
        tuple(e.pitch for e in a) == tuple(e.pitch for e in b),
        tuple(e.start for e in a) == tuple(e.start for e in b),
        tuple(e.duration for e in a) == tuple(e.duration for e in b),
        tuple(e.velocity for e in a) == tuple(e.velocity for e in b),
    )


def variation_inventory(changed: Iterable[str]) -> dict[str, bool]:
    """Describe explicitly chosen changes rather than inventing a similarity score."""
    selected = frozenset(changed)
    unknown = selected.difference(VARIATION_DIMENSIONS)
    if unknown:
        raise ValueError(f"unknown variation dimensions: {', '.join(sorted(unknown))}")
    return {dimension: dimension in selected for dimension in VARIATION_DIMENSIONS}


def variation_matrix(rows: Sequence[tuple[str, Iterable[str]]]) -> str:
    """Format X (changed) and . (retained) for declared dimensions."""
    header = "       " + " ".join(f"{name.title():>8}" for name in VARIATION_DIMENSIONS)
    lines = [header]
    for label, changed in rows:
        facts = variation_inventory(changed)
        lines.append(f"{label:<7}" + " ".join(f"{'X' if facts[name] else '.':>8}" for name in VARIATION_DIMENSIONS))
    return "\n".join(lines)
