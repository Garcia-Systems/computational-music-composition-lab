"""Chapter 25: spatial playback metadata and shared-effect configuration."""

from __future__ import annotations

from dataclasses import asdict, dataclass
import json
from pathlib import Path
from typing import Mapping

from .chapter22 import TEMPO_BPM, chapter_22_capstone
from .events import NoteEvent
from .export import write_events_json
from .rhythm import beats_to_seconds


def _unit_value(name: str, value: float) -> float:
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        raise ValueError(f"{name} must be a number")
    if not 0 <= value <= 1:
        raise ValueError(f"{name} must be between 0 and 1")
    return float(value)


@dataclass(frozen=True)
class LayerPlayback:
    """Per-layer rendering choices; none of these fields creates a note."""

    instrument: str
    gate_ratio: float = 0.9
    pan: float = 0.0
    delay_send: float = 0.0
    reverb_send: float = 0.0

    def __post_init__(self) -> None:
        if not self.instrument:
            raise ValueError("instrument must not be empty")
        if isinstance(self.gate_ratio, bool) or not 0 < self.gate_ratio <= 1:
            raise ValueError("gate_ratio must be greater than 0 and at most 1")
        if isinstance(self.pan, bool) or not isinstance(self.pan, (int, float)) or not -1 <= self.pan <= 1:
            raise ValueError("pan must be between -1 and 1")
        _unit_value("delay_send", self.delay_send)
        _unit_value("reverb_send", self.reverb_send)


@dataclass(frozen=True)
class DelaySettings:
    delay_beats: float = 0.5
    feedback: float = 0.35
    return_amp: float = 0.35

    def __post_init__(self) -> None:
        if isinstance(self.delay_beats, bool) or not isinstance(self.delay_beats, (int, float)) or self.delay_beats <= 0:
            raise ValueError("delay_beats must be greater than zero")
        if isinstance(self.feedback, bool) or not isinstance(self.feedback, (int, float)) or not 0 <= self.feedback < 1:
            raise ValueError("feedback must be at least 0 and strictly less than 1")
        _unit_value("return_amp", self.return_amp)


@dataclass(frozen=True)
class ReverbSettings:
    room: float = 0.5
    damp: float = 0.4
    return_amp: float = 0.3

    def __post_init__(self) -> None:
        _unit_value("room", self.room)
        _unit_value("damp", self.damp)
        _unit_value("return_amp", self.return_amp)


DRY_LAYERS = {
    name: LayerPlayback("routed_saw", gate_ratio=ratio)
    for name, ratio in (("melody", 0.5), ("harmony", 1.0), ("bass", 0.85))
}
SPATIAL_LAYERS = {
    "melody": LayerPlayback("routed_saw", 0.5, 0.2, 0.15, 0.30),
    "harmony": LayerPlayback("routed_saw", 1.0, -0.3, 0.05, 0.38),
    "bass": LayerPlayback("routed_saw", 0.85, 0.0, 0.0, 0.10),
}
DELAY = DelaySettings()
REVERB = ReverbSettings()


def chapter_25_capstone() -> tuple[tuple[NoteEvent, ...], tuple[str, ...]]:
    """Extend the existing I-IV-V-I study to 16 beats without new theory."""
    events, layers = chapter_22_capstone()
    repeated = tuple(NoteEvent(e.pitch, e.start + 8, e.duration, e.velocity) for e in events)
    return events + repeated, layers + layers


def playback_document(layers: Mapping[str, LayerPlayback]) -> dict:
    return {"tempo_bpm": TEMPO_BPM, "layers": {name: asdict(value) for name, value in layers.items()}}


def effects_document(delay: DelaySettings = DELAY, reverb: ReverbSettings = REVERB) -> dict:
    """Serialize global effects once, including the derived physical delay time."""
    return {
        "tempo_bpm": TEMPO_BPM,
        "delay": {**asdict(delay), "delay_seconds": beats_to_seconds(delay.delay_beats, TEMPO_BPM)},
        "reverb": asdict(reverb),
        "routing": "wet-only send/return",
    }


def _write_json(document: Mapping, path: Path) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(document, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return path


def render_chapter_25(output_directory: Path = Path("outputs")) -> tuple[Path, ...]:
    events, layers = chapter_25_capstone()
    paths = (
        output_directory / "chapter_25_capstone_events.json",
        output_directory / "chapter_25_playback_map.json",
        output_directory / "chapter_25_effects.json",
    )
    write_events_json(events, paths[0], layers=layers)
    _write_json({"dry": playback_document(DRY_LAYERS), "spatial": playback_document(SPATIAL_LAYERS)}, paths[1])
    _write_json(effects_document(), paths[2])
    return paths


def run_chapter_25(output_directory: Path = Path("outputs")) -> None:
    paths = render_chapter_25(output_directory)
    rows = "\n".join(
        f"{name.title():<10} {settings.pan:>5.1f} {settings.delay_send:>12.2f} {settings.reverb_send:>14.2f}"
        for name, settings in SPATIAL_LAYERS.items()
    )
    seconds = beats_to_seconds(DELAY.delay_beats, TEMPO_BPM)
    print(f"""Chapter 25 — Space, Delay, Reverb, and Signal Routing

Composition: unchanged NoteEvents. Pan and sends are playback metadata.
Dry signal is the original instrument signal; wet signal has passed through an effect.
Final output = dry signal + wet-only delay return + wet-only reverb return.

Tempo: {TEMPO_BPM:g} BPM
Delay: {DELAY.delay_beats:g} beats = {seconds:.2f} seconds; feedback {DELAY.feedback:.2f} (< 1)
Reverb: room {REVERB.room:.2f}; damp {REVERB.damp:.2f}; shared, persistent return

Layer      Pan   Delay Send    Reverb Send
{rows}

Created:
{chr(10).join(map(str, paths))}

An echo is processed audio, not a new NoteEvent: composed repetition != delay repetition.
SuperCollider: supercollider/chapter_25_space_and_effects.scd
SuperCollider is optional and is not launched by this command. No OSC is used.""")
