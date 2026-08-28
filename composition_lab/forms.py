"""Small, transparent section and form assembly tools."""

from __future__ import annotations

from collections.abc import Mapping, Sequence
from dataclasses import dataclass, replace

from .events import NoteEvent
from .motifs import motif_duration, normalize_events


@dataclass(frozen=True)
class Section:
    """A label, optional role, and locally normalized immutable content."""

    label: str
    events: tuple[NoteEvent, ...]
    role: str | None = None

    def __post_init__(self) -> None:
        if not isinstance(self.label, str) or not self.label.strip():
            raise ValueError("section label must not be empty")
        object.__setattr__(self, "events", tuple(normalize_events(self.events)))

    @property
    def duration(self) -> float:
        """Return timeline span, not the sum of overlapping durations."""
        return motif_duration(self.events)


@dataclass(frozen=True)
class SectionPlacement:
    """Objective placement facts for one occurrence in a form."""

    label: str
    start: float
    end: float
    duration: float


@dataclass(frozen=True)
class FormAssembly:
    """The audible timeline and its inspectable section placements."""

    events: tuple[NoteEvent, ...]
    placements: tuple[SectionPlacement, ...]

    @property
    def duration(self) -> float:
        return max((placement.end for placement in self.placements), default=0.0)


def assemble_form(
    plan: Sequence[str], sections: Mapping[str, Section],
    gaps: Sequence[float] | None = None,
) -> FormAssembly:
    """Place named reusable sections successively without editing their sources."""
    order = tuple(plan)
    if not order:
        raise ValueError("form plan must contain at least one section")
    missing = tuple(label for label in order if label not in sections)
    if missing:
        raise ValueError(f"unknown section label: {missing[0]}")
    transitions = (0.0,) * (len(order) - 1) if gaps is None else tuple(gaps)
    if len(transitions) != len(order) - 1:
        raise ValueError("gaps must contain one value between each pair of sections")
    if any(isinstance(gap, bool) or not isinstance(gap, (int, float)) or gap < 0 for gap in transitions):
        raise ValueError("gaps must be non-negative numbers")

    cursor = 0.0
    score: list[NoteEvent] = []
    placements: list[SectionPlacement] = []
    for index, label in enumerate(order):
        section = sections[label]
        start, end = cursor, cursor + section.duration
        score.extend(replace(event, start=event.start + start) for event in section.events)
        placements.append(SectionPlacement(label, start, end, section.duration))
        cursor = end + (transitions[index] if index < len(transitions) else 0.0)
    return FormAssembly(tuple(score), tuple(placements))


assemble_sections = assemble_form


def bars_to_beats(bars: int, beats_per_bar: int = 4) -> float:
    """Convert a small bar count to beats without creating a meter system."""
    if isinstance(bars, bool) or not isinstance(bars, int) or bars < 0:
        raise ValueError("bars must be a non-negative integer")
    if isinstance(beats_per_bar, bool) or not isinstance(beats_per_bar, int) or beats_per_bar <= 0:
        raise ValueError("beats_per_bar must be a positive integer")
    return float(bars * beats_per_bar)


def form_timeline(assembly: FormAssembly) -> str:
    """Format section placement facts for command-line inspection."""
    rows = ["Section  Start  End  Duration"]
    rows.extend(f"{p.label:<8} {p.start:>5g}  {p.end:>3g}  {p.duration:>8g}" for p in assembly.placements)
    return "\n".join(rows)


def section_proportions(assembly: FormAssembly) -> tuple[tuple[str, float], ...]:
    """Return occurrence proportions as objective percentages."""
    total = assembly.duration
    return tuple((p.label, 0.0 if total == 0 else 100 * p.duration / total) for p in assembly.placements)
