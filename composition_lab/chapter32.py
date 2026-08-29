"""Chapter 32: offline-first minimalism and generative-music style lab."""
from __future__ import annotations

from collections import Counter
from dataclasses import asdict, replace
import json
from pathlib import Path

from .evaluation import melody_profile, rhythm_profile
from .event_rendering import render_events
from .minimalism import (additive_patterns, build_process_study, phase_offsets,
    realignment_period, rotate_pattern, source_pattern_a, source_pattern_b,
    substitute_pattern_steps, subtractive_patterns)
from .osc import (OSC_HOST, OSC_PORT, OscNoteClient, PlaybackChoice,
                  build_osc_schedule, execute_osc_schedule)
from .pitch import pitch_to_name
from .waveform import write_wav

PLAYBACK = {"pattern_a": PlaybackChoice("pulse", -.25), "pattern_b": PlaybackChoice("sine", .25),
            "bass": PlaybackChoice("sine", 0), "high": PlaybackChoice("articulated_saw", .4)}


def _manifest(study):
    return {"title": study.title, "tempo": study.bpm, "meter": study.meter,
            "total_beats": study.total_beats, "randomness": None,
            "source_patterns": {"A": [asdict(e) for e in study.source_a], "B": [asdict(e) for e in study.source_b]},
            "cycle_lengths": {"A": 2, "B": 3, "meter": 4},
            "process_order": ["establish", "add bass", "rotate", "add B", "discrete offset", "substitute and add high", "accumulate", "reduce"],
            "rotation_schedule": {"beats 16-24": 1, "24-32": 2, "32-64": 3},
            "phase_schedule": {"beats 24-32": 0, "32-40": .25, "40-48": .5, "48-56": .75},
            "layer_entry_schedule": {"pattern_a": 0, "bass": 8, "pattern_b": 24, "high": 40},
            "layer_reduction_schedule": {"high": 56, "pattern_b": 56, "bass": 56},
            "substitution_schedule": {"beat 40": 1, "beat 48": 2},
            "harmonic_plan": [[0, 16, "I"], [16, 32, "IV"], [32, 48, "vi"], [48, 64, "V"]]}


def write_process_artifacts(study, output: Path) -> tuple[Path, ...]:
    output.mkdir(parents=True, exist_ok=True)
    score = output / "chapter_32_process_study.json"
    manifest = output / "chapter_32_manifest.json"
    trace = output / "chapter_32_process_trace.json"
    wav = output / "chapter_32_reference.wav"
    osc = output / "chapter_32_osc_schedule.json"
    score.write_text(json.dumps([{"event": asdict(e), "layer": layer} for e, layer in
        zip(study.events, study.layers, strict=True)], indent=2, sort_keys=True) + "\n")
    manifest.write_text(json.dumps(_manifest(study), indent=2, sort_keys=True) + "\n")
    trace.write_text(json.dumps([asdict(item) for item in study.trace], indent=2, sort_keys=True) + "\n")
    write_wav(wav, render_events(study.events, study.bpm))
    schedule = build_osc_schedule(study.events, study.layers, bpm=study.bpm, playback_by_layer=PLAYBACK)
    osc.write_text(json.dumps([asdict(group) for group in schedule], indent=2, sort_keys=True) + "\n")
    return score, manifest, trace, wav, osc


