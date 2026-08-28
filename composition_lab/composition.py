"""A deliberately narrow, pure composition pipeline for Chapter 27."""
from __future__ import annotations

from dataclasses import asdict, dataclass, replace
import json
from pathlib import Path
import random
from collections.abc import Mapping, Sequence

from .bass import bass_from_progression
from .evaluation import melody_profile
from .event_rendering import render_events
from .events import NoteEvent, composition_duration
from .groove import GroovePattern, groove_events, repeat_groove
from .harmonic_function import harmonic_function
from .osc import PlaybackChoice, build_osc_schedule
from .progressions import progression_chords, progression_roman_numerals
from .scales import MAJOR
from .texture import MusicalLayer, combine_event_layers
from .voice_leading import smooth_progression_voicings
from .waveform import write_wav


@dataclass(frozen=True)
class SectionSpec:
    label: str
    beats: float
    harmony_degrees: tuple[int, ...]
    melody_recipe: str
    active_layers: tuple[str, ...]


DEFAULT_SECTIONS = (
    SectionSpec("A", 8.0, (1, 4, 5, 1), "generate", ("melody", "harmony", "bass")),
    SectionSpec("A'", 8.0, (1, 4, 5, 1), "A register +12", ("melody", "harmony", "bass", "groove")),
    SectionSpec("B", 8.0, (6, 4, 2, 5), "generate contrasting contour", ("melody", "harmony", "bass", "groove")),
    SectionSpec("A", 8.0, (1, 4, 5, 1), "literal return", ("melody", "harmony", "bass")),
)


@dataclass(frozen=True)
class CompositionSpec:
    title: str = "Chapter 27 Study"
    bpm: float = 108.0
    tonic: int = 60
    mode: str = "major"
    sections: tuple[SectionSpec, ...] = DEFAULT_SECTIONS
    seed: int = 2026
    generator_strategy: str = "seeded constrained melody"
    pitch_range: tuple[int, int] = (60, 84)
    maximum_leap: int = 5

    @property
    def form(self) -> tuple[str, ...]:
        return tuple(section.label for section in self.sections)


@dataclass(frozen=True)
class SectionSpan:
    label: str
    instance: int
    start: float
    end: float


@dataclass(frozen=True)
class HarmonicSpan:
    section: str
    start: float
    duration: float
    degree: int
    roman_numeral: str
    function: str
    pitches: tuple[int, ...]


@dataclass(frozen=True)
class CompositionResult:
    spec: CompositionSpec
    sections: tuple[SectionSpan, ...]
    harmony: tuple[HarmonicSpan, ...]
    layers: tuple[MusicalLayer, ...]
    trace: tuple[str, ...]

    @property
    def duration(self) -> float:
        return self.sections[-1].end

    def layer(self, name: str) -> MusicalLayer:
        return next(layer for layer in self.layers if layer.name == name)

    def flattened(self) -> tuple[NoteEvent, ...]:
        return combine_event_layers(*self.layers)


TRACE = (
    "[1] validate specification", "[2] build form timeline",
    "[3] build symbolic harmonic plan and voice-led voicings",
    "[4] generate A melody with seeded constraints", "[5] transform A → A' by register +12",
    "[6] generate contrasting B", "[7] return literal A",
    "[8] build roots-and-fifths bass from harmony", "[9] build sustained accompaniment",
    "[10] activate deterministic groove by texture plan", "[11] assemble named layers",
    "[12] validate objective result invariants",
)


def validate_spec(spec: CompositionSpec) -> None:
    if spec.bpm <= 0:
        raise ValueError("bpm must be greater than zero")
    if spec.mode != "major":
        raise ValueError("mode unsupported in Chapter 27: only major is supported")
    if not 0 <= spec.tonic <= 103:
        raise ValueError("tonic must be between 0 and 103")
    if not spec.sections:
        raise ValueError("form must not be empty")
    if any(section.beats <= 0 for section in spec.sections):
        raise ValueError("section lengths must be positive")
    if any(not section.harmony_degrees or section.beats % len(section.harmony_degrees)
           for section in spec.sections):
        raise ValueError("each section must divide evenly among its harmony degrees")
    if spec.generator_strategy != "seeded constrained melody":
        raise ValueError("generator strategy unsupported in Chapter 27")
    if spec.maximum_leap < 0 or spec.pitch_range[0] > spec.pitch_range[1]:
        raise ValueError("invalid melody constraints")


