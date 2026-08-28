"""Chapter 24: articulation metadata kept separate from musical events."""

from __future__ import annotations

from collections.abc import Mapping, Sequence
import json
from pathlib import Path

from .chapter22 import TEMPO_BPM, chapter_22_capstone
from .events import NoteEvent
from .export import write_events_json
from .pitch import pitch_to_name
from .rhythm import beats_to_seconds

ARTICULATIONS = {"short": 0.5, "normal": 0.85, "sustained": 1.0}

BASIC_PLAYBACK = {
    "tempo_bpm": TEMPO_BPM,
    "layers": {
        "bass": {"instrument": "simple_saw", "gate_ratio": 0.85},
        "harmony": {"instrument": "simple_saw", "gate_ratio": 0.85},
        "melody": {"instrument": "simple_saw", "gate_ratio": 0.85},
    },
}

ARTICULATED_PLAYBACK = {
    "tempo_bpm": TEMPO_BPM,
    "layers": {
        "bass": {"instrument": "filtered_saw", "articulation": "normal", "gate_ratio": 0.85,
                 "envelope": "sustained", "base_cutoff": 550, "rq": 0.7},
        "harmony": {"instrument": "filter_env_saw", "articulation": "sustained", "gate_ratio": 1.0,
                    "envelope": "slow_attack", "base_cutoff": 900, "rq": 0.8},
        "melody": {"instrument": "filter_env_saw", "articulation": "short", "gate_ratio": 0.5,
                   "envelope": "short", "base_cutoff": 700, "rq": 0.5,
                   "velocity_cutoff_range": 1800},
    },
}


def validate_gate_ratio(gate_ratio: float) -> float:
    """Validate a non-overlapping gate fraction."""
    if isinstance(gate_ratio, bool) or not isinstance(gate_ratio, (int, float)):
        raise ValueError("gate_ratio must be a number")
    if not 0 < gate_ratio <= 1:
        raise ValueError("gate_ratio must be greater than 0 and at most 1")
    return float(gate_ratio)


def gate_duration_beats(event: NoteEvent, gate_ratio: float) -> float:
    """Return playback gate length without mutating compositional duration."""
    return event.duration * validate_gate_ratio(gate_ratio)


def velocity_normalized(velocity: int) -> float:
    """Map MIDI velocity to 0..1 before the synth's conservative gain scale."""
    if isinstance(velocity, bool) or not isinstance(velocity, int) or not 0 <= velocity <= 127:
        raise ValueError("velocity must be an integer between 0 and 127")
    return velocity / 127


def write_playback_configuration(configuration: Mapping, path: Path) -> Path:
    """Validate the small Chapter 24 playback document and serialize it."""
    layers = configuration.get("layers")
    if not isinstance(layers, Mapping):
        raise ValueError("playback configuration requires a layers mapping")
    for settings in layers.values():
        validate_gate_ratio(settings["gate_ratio"])
        if "base_cutoff" in settings and settings["base_cutoff"] <= 0:
            raise ValueError("base_cutoff must be positive")
        if "rq" in settings and not 0.1 <= settings["rq"] <= 1.0:
            raise ValueError("rq must be between 0.1 and 1.0 for these presets")
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(configuration, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return path


def render_chapter_24(output_directory: Path = Path("outputs")) -> tuple[Path, ...]:
    """Write one composition and two alternative rendering specifications."""
    events, layers = chapter_22_capstone()
    paths = (
        output_directory / "chapter_24_capstone_events.json",
        output_directory / "chapter_24_basic_playback.json",
        output_directory / "chapter_24_articulated_playback.json",
    )
    write_events_json(events, paths[0], layers=layers)
    write_playback_configuration(BASIC_PLAYBACK, paths[1])
    write_playback_configuration(ARTICULATED_PLAYBACK, paths[2])
    return paths


def articulation_table(events: Sequence[NoteEvent], gate_ratio: float, tempo_bpm: float) -> str:
    rows = ["Pitch  Start  Nominal Duration  Gate Ratio  Gate Beats  Gate Seconds"]
    for event in events:
        gate_beats = gate_duration_beats(event, gate_ratio)
        rows.append(f"{pitch_to_name(event.pitch):<5}  {event.start:>5.1f}  {event.duration:>16.1f}  "
                    f"{gate_ratio:>10.2f}  {gate_beats:>10.2f}  "
                    f"{beats_to_seconds(gate_beats, tempo_bpm):>12.2f}")
    return "\n".join(rows)


def run_chapter_24(output_directory: Path = Path("outputs")) -> None:
    paths = render_chapter_24(output_directory)
    events, _ = chapter_22_capstone()
    print(f"""Chapter 24 — Envelopes, Filters, and Articulation

Same notes. Different sound behavior.
Tempo: {TEMPO_BPM:g} BPM (one beat = {beats_to_seconds(1, TEMPO_BPM):.2f} seconds)

Articulation describes how an event is shaped and separated from its neighbors.
Compositional duration remains in NoteEvent; gate ratio determines gate-off.
Attack, decay, and release are instrument times in seconds. Release may continue after gate-off.

Articulation presets:
short      gate ratio {ARTICULATIONS['short']:.2f}
normal     gate ratio {ARTICULATIONS['normal']:.2f}
sustained  gate ratio {ARTICULATIONS['sustained']:.2f}

{articulation_table(events[:4], ARTICULATIONS['short'], TEMPO_BPM)}

Created:
{chr(10).join(map(str, paths))}

The event file is shared: basic and articulated JSON describe rendering only.
SuperCollider: supercollider/chapter_24_envelopes_filters_articulation.scd
SuperCollider is optional and is not launched by this command.""")
