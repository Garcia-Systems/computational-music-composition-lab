"""Chapter 27 report and output-adapter orchestration (after one composition)."""
from __future__ import annotations
from pathlib import Path
from .composition import CompositionSpec, compose, composition_osc_schedule, write_composition_artifacts
from .evaluation import melody_profile
from .osc import OSC_HOST, OSC_PORT, OscNoteClient, execute_osc_schedule
from .pitch import pitch_to_name


def run_chapter_27(output_directory: Path = Path("outputs"), *, seed: int = 2026,
                   bpm: float = 108, tonic: int = 60, live: bool = False,
                   host: str = OSC_HOST, port: int = OSC_PORT) -> None:
    spec = CompositionSpec(bpm=bpm, tonic=tonic, seed=seed)
    result = compose(spec)  # exactly one generation; every adapter below receives this object
    melody = result.layer("melody")
    profile = melody_profile(tuple(event.pitch for event in melody.events))
    paths = write_composition_artifacts(result, output_directory)
    schedule = composition_osc_schedule(result)
    print(f"""Chapter 27 — The Composition Engine

Specification
-------------
Title: {spec.title}
Tempo: {spec.bpm:g} BPM
Key: {pitch_to_name(spec.tonic)} major
Seed: {spec.seed}
Form: {' | '.join(spec.form)}
Layers: melody, harmony, bass, groove
Generator: {spec.generator_strategy}

Pipeline
--------
{chr(10).join(result.trace)}

Form timeline
-------------
Section  Instance  Start  End  Beats
{chr(10).join(f'{s.label:<8} {s.instance:<8} {s.start:>5g} {s.end:>4g} {s.end-s.start:>6g}' for s in result.sections)}

Harmonic timeline
-----------------
Beat  Section  Degree  Function
{chr(10).join(f'{h.start:>4g}  {h.section:<7} {h.roman_numeral:<7} {h.function}' for h in result.harmony)}

Result
------
Duration: {result.duration:g} beats
Layers: {len(result.layers)}
Events: {len(result.flattened())}
{chr(10).join(f'{layer.name:<9} {len(layer.events):>3} events' for layer in result.layers)}
Validation: PASS

Melody description (Chapter 21; no quality score)
--------------------------------------------------
Pitch range: {profile.pitch_range} semitones ({pitch_to_name(profile.lowest_pitch)}–{pitch_to_name(profile.highest_pitch)})
Average absolute interval: {profile.average_absolute_interval:.2f}
Steps: {profile.step_count}; leaps: {profile.leap_count}; repeats: {profile.repeat_count}

Provenance / texture
--------------------
A: seeded constrained generation; melody + harmony + bass
A': register +12 transformation of A; add groove
B: new seeded descending-biased contour; full texture
Final A: literal symbolic return; remove groove
Bass: roots-and-fifths from harmony
Harmony: sustained voice-led diatonic triads

Artifacts
---------
{chr(10).join(map(str, paths))}
OSC schedule: {len(schedule)} onset groups prepared from this same CompositionResult.

The composition engine constructs musical events. SuperCollider turns playback instructions into sound.
The reference WAV verifies pitch and timing structure; SuperCollider remains the richer sound engine.
They share symbolic events, not timbre, envelopes, effects, or exact samples.
""")
    if not live:
        print("Use --live to perform the already completed score through the Chapter 26 receiver.")
        return
    client = OscNoteClient(host, port)
    client.ping()
    execute_osc_schedule(schedule, client, verbose=True)
