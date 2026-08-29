"""Chapter 31: offline-first classical-style motivic development lab."""
from __future__ import annotations

from collections import Counter
from dataclasses import asdict
import json
from pathlib import Path

from .classical_style import (HARMONIC_PLAN, SECTION_PLAN, DevelopmentStudy,
    adapt_for_vi, build_development_study, developed_phrase, fragment, source_motif)
from .evaluation import melody_profile, rhythm_profile
from .event_rendering import render_events
from .motifs import (augment_motif, diminish_motif, invert_motif,
                     retrograde_motif, sequence_motif)
from .osc import (OSC_HOST, OSC_PORT, OscNoteClient, PlaybackChoice,
                  build_osc_schedule, execute_osc_schedule)
from .pitch import pitch_to_name
from .waveform import write_wav

PLAYBACK_SIMPLE = {layer: PlaybackChoice("sine") for layer in ("motif", "harmony", "bass")}
PLAYBACK_RICH = {"motif": PlaybackChoice("articulated_saw", -.15),
                 "harmony": PlaybackChoice("sine", .2), "bass": PlaybackChoice("saw", 0)}


def _melody(study: DevelopmentStudy, start: float, end: float):
    return tuple(e for e, layer in zip(study.events, study.layers, strict=True)
                 if layer == "motif" and start <= e.start < end)


def write_development_artifacts(study: DevelopmentStudy, output: Path) -> tuple[Path, ...]:
    output.mkdir(parents=True, exist_ok=True)
    score = output / "chapter_31_development_study.json"
    manifest = output / "chapter_31_manifest.json"
    provenance = output / "chapter_31_provenance.json"
    wav = output / "chapter_31_reference.wav"
    osc = output / "chapter_31_osc_schedule.json"
    score.write_text(json.dumps([{"event": asdict(e), "layer": layer} for e, layer in
        zip(study.events, study.layers, strict=True)], indent=2, sort_keys=True) + "\n")
    manifest.write_text(json.dumps({"title": study.title, "tonic": study.tonic,
        "mode": study.mode, "tempo": study.bpm, "source_motif": [asdict(e) for e in study.motif],
        "section_plan": SECTION_PLAN, "transformation_order": [m.transformation for m in study.materials],
        "harmonic_plan": HARMONIC_PLAN, "bass_strategy": "diatonic harmonic roots",
        "accompaniment_strategy": "restrained sustained triads using Chapter 11 nearest-inversion voice leading",
        "return_strategy": "literal A in opening register over tonic", "seed": None},
        indent=2, sort_keys=True) + "\n")
    provenance.write_text(json.dumps([asdict(p) for p in study.provenance], indent=2, sort_keys=True) + "\n")
    write_wav(wav, render_events(study.events, study.bpm))
    schedule = build_osc_schedule(study.events, study.layers, bpm=study.bpm, playback_by_layer=PLAYBACK_RICH)
    osc.write_text(json.dumps([asdict(g) for g in schedule], indent=2, sort_keys=True) + "\n")
    return score, manifest, provenance, wav, osc


