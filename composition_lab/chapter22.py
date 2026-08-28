"""Chapter 22 fixtures: composition data prepared for two synthesis engines."""

from __future__ import annotations

from pathlib import Path

from .event_rendering import render_events
from .events import NoteEvent
from .export import write_events_json
from .pitch import pitch_to_frequency, pitch_to_name
from .waveform import write_wav

TEMPO_BPM = 120.0
CHAPTER_22_EVENTS = (
    NoteEvent(60, 0, 1, 90), NoteEvent(64, 1, 1, 90),
    NoteEvent(67, 2, 1, 90), NoteEvent(72, 3, 1, 90),
    NoteEvent(60, 4, 2, 80), NoteEvent(64, 4, 2, 80),
    NoteEvent(67, 4, 2, 80),
)


def chapter_22_capstone() -> tuple[tuple[NoteEvent, ...], tuple[str, ...]]:
    """Return a modest 8-beat I-IV-V-I, melody, harmony, and bass study."""
    melody = tuple(NoteEvent(p, i, 1, 90) for i, p in enumerate((60, 64, 67, 72, 69, 67, 62, 60)))
    harmony_pitches = ((60, 64, 67), (65, 69, 72), (67, 71, 74), (60, 64, 67))
    harmony = tuple(
        NoteEvent(pitch, start, 2, 54)
        for start, chord in zip((0, 2, 4, 6), harmony_pitches, strict=True)
        for pitch in chord
    )
    bass = tuple(NoteEvent(pitch, start, 2, 64) for start, pitch in zip((0, 2, 4, 6), (36, 41, 43, 36), strict=True))
    events = melody + harmony + bass
    return events, ("melody",) * len(melody) + ("harmony",) * len(harmony) + ("bass",) * len(bass)


def render_chapter_22(output_directory: Path = Path("outputs")) -> tuple[Path, ...]:
    """Create JSON and Python-rendered controls without invoking SuperCollider."""
    capstone, layers = chapter_22_capstone()
    paths = (
        output_directory / "chapter_22_events.json",
        output_directory / "chapter_22_python_reference.wav",
        output_directory / "chapter_22_capstone_events.json",
        output_directory / "chapter_22_capstone_python_reference.wav",
    )
    write_events_json(CHAPTER_22_EVENTS, paths[0])
    write_wav(paths[1], render_events(CHAPTER_22_EVENTS, TEMPO_BPM))
    write_events_json(capstone, paths[2], layers=layers)
    write_wav(paths[3], render_events(capstone, TEMPO_BPM))
    return paths


def run_chapter_22(output_directory: Path = Path("outputs")) -> None:
    paths = render_chapter_22(output_directory)
    rows = "\n".join(
        f"{event.start:>5.1f}  {pitch_to_name(event.pitch):<5}  "
        f"{pitch_to_frequency(event.pitch):>9.3f}  {event.duration:>8.1f}  {event.velocity:>8}"
        for event in CHAPTER_22_EVENTS
    )
    capstone, _ = chapter_22_capstone()
    print(f"""Chapter 22 — From Notes to Sound

Composition remains in Python. Synthesis begins moving to SuperCollider.
Python prepares inspectable event data and a reference WAV; it does not launch sclang.

Events (start and duration are beats):
start  pitch  frequency  duration  velocity
{rows}

Pitch is converted once by Python's Chapter 1 pitch_to_frequency().
SuperCollider maps amp = (velocity / 127) * 0.15, leaving polyphonic headroom.

Created:
{chr(10).join(map(str, paths))}

Capstone: {len(capstone)} events across melody, harmony, and bass metadata; every layer uses the same sine instrument.

SuperCollider script:
supercollider/chapter_22_first_sound.scd

Open that script, boot the server, evaluate the SynthDef, then play either exported file.
SuperCollider playback is performed separately using the provided .scd file.
Same composition, different synthesis engine.""")
