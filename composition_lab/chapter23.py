"""Chapter 23 fixtures: one composition, explicitly separate timbre maps."""

from __future__ import annotations

import json
from pathlib import Path
from collections.abc import Mapping, Sequence

from .chapter22 import CHAPTER_22_EVENTS, chapter_22_capstone
from .events import NoteEvent
from .export import write_events_json

SUPPORTED_INSTRUMENTS = frozenset({"sine", "saw", "pulse", "two_partial", "detuned_saw"})
ALL_SINE_INSTRUMENT_MAP = {"melody": "sine", "harmony": "sine", "bass": "sine"}
COLORED_INSTRUMENT_MAP = {"melody": "pulse", "harmony": "two_partial", "bass": "detuned_saw"}


def validate_instrument(name: str) -> str:
    """Return a supported metadata name, rejecting executable/arbitrary input."""
    if name not in SUPPORTED_INSTRUMENTS:
        raise ValueError(f"unsupported instrument {name!r}; choose from {sorted(SUPPORTED_INSTRUMENTS)}")
    return name


def instrument_metadata(events: Sequence[NoteEvent], instrument: str = "sine") -> tuple[str, ...]:
    """Assign playback metadata without changing any NoteEvent."""
    return (validate_instrument(instrument),) * len(events)


def write_instrument_map(mapping: Mapping[str, str], path: Path) -> Path:
    """Validate and deterministically serialize an explicit layer mapping."""
    validated = {layer: validate_instrument(mapping[layer]) for layer in sorted(mapping)}
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(validated, indent=2) + "\n", encoding="utf-8")
    return path


def render_chapter_23(output_directory: Path = Path("outputs")) -> tuple[Path, ...]:
    """Write composition and alternative playback specifications; require no SC."""
    capstone, layers = chapter_22_capstone()
    paths = (
        output_directory / "chapter_23_melody_events.json",
        output_directory / "chapter_23_capstone_events.json",
        output_directory / "chapter_23_instrument_map_all_sine.json",
        output_directory / "chapter_23_instrument_map_colored.json",
    )
    write_events_json(CHAPTER_22_EVENTS[:4], paths[0])
    write_events_json(capstone, paths[1], layers=layers)
    write_instrument_map(ALL_SINE_INSTRUMENT_MAP, paths[2])
    write_instrument_map(COLORED_INSTRUMENT_MAP, paths[3])
    return paths


def run_chapter_23(output_directory: Path = Path("outputs")) -> None:
    paths = render_chapter_23(output_directory)
    print("""Chapter 23 — Synthesizers as Instruments

The notes can stay the same while the synthesizer changes.
PITCH asks what periodic rate we hear; TIMBRE asks what spectral and temporal structure accompanies it.

Melody: C4 E4 G4 C5
Available Chapter 23 instruments:
sine, saw, pulse, two_partial, detuned_saw

Colored layer mapping:
melody -> pulse
harmony -> two_partial
bass -> detuned_saw

Created:
{}

The capstone event file is shared by both instrument maps: WHAT IS PLAYED remains separate from HOW IT SOUNDS.
SuperCollider: supercollider/chapter_23_synthesizers_as_instruments.scd
SuperCollider is optional and is not launched by this command.""".format("\n".join(map(str, paths))))