def run_chapter_31(output: Path = Path("outputs"), *, bpm: float = 96, tonic: int = 60,
                   live: bool = False, host: str = OSC_HOST, port: int = OSC_PORT) -> None:
    motif = tuple(e if tonic == 60 else type(e)(e.pitch + tonic - 60, e.start, e.duration, e.velocity) for e in source_motif())
    study = build_development_study(bpm, tonic); paths = write_development_artifacts(study, output)
    pitches = tuple(e.pitch for e in motif); profile = melody_profile(pitches)
    literal = tuple(e for n in range(4) for e in [type(x)(x.pitch, x.start + n * 2, x.duration, x.velocity) for x in motif])
    ascending = tuple(sequence_motif(motif, (0, 2, 4))); descending = tuple(sequence_motif(motif, (0, -2, -4)))
    frag = fragment(motif); frag4 = tuple(e for n in range(4) for e in [type(x)(x.pitch, x.start + n, x.duration, x.velocity) for x in frag])
    inverted = tuple(invert_motif(motif, tonic)); retrograde = tuple(retrograde_motif(motif))
    classifications = {name: tuple("chord tone" if e.pitch % 12 in pcs else "non-chord tone" for e in motif)
        for name, pcs in {"I": {0,4,7}, "vi": {9,0,4}, "IV": {5,9,0}, "V": {7,11,2}}.items()}
    counts = Counter(p.transformation for p in study.provenance)
    section_rows = []
    for section in study.sections:
        events = _melody(study, section.start, section.end); mp = melody_profile(tuple(e.pitch for e in events)); rp = rhythm_profile(events)
        section_rows.append(f"{section.name:<12} {len(events):>3} {rp.attacks_per_beat or 0:>6.2f} {mp.pitch_range:>5} {mp.average_absolute_interval or 0:>7.2f} {mp.maximum_leap or 0:>5}")
    print(f"""Chapter 31 — Classical-Style Development

“Classical-style development” here refers to a limited computational study of compositional techniques
associated with common-practice and related instrumental traditions. It does not define classical music as a whole.
Motivic development, phrase construction, tonal direction, sequence, cadence, and return were important tools in
many eighteenth- and nineteenth-century instrumental traditions; this is context, not a full history.

Chapter 30: riff repetition + groove + section contrast + arrangement.
Chapter 31: motif transformation + harmonic direction + phrase expansion + development + return.
A tiny motif of only a few notes begins the study. Motivic economy means creating a substantial amount of music
from limited source material. The question is how many transformations and contexts preserve a source relationship;
there is no economy, authenticity, or “classical” score.

Experiment 1 — Original motif
pitches {tuple(pitch_to_name(p) for p in pitches)} / MIDI {pitches}
intervals {profile.intervals}; rhythm {tuple(e.duration for e in motif)}; contour {profile.contour}
range {profile.pitch_range} semitones; duration {rhythm_profile(motif).beat_span} beats
Experiment 2 — Literal repetition: A A A A; {len(literal)} notes, rhythm unchanged.
Experiment 3 — Exact-semitone (real) sequence: 0,+2,+4 pitches {tuple(e.pitch for e in ascending)};
descending 0,-2,-4 range {melody_profile(tuple(e.pitch for e in descending)).pitch_range}. A scale-adjusted sequence
would preserve degrees instead; this lab transparently uses Chapter 6 semitone transposition.
Experiment 4 — first-two-note fragment ×4: {len(frag4)} notes, range {melody_profile(tuple(e.pitch for e in frag4)).pitch_range},
interval distribution {melody_profile(tuple(e.pitch for e in frag4)).interval_distribution}; full A×4 has {len(literal)} notes.
Experiment 5 — same pitches, durations original {tuple(e.duration for e in motif)}, diminution {tuple(e.duration for e in diminish_motif(motif))},
augmentation {tuple(e.duration for e in augment_motif(motif))}. Neither duration change implies importance.
Experiment 6 — inversion around MIDI {tonic}: original intervals {profile.intervals}, inverted intervals
{melody_profile(tuple(e.pitch for e in inverted)).intervals}; retrograde pitch order {tuple(e.pitch for e in retrograde)}.
Retrograde reverses temporal event order; it is not harmonic inversion.

Transformation   Pitch Order                 Rhythm          Register/Contour
Original         source                      source          {profile.contour}
Sequence         exact +2/+4 copies           unchanged       rising copy registers
Fragment         first two source events      source cell     {melody_profile(tuple(e.pitch for e in frag)).contour}
Augmentation     unchanged                    ×2              unchanged
Diminution       unchanged                    ×0.5            unchanged
Inversion        reflected around {tonic:<3}          unchanged       {melody_profile(tuple(e.pitch for e in inverted)).contour}
Retrograde       temporal reverse             reversed order  {melody_profile(tuple(e.pitch for e in retrograde)).contour}

Experiment 7 — Reharmonization means placing substantially the same melody in a different harmonic context.
Fixed event equality is retained under I, vi, and IV→V. Chord-tone classifications: {classifications}.
The adapted vi version changes exactly G4→A4: {tuple(e.pitch for e in adapt_for_vi(motif))}.
Smooth voice movement can provide continuity beneath active motifs; this is an observation, not a quality rule.
Harmony uses simple diatonic degrees {HARMONIC_PLAN}, root bass, restrained sustained sonorities, and narrow V→I endings.

Experiment 8 — Developed phrase: opening A → +2 sequence → diminished fragment continuation → longer V–I close.
Roles are local labels, not universal formal syntax. Duration {rhythm_profile(developed_phrase(motif)).beat_span} beats.
Experiment 9 — Expansion increases duration without requiring new material: 8 →
{rhythm_profile(developed_phrase(motif, True)).beat_span:g} beats; added 8–10 fragment repetition, 10–12 cadential extension.
Experiment 10 — A / ordered development / literal A. Development is related transformation serving a formal trajectory,
not a random transformation list. The return at beat 40 restores source pitches, tonic context, and opening register.
Experiment 11 — {study.title}: Opening 0–16, Development 16–40, Return 40–56, Coda 56–64.
Coda derives from an augmented A fragment and V–I cadential extension; this is a development study, not sonata form.

Transformation graph
MOTIF A
├── A1 sequence
├── A2 fragment
├── A3 inversion
├── A4 augmented
├── A5 diminished fragment
└── A6 retrograde

Provenance / motif appearance map
{chr(10).join(f'{p.material_label:<8} {p.section:<12} beat {p.start_beat:<5g} {p.transformation}' for p in study.provenance)}
Counts by explicit placement: {dict(sorted(counts.items()))}

Section      Motif state                               Harmony          Register              Density
{chr(10).join(f'{s.name:<12} {s.motif_state:<41} {s.harmony!s:<16} {s.register:<21} {s.density}' for s in study.sections)}
Section metrics: event count, attacks/beat, range, average interval, maximum leap
{chr(10).join(section_rows)}
Greater harmonic motion, broader register, more attacks, and shorter values describe authored activity; no tension
or automatic climax score is computed. The same motif + new transformation + harmony + register + placement takes
a new formal role. The program proves provenance and event reuse, not conviction, emotion, or resemblance to a composer.

What This Model Does Not Capture
--------------------------------
Historical stylistic diversity; ornamentation; counterpoint in depth; instrument-specific idioms; performance rubato;
articulation nuance; phrase shaping; advanced harmonic syntax; large-scale sonata procedures; orchestration; or human
interpretive decisions. NoteEvent cannot encode articulation symbols, slurs, phrasing, dynamic curves, rubato, or
instrument technique without more playback metadata. Its abstraction is sufficient for these structural experiments.
Chapter 32's ostinato, phase, additive/subtractive process, gradual transformation, and generative texture remain out of scope.

Simple-sine and richer OSC maps leave symbolic composition and provenance unchanged. Artifacts:
{chr(10).join(map(str, paths))}
""")
    if live:
        execute_osc_schedule(build_osc_schedule(study.events, study.layers, bpm=bpm,
            playback_by_layer=PLAYBACK_RICH), OscNoteClient(host, port))
