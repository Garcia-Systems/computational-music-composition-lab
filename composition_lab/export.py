"""A small, inspectable file bridge from Python events to SuperCollider."""

from __future__ import annotations

from collections.abc import Sequence
import json
from pathlib import Path

from .events import NoteEvent
from .pitch import pitch_to_frequency


def events_as_records(
    events: Sequence[NoteEvent], *, layers: Sequence[str] | None = None
) -> list[dict[str, int | float | str]]:
    """Return deterministically onset-sorted event records.

    Sorting is stable, so simultaneous notes retain their supplied voice order.
    ``layer`` is optional descriptive metadata and has no synthesis behavior.
    """
    if layers is not None and len(layers) != len(events):
        raise ValueError("layers must contain one label per event")
    indexed = list(enumerate(events))
    indexed.sort(key=lambda item: (item[1].start, item[0]))
    records: list[dict[str, int | float | str]] = []
    for index, event in indexed:
        record: dict[str, int | float | str] = {
            "pitch": event.pitch,
            "frequency": pitch_to_frequency(event.pitch),
            "start": float(event.start),
            "duration": float(event.duration),
            "velocity": event.velocity,
        }
        if layers is not None:
            record["layer"] = layers[index]
        records.append(record)
    return records


def write_events_json(
    events: Sequence[NoteEvent], path: Path, *, layers: Sequence[str] | None = None
) -> Path:
    """Write the Chapter 22 JSON interchange format, creating parents."""
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(events_as_records(events, layers=layers), indent=2) + "\n",
        encoding="utf-8",
    )
    return path