def run_chapter_32(output: Path = Path("outputs"), *, bpm: float = 96, live: bool = False,
                   host: str = OSC_HOST, port: int = OSC_PORT) -> None:
    a, b = source_pattern_a(), source_pattern_b(); study = build_process_study(bpm)
    paths = write_process_artifacts(study, output)
    additive, subtractive = additive_patterns(a), subtractive_patterns(a)
    pitch_rotations = tuple(rotate_pattern(a, n) for n in range(4))
    uneven = tuple(replace(e, duration=d) for e, d in zip(a, (.25, .5, .75, .5), strict=True))
    rhythm_rotations = tuple(rotate_pattern(uneven, n, pitches=False, rhythm=True) for n in range(4))
    offsets = phase_offsets(5, .25, 1)
    simultaneous = tuple(4 if offset == 0 else 0 for offset in offsets)
    substitutions = substitute_pattern_steps(tuple(e.pitch for e in a), (65, 60, 69, 64))
    counts = Counter(study.layers); profile = melody_profile(tuple(e.pitch for e in study.events))
    density = rhythm_profile(study.events).attacks_per_beat
    print(f"""Chapter 32 — Minimalism and Generative Music

“Minimalism” covers many different composers, traditions, techniques, and historical contexts. This chapter studies
a small set of computationally useful process-based techniques and does not define minimalist music as a whole.
Twentieth-century and later experimental/minimalist practices include diverse uses of repetition, pulse, audible
process, gradual transformation, layering, phase relationships, and additive structures. No recognizable melody or
exact plan from a particular work is reproduced, and repetition + phase is not a definition of minimalism.

Chapter 31 used motif → transformation → contrasting developmental stages → return. Here a tiny pattern that barely
changes at all follows pattern → repeat → slightly alter process state → repeat. A musical process is an explicit rule
that changes musical material over time. Each study states its constant, step, and finite stopping point.

Experiment 1 — Ostinato
An ostinato is a persistently repeated musical pattern; not all minimalist music is ostinato-based.
Pattern A pitches {tuple(pitch_to_name(e.pitch) for e in a)}, rhythm {tuple(e.duration for e in a)}, cycle 2 beats.
Once: 4 events/2 beats. Control: 16 unchanged cycles, 64 events/32 beats. What changes in large-scale perception when
only elapsed repetitions increase? This is descriptive, not an interest score.

Experiment 2 — Pitch rotation
Pitch orders: {tuple(tuple(e.pitch for e in stage) for stage in pitch_rotations)}. Rhythm stays fixed; one position changes
per cycle; four states stop on wrap. Rotation changes order. Transposition changes pitch height.
Experiment 3 — Rhythm rotation
Pitches stay {tuple(e.pitch for e in a)}; duration orders {tuple(tuple(e.duration for e in stage) for stage in rhythm_rotations)}.
Pitch and rhythm processes are independent.
Experiment 4 — Additive process
An additive process gradually introduces material: prefix sizes {tuple(map(len, additive))}; one new event per stage,
four repeats per stage, then stop at the complete source.
Experiment 5 — Subtractive process
Structural reduction uses the same source, sizes {tuple(map(len, subtractive))}; it does not reverse an audio file.
At four cycles per stage, additive/subtractive event counts are {tuple(len(x)*4 for x in additive)} and
{tuple(len(x)*4 for x in subtractive)}; stage durations follow each prefix's explicit summed durations.

Experiment 6 — Layer accumulation and reduction
Timeline: 0–8 A; 8–24 A+bass; 24–40 A+bass+B; 40–56 A+bass+B+high; 56–64 A.
Existing layers are not altered merely because another enters. Reduction removes high, B, and bass at beat 56.
Experiment 7 — Discrete phase study
Identical four-attack cycles use offsets {offsets} beats (step 1/4, wrap 1 beat). Simultaneous attacks
{simultaneous}; non-simultaneous attacks {tuple(0 if n else 8 for n in simultaneous)}. This symbolic offset model shows
alignment → misalignment → full alignment, not continuously drifting clocks or exact historical phasing practice.
Experiment 8 — Gradual substitution
Fixed rhythm; pitch states {substitutions}; changed-position counts {tuple(range(len(substitutions)))}. One position changes
per stage until the target is reached; this is a factual Hamming-style count, not similarity judgment.
Experiment 9 — Different cycle lengths / realignment
4+4 realigns every {realignment_period(4,4)} beats; 3+4 realigns every {realignment_period(3,4)} beats because LCM(3,4)=12.
Pattern B's 3-beat cycle crosses barlines in global 4/4: pattern cycle ≠ meter. Complex aggregate attack patterns can
arise between simple layers without being present in either layer; aggregate complexity is not a quality claim.

Process        Pitch Order  Rhythm       Timing        Layers    Density
Repetition     no           no           no            no        constant
Rotation       yes          optional     no            no        constant
Addition       prefix       shorter span no            no        increases
Subtraction    prefix       shorter span no            no        decreases
Phase          no           no           offset        two       aggregate changes
Substitution   one position no           no            no        constant
Layer build    no           no           entrances     yes       increases

Experiment 10 — {study.title}
Eight bounded 8-beat process stages establish A, add bass, rotate A, add 3-beat B, offset B, substitute A/add a high
octave layer, retain maximum four-layer density, then reduce to A. Harmony changes only every 16 beats: I–IV–vi–V.
Maximum layer count is 4; counts {dict(sorted(counts.items()))}. Total events {len(study.events)}, attacks/beat
{density:.3f}, pitch range {profile.pitch_range} semitones. Metrics describe event data and do not score the process.
Process trace fields are beat, cycle, process, previous_state, new_state:
{chr(10).join(f'beat {t.beat:>2g} cycle {t.cycle:>2}: {t.process}; {t.new_state}' for t in study.trace)}

A generative system can produce music from deterministic rules. Algorithmic ≠ random: rotation, prefixes, offsets,
and substitution use no randomness here. Large-scale form can emerge from continuous process rather than named
sections. Repetition makes cycle count a compositional decision. Every process still needs a beginning, change rate,
stop, and successor; human boundary decisions remain visible. Pitch rotation is composition data; pan and instrument
choice are playback data. Alternate OSC timbres do not alter the NoteEvents, and velocity ≠ acoustic loudness.

Part IX synthesis (limited studies, not exhaustive genre definitions)
BLUES: form organizes variation. ROCK: riff and section organize the song. CLASSICAL-STYLE DEVELOPMENT: motif
transforms through directed development. MINIMALISM / PROCESS: repetition and gradual rule changes generate form.

What This Model Does Not Capture
--------------------------------
Historical diversity within minimalism; acoustic resonance; performer interaction; microtiming; gradual tempo drift;
human ensemble phasing; instrument-specific sustain; psychoacoustic perception; large-scale listening experience;
performance space; or composer-specific aesthetics. The event model is strong for discrete repetition, rotation,
layering, and offset, but continuous drift, subtle microtiming, and long resonance need more machinery. Transparent
rules can yield complex aggregates; complicated code alone does not imply musically meaningful complexity.
Chapter 33's questions of human intention, delegation, selection, revision, provenance, and authorship remain unimplemented.

Artifacts:
{chr(10).join(map(str, paths))}
""")
    if live:
        execute_osc_schedule(build_osc_schedule(study.events, study.layers, bpm=bpm,
            playback_by_layer=PLAYBACK), OscNoteClient(host, port))