def build_section_timeline(spec: CompositionSpec) -> tuple[SectionSpan, ...]:
    elapsed, occurrences, result = 0.0, {}, []
    for section in spec.sections:
        occurrences[section.label] = occurrences.get(section.label, 0) + 1
        result.append(SectionSpan(section.label, occurrences[section.label], elapsed, elapsed + section.beats))
        elapsed += section.beats
    return tuple(result)


def build_harmony_for_sections(spec: CompositionSpec, timeline: Sequence[SectionSpan]) -> tuple[HarmonicSpan, ...]:
    result = []
    for section, position in zip(spec.sections, timeline, strict=True):
        duration = section.beats / len(section.harmony_degrees)
        chords = progression_chords(spec.tonic, MAJOR, section.harmony_degrees)
        romans = progression_roman_numerals(spec.tonic, MAJOR, section.harmony_degrees)
        for index, (degree, chord, roman) in enumerate(zip(section.harmony_degrees, chords, romans, strict=True)):
            result.append(HarmonicSpan(section.label, position.start + index * duration, duration,
                                       degree, roman, harmonic_function(degree), chord))
    return tuple(result)


def _walk(seed: int, tonic: int, low: int, high: int, maximum_leap: int, descending: bool = False) -> tuple[int, ...]:
    scale = tuple(p for p in range(low, high + 1) if (p - tonic) % 12 in set(MAJOR[:-1]))
    rng, notes = random.Random(seed), [min(scale, key=lambda p: (abs(p - (tonic + 12)), p))]
    for _ in range(6):
        choices = [p for p in scale if 0 < abs(p - notes[-1]) <= maximum_leap]
        if descending:
            choices.sort(reverse=True)
            weights = [3 if p < notes[-1] else 1 for p in choices]
        else:
            weights = [1] * len(choices)
        notes.append(rng.choices(choices, weights=weights, k=1)[0])
    notes.append(min(scale, key=lambda p: (abs(p - (tonic + 12)), p)))
    return tuple(notes)


def build_melody_for_sections(spec: CompositionSpec, timeline: Sequence[SectionSpan]) -> MusicalLayer:
    low, high = spec.pitch_range
    a = _walk(spec.seed, spec.tonic, low, high - 12, spec.maximum_leap)
    b = _walk(spec.seed + 1, spec.tonic, low, high, spec.maximum_leap, descending=True)
    material = (a, tuple(p + 12 for p in a), b, a)
    events = tuple(NoteEvent(pitch, span.start + index, 1.0, 94)
                   for span, pitches in zip(timeline, material, strict=True)
                   for index, pitch in enumerate(pitches))
    return MusicalLayer("melody", events)


def build_bass_layer(spec: CompositionSpec, harmony: Sequence[HarmonicSpan]) -> MusicalLayer:
    degrees, durations = zip(*((span.degree, span.duration) for span in harmony), strict=True)
    pattern = GroovePattern(2, 1, (0, 1))
    return MusicalLayer("bass", bass_from_progression(spec.tonic, MAJOR, degrees, durations,
                                                       pattern, strategy="roots_and_fifths"))


def build_accompaniment_layer(harmony: Sequence[HarmonicSpan]) -> MusicalLayer:
    voicings = smooth_progression_voicings(tuple(span.pitches for span in harmony), (48, 84))
    events = tuple(NoteEvent(pitch, span.start, span.duration, 62)
                   for span, voicing in zip(harmony, voicings, strict=True) for pitch in voicing)
    return MusicalLayer("harmony", events)


def build_groove_layer(spec: CompositionSpec, timeline: Sequence[SectionSpan]) -> MusicalLayer:
    pattern = GroovePattern(2, 2, (0, 3), (70, 82))
    events = []
    for section, span in zip(spec.sections, timeline, strict=True):
        if "groove" in section.active_layers:
            events.extend(replace(event, start=event.start + span.start)
                          for event in repeat_groove(groove_events(pattern, 36), int(section.beats / 2), 2))
    return MusicalLayer("groove", tuple(events))


