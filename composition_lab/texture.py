"""Small, inspectable accompaniment and texture tools for Chapter 15."""

from __future__ import annotations

from collections.abc import Iterable, Sequence
from dataclasses import dataclass

from .events import NoteEvent, shift_events
from .pitch import pitch_to_name


@dataclass(frozen=True)
class MusicalLayer:
    """Immutable events grouped by a compositional role, not an instrument."""

    name: str
    events: tuple[NoteEvent, ...]

    def __post_init__(self) -> None:
        if not self.name.strip():
            raise ValueError("layer name must not be empty")


def combine_event_layers(*layers: MusicalLayer | Iterable[NoteEvent]) -> tuple[NoteEvent, ...]:
    """Preserve and deterministically merge events; make no musical adjustments."""
    events = []
    for layer_index, layer in enumerate(layers):
        source = layer.events if isinstance(layer, MusicalLayer) else tuple(layer)
        events.extend((event, layer_index, event_index)
                      for event_index, event in enumerate(source))
    return tuple(item[0] for item in sorted(
        events, key=lambda item: (item[0].start, item[0].pitch, item[1], item[2])))


def shift_layer(layer: MusicalLayer, beats: float) -> MusicalLayer:
    """Return a shifted layer without changing the source layer or its events."""
    return MusicalLayer(layer.name, tuple(shift_events(layer.events, beats)))


def arpeggiate_voicing(
    pitches: Sequence[int], start: float, duration: float,
    pattern: Sequence[int], subdivisions: int, velocity: int = 70,
) -> tuple[NoteEvent, ...]:
    """Apply an explicit chord-index pattern to equal subdivisions of a span."""
    if not pitches or not pattern:
        raise ValueError("pitches and pattern must not be empty")
    if duration <= 0 or subdivisions <= 0:
        raise ValueError("duration and subdivisions must be positive")
    if len(pattern) != subdivisions:
        raise ValueError("pattern length must equal subdivisions")
    if any(isinstance(index, bool) or not isinstance(index, int)
           or index < 0 or index >= len(pitches) for index in pattern):
        raise ValueError("pattern indices must identify chord pitches")
    step = duration / subdivisions
    return tuple(NoteEvent(pitches[index], start + number * step, step, velocity)
                 for number, index in enumerate(pattern))


def repeated_chord_events(
    pitches: Sequence[int], start: float, duration: float,
    attacks_per_beat: float, velocity: int = 70,
) -> tuple[NoteEvent, ...]:
    """Re-attack a complete voicing regularly while chord identity stays fixed."""
    if duration <= 0 or attacks_per_beat <= 0:
        raise ValueError("duration and attacks_per_beat must be positive")
    attack_count = duration * attacks_per_beat
    if not attack_count.is_integer():
        raise ValueError("span must contain a whole number of attacks")
    step = 1 / attacks_per_beat
    return tuple(NoteEvent(pitch, start + attack * step, step, velocity)
                 for attack in range(int(attack_count)) for pitch in pitches)


def attack_density(events: Sequence[NoteEvent], beat_span: float) -> float:
    """Count distinct onset positions per beat, so a chord is one attack."""
    if beat_span <= 0:
        raise ValueError("beat_span must be positive")
    return len({event.start for event in events}) / beat_span


def attack_overlap(first: Sequence[NoteEvent], second: Sequence[NoteEvent]) -> tuple[int, int]:
    """Return shared and total distinct onset positions; this is not a quality score."""
    a, b = {event.start for event in first}, {event.start for event in second}
    return len(a & b), len(a | b)


def layer_metrics(layer: MusicalLayer) -> dict[str, object]:
    """Return only directly observable layer facts."""
    if not layer.events:
        return {"events": 0, "beat_span": 0.0, "register": None,
                "attacks_per_beat": 0.0, "average_velocity": 0.0}
    start = min(event.start for event in layer.events)
    end = max(event.start + event.duration for event in layer.events)
    span = end - start
    low, high = min(event.pitch for event in layer.events), max(event.pitch for event in layer.events)
    return {"events": len(layer.events), "beat_span": span,
            "register": (pitch_to_name(low), pitch_to_name(high)),
            "attacks_per_beat": len({event.start for event in layer.events}) / span,
            "average_velocity": sum(event.velocity for event in layer.events) / len(layer.events)}


def arrangement_timeline(layers: Sequence[MusicalLayer], boundaries: Sequence[float]) -> str:
    """Show whether each role sounds anywhere within each half-open beat window."""
    if len(boundaries) < 2 or any(a >= b for a, b in zip(boundaries, boundaries[1:])):
        raise ValueError("boundaries must be strictly increasing")
    windows = tuple(zip(boundaries, boundaries[1:]))
    header = "Beats       " + "  ".join(f"{a:g}–{b:g}" for a, b in windows)
    rows = [header]
    for layer in layers:
        marks = ["X" if any(event.start < b and event.start + event.duration > a
                            for event in layer.events) else "." for a, b in windows]
        rows.append(f"{layer.name.title():<11} " + "     ".join(marks))
    return "\n".join(rows)
