"""Transparent phrase-building experiments for Chapter 7."""

from __future__ import annotations

from collections.abc import Iterable, Sequence
from dataclasses import dataclass, replace

from .events import NoteEvent, shift_events
from .motifs import normalize_events, transpose_motif


@dataclass(frozen=True)
class PhraseSection:
    """A designed role and its immutable events on the phrase timeline."""

    label: str
    events: tuple[NoteEvent, ...]

    @property
    def start(self) -> float:
        return min((event.start for event in self.events), default=0.0)

    @property
    def end(self) -> float:
        return max((event.start + event.duration for event in self.events), default=self.start)


def fragment_motif(
    motif: Sequence[NoteEvent], start_index: int, length: int
) -> tuple[NoteEvent, ...]:
    """Extract and normalize one small, consecutive piece of a motif."""
    if start_index < 0 or length <= 0:
        raise ValueError("start_index must be non-negative and length must be positive")
    return tuple(normalize_events(motif[start_index:start_index + length]))


def phrase_span(events: Iterable[NoteEvent]) -> float:
    """Measure latest end minus earliest onset, rather than summed durations."""
    source = tuple(events)
    if not source:
        return 0.0
    return max(e.start + e.duration for e in source) - min(e.start for e in source)


def place_after(
    existing: Iterable[NoteEvent], new_events: Iterable[NoteEvent], gap: float = 0.0
) -> tuple[NoteEvent, ...]:
    """Normalize material, place it after the current ending, and concatenate."""
    if gap < 0:
        raise ValueError("gap must be non-negative")
    first = tuple(existing)
    second = normalize_events(new_events)
    end = max((event.start + event.duration for event in first), default=0.0)
    return first + tuple(shift_events(second, end + gap))


def _notes(
    pitches: Sequence[int], start: float, step: float, duration: float,
    velocities: Sequence[int] | int,
) -> tuple[NoteEvent, ...]:
    values = (velocities,) * len(pitches) if isinstance(velocities, int) else velocities
    return tuple(
        NoteEvent(pitch, start + index * step, duration, velocity)
        for index, (pitch, velocity) in enumerate(zip(pitches, values, strict=True))
    )


def build_complete_phrase(motif: Sequence[NoteEvent]) -> tuple[tuple[NoteEvent, ...], tuple[PhraseSection, ...]]:
    """Build a sixteen-beat opening/continuation/climax/closing arc."""
    # The opening retains Chapter 6's pitches but establishes a spacious pulse.
    opening = _notes(tuple(e.pitch for e in motif), 0, 1, .8, (70, 72, 74, 76))
    fragment = fragment_motif(motif, 0, 2)
    # Chapter 6 transposition supplies related, rising two-note cells.
    cells = [transpose_motif(fragment, amount) for amount in (0, 2, 4, 5)]
    continuation = tuple(
        NoteEvent(event.pitch, 4 + cell_index + note_index * .5, .42, 80 + cell_index * 3)
        for cell_index, cell in enumerate(cells)
        for note_index, event in enumerate(cell)
    )
    climax = _notes((69, 72), 8, 1, (.8), (96, 105))
    closing = (
        NoteEvent(67, 10, 1, 84), NoteEvent(64, 11, 1, 80),
        NoteEvent(62, 12, 1, 77), NoteEvent(60, 13, 3, 74),
    )
    sections = tuple(
        PhraseSection(label, tuple(events)) for label, events in (
            ("opening", opening), ("continuation", continuation),
            ("climax", climax), ("closing", closing),
        )
    )
    return tuple(event for section in sections for event in section.events), sections


def build_flat_phrase(motif: Sequence[NoteEvent]) -> tuple[NoteEvent, ...]:
    """Use related material at stable register, density, and velocity."""
    pitches = tuple(e.pitch for e in motif) * 4
    return _notes(pitches, 0, 1, .8, 76)


def build_question(answer: bool = False, final_duration: float = 2.0) -> tuple[NoteEvent, ...]:
    """Build related eight-beat phrases differing principally at their ending."""
    if final_duration <= 0:
        raise ValueError("final_duration must be positive")
    pitches = (60, 62, 64, 67, 65, 64, 62 if not answer else 60)
    events = list(_notes(pitches, 0, 1, .8, (72, 74, 76, 80, 78, 76, 74)))
    events[-1] = replace(events[-1], duration=final_duration)
    return tuple(events)


def ending_variant(final_pitch: int = 60, final_duration: float = 2.0) -> tuple[NoteEvent, ...]:
    """Hold the lead-in constant while changing only final pitch or duration."""
    lead = _notes((60, 62, 64, 67, 65, 64), 0, 1, .8, 76)
    return lead + (NoteEvent(final_pitch, 6, final_duration, 74),)