def validate_composition(result: CompositionResult) -> None:
    if {layer.name for layer in result.layers} != {"melody", "harmony", "bass", "groove"}:
        raise ValueError("required layers are missing")
    if any(event.start < 0 or event.duration <= 0 or event.start + event.duration > result.duration
           for event in result.flattened()):
        raise ValueError("events must remain inside the form timeline")
    if composition_duration(result.flattened()) != result.duration:
        raise ValueError("composition duration must equal form duration")


def compose(spec: CompositionSpec) -> CompositionResult:
    """Generate the complete symbolic score without I/O, sleep, or playback."""
    validate_spec(spec)
    timeline = build_section_timeline(spec)
    harmony = build_harmony_for_sections(spec, timeline)
    result = CompositionResult(spec, timeline, harmony, (
        build_melody_for_sections(spec, timeline), build_accompaniment_layer(harmony),
        build_bass_layer(spec, harmony), build_groove_layer(spec, timeline)), TRACE)
    validate_composition(result)
    return result


DEFAULT_PLAYBACK = {"melody": PlaybackChoice("articulated_saw", .15),
                    "harmony": PlaybackChoice("saw", -.15),
                    "bass": PlaybackChoice("sine", 0), "groove": PlaybackChoice("pulse", 0)}


def result_events_and_layers(result: CompositionResult) -> tuple[tuple[NoteEvent, ...], tuple[str, ...]]:
    pairs = sorted(((event, layer.name, li, ei) for li, layer in enumerate(result.layers)
                    for ei, event in enumerate(layer.events)), key=lambda x: (x[0].start, x[0].pitch, x[2], x[3]))
    return tuple(x[0] for x in pairs), tuple(x[1] for x in pairs)


def composition_osc_schedule(result: CompositionResult, playback: Mapping[str, PlaybackChoice] = DEFAULT_PLAYBACK,
                             *, bpm: float | None = None):
    events, layers = result_events_and_layers(result)
    return build_osc_schedule(events, layers, bpm=bpm or result.spec.bpm, playback_by_layer=playback)


def write_composition_artifacts(result: CompositionResult, output_directory: Path) -> tuple[Path, Path, Path, Path]:
    output_directory.mkdir(parents=True, exist_ok=True)
    composition_path = output_directory / "chapter_27_composition.json"
    manifest_path = output_directory / "chapter_27_manifest.json"
    wav_path = output_directory / "chapter_27_reference.wav"
    schedule_path = output_directory / "chapter_27_osc_schedule.json"
    data = {"specification": asdict(result.spec), "sections": [asdict(x) for x in result.sections],
            "harmony": [asdict(x) for x in result.harmony],
            "layers": [{"name": layer.name, "events": [asdict(e) for e in layer.events]} for layer in result.layers]}
    composition_path.write_text(json.dumps(data, indent=2, sort_keys=True) + "\n")
    manifest = {"chapter": 27, "seed": result.spec.seed, "tempo": result.spec.bpm,
                "tonic": result.spec.tonic, "mode": result.spec.mode, "form": result.spec.form,
                "generator_strategy": result.spec.generator_strategy,
                "layer_strategies": {"melody": "seeded constraints / explicit reuse", "harmony": "voice-led sustained",
                                     "bass": "roots_and_fifths", "groove": "deterministic section activation"}}
    manifest_path.write_text(json.dumps(manifest, indent=2, sort_keys=True) + "\n")
    write_wav(wav_path, render_events(result.flattened(), result.spec.bpm))
    events, layers = result_events_and_layers(result)
    schedule = composition_osc_schedule(result)
    rows = []
    for group in schedule:
        group_events = [(e, l) for e, l in zip(events, layers, strict=True) if e.start == group.beat]
        for message, (event, layer) in zip(group.messages, group_events, strict=True):
            rows.append({"time_seconds": group.at_seconds, "address": message.address,
                         "arguments": message.arguments, "layer": layer, "pitch": event.pitch})
    schedule_path.write_text(json.dumps(rows, indent=2, sort_keys=True) + "\n")
    return composition_path, manifest_path, wav_path, schedule_path
