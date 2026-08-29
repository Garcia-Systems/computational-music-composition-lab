"""Chapter 29 offline style lab: a deliberately partial blues study."""
from __future__ import annotations

from collections import Counter
from dataclasses import asdict, dataclass, replace
import json
from pathlib import Path

from .blues import (MINOR_BLUES, DEGREE_ROOT_OFFSETS, bar_start_beat, blues_bass_pitches,
                    ending_variation, generate_blues_phrase, harmony_timeline,
                    shuffle_eighth_onsets, straight_eighth_onsets, twelve_bar_degrees)
from .chords import dominant_seventh, major_triad
from .event_rendering import render_events
from .events import NoteEvent
from .osc import (OSC_HOST, OSC_PORT, OscNoteClient, PlaybackChoice,
                  build_osc_schedule, execute_osc_schedule)
from .pitch import pitch_to_name
from .waveform import write_wav

PLAYBACK_LAYERED = {"melody": PlaybackChoice("articulated_saw", .15),
                    "harmony": PlaybackChoice("saw", -.15),
                    "bass": PlaybackChoice("sine", 0)}
PLAYBACK_SINE = {name: PlaybackChoice("sine", 0) for name in PLAYBACK_LAYERED}


@dataclass(frozen=True)
class BluesStudy:
    title: str
    tonic: int
    bpm: float
    beats_per_bar: int
    seed: int
    degrees: tuple[int, ...]
    events: tuple[NoteEvent, ...]
    layers: tuple[str, ...]
    phrase_relationships: tuple[str, ...]

    @property
    def beats(self) -> int:
        return 24 * self.beats_per_bar


def _shift(events: tuple[NoteEvent, ...], beats: float, transpose: int = 0) -> tuple[NoteEvent, ...]:
    return tuple(replace(e, start=e.start + beats, pitch=e.pitch + transpose) for e in events)


def build_blues_study(seed: int = 2026, bpm: float = 100, tonic: int = 60) -> BluesStudy:
    """Human-authored form/groove/relationships with seeded local note detail."""
    chorus1 = twelve_bar_degrees(turnaround=True)
    chorus2 = twelve_bar_degrees(quick_change=True, turnaround=False)
    degrees = chorus1 + chorus2
    events: list[NoteEvent] = []
    layers: list[str] = []
    # Sustained I7/IV7/V7 harmony and one transposed root-relative bass recipe.
    for bar, degree in enumerate(degrees):
        start, root = bar * 4, tonic + DEGREE_ROOT_OFFSETS[degree]
        for pitch in dominant_seventh(root):
            events.append(NoteEvent(pitch, start, 3.8, 48)); layers.append("harmony")
        for index, pitch in enumerate(blues_bass_pitches(root - 24)):
            onset = start + index / 2 if index % 2 == 0 else start + (index // 2) + 2 / 3
            events.append(NoteEvent(pitch, onset, .38, 72)); layers.append("bass")
    # Generate A once; all five later phrases are transparent transformations.
    a = generate_blues_phrase(tonic=tonic, seed=seed, duration=16,
                              pitch_range=(tonic, tonic + 12))
    a_prime = ending_variation(a, 3)
    b = tuple(replace(e, pitch=max(0, e.pitch - 5)) for e in reversed(a))
    # Restore chronological placement after pitch-order contrast.
    b = tuple(replace(e, start=a[i].start) for i, e in enumerate(b))
    phrases = (a, a_prime, b, _shift(a, 0, 0), ending_variation(a, -2),
               tuple(replace(e, duration=.3) for e in b))
    for phrase, start in zip(phrases, (0, 16, 32, 48, 64, 80), strict=True):
        for event in _shift(phrase, start):
            events.append(event); layers.append("melody")
    indexed = sorted(enumerate(events), key=lambda item: (item[1].start, item[0]))
    return BluesStudy("Chapter 29 Blues Study", tonic, bpm, 4, seed, degrees,
                      tuple(events[i] for i, _ in indexed), tuple(layers[i] for i, _ in indexed),
                      ("A", "A' ending variation", "B reordered/shifted", "A'' return",
                       "A''' ending variation", "B' articulation variation"))


def chord_tone_flags(pitches: tuple[int, ...], chord: tuple[int, ...]) -> tuple[bool, ...]:
    pcs = {p % 12 for p in chord}
    return tuple(p % 12 in pcs for p in pitches)


def _write_audio(path: Path, events: tuple[NoteEvent, ...], bpm: float) -> Path:
    write_wav(path, render_events(events, bpm)); return path


def write_blues_artifacts(study: BluesStudy, output: Path) -> tuple[Path, ...]:
    output.mkdir(parents=True, exist_ok=True)
    pairs = list(zip(study.events, study.layers, strict=True))
    symbolic = output / "chapter_29_blues_study.json"
    manifest = output / "chapter_29_manifest.json"
    wav = output / "chapter_29_reference.wav"
    osc = output / "chapter_29_osc_schedule.json"
    symbolic.write_text(json.dumps([{"event": asdict(e), "layer": layer} for e, layer in pairs], indent=2) + "\n")
    manifest.write_text(json.dumps({"chapter": 29, "title": study.title, "tonic": study.tonic,
        "tempo": study.bpm, "meter": "4/4", "bars": 24, "beats": study.beats,
        "harmonic_pattern": study.degrees, "chord_quality": "dominant seventh (0,4,7,10)",
        "pitch_vocabulary": list(MINOR_BLUES), "groove_model": "triplet-grid 2/3 + 1/3 approximation",
        "bass_strategy": "root-relative 1-3-5-6-6-5-3-1", "phrase_relationships": study.phrase_relationships,
        "seed": study.seed, "modeled_features": ["12-bar form", "dominant-seventh I/IV/V",
        "minor blues scale approximation", "shuffle-like subdivision", "call-and-response phrase design",
        "root-relative moving bass"]}, indent=2, sort_keys=True) + "\n")
    _write_audio(wav, study.events, study.bpm)
    schedule = build_osc_schedule(study.events, study.layers, bpm=study.bpm, playback_by_layer=PLAYBACK_LAYERED)
    osc.write_text(json.dumps([asdict(group) for group in schedule], indent=2) + "\n")
    # Narrow controlled comparisons.
    degrees = twelve_bar_degrees()
    triads, sevenths = [], []
    for bar, degree in enumerate(degrees):
        root = study.tonic + DEGREE_ROOT_OFFSETS[degree]
        triads.extend(NoteEvent(p, bar * 4, 3.8, 55) for p in major_triad(root))
        sevenths.extend(NoteEvent(p, bar * 4, 3.8, 55) for p in dominant_seventh(root))
    comparison_paths = (
        _write_audio(output / "chapter_29_triads_blues_form.wav", tuple(triads), study.bpm),
        _write_audio(output / "chapter_29_dominant_sevenths_blues_form.wav", tuple(sevenths), study.bpm))
    pitches = (60, 62, 64, 65, 67, 69, 71, 72)
    straight = tuple(NoteEvent(p, i // 2 + (i % 2) * .5, .35, 85) for i, p in enumerate(pitches))
    shuffle = tuple(NoteEvent(p, i // 2 + (i % 2) * 2 / 3, .35, 85) for i, p in enumerate(pitches))
    timing_paths = (_write_audio(output / "chapter_29_straight_eighths.wav", straight, study.bpm),
                    _write_audio(output / "chapter_29_shuffle_eighths.wav", shuffle, study.bpm))
    return (symbolic, manifest, wav, osc) + comparison_paths + timing_paths


def run_chapter_29(output: Path = Path("outputs"), *, seed: int = 2026, bpm: float = 100,
                   tonic: int = 60, live: bool = False, host: str = OSC_HOST,
                   port: int = OSC_PORT) -> None:
    study = build_blues_study(seed, bpm, tonic); paths = write_blues_artifacts(study, output)
    phrase = tuple(e.pitch for e, layer in zip(study.events, study.layers, strict=True) if layer == "melody")
    flags_i = chord_tone_flags(phrase[:6], dominant_seventh(tonic))
    flags_iv = chord_tone_flags(phrase[:6], dominant_seventh(tonic + 5))
    timeline = "\n".join(f"{bar:<5} {beat:<6} {pitch_to_name(chord[0])[:-1]}7" for bar, beat, _, chord in harmony_timeline(tonic))
    print(f"""Chapter 29 — Blues

A musical style is larger than any list of scales, chord progressions, rhythms, or algorithms.
This model represents selected features; musical data alone cannot establish authenticity, historical meaning,
cultural identity, or expressive quality. Blues developed within African American musical traditions in the
United States and became foundational to jazz, R&B, rock and roll, rock, soul, and funk.

The twelve-bar textbook abstraction is useful, not a definition: performances alter, extend, compress,
substitute, and reinterpret it. Style emerges through interaction among form, harmony, pitch inflection,
rhythmic feel, repetition, call and response, phrase placement, space, bass, and performance practice.

Baseline: I I I I | IV IV I I | V IV I I (one chord per bar)
Bar   Beat   Chord
{timeline}
4/4 keeps beat time underneath the bar convenience: 12 bars = 48 beats; bar 5 starts at beat {bar_start_beat(5)}.

Dominant seventh: {dominant_seventh(tonic)} = root + (0, 4, 7, 10).
Unlike conventional major-key tonic harmony, I7 and IV7 here do not merely inherit Chapter 10's classical
function labels. The same roots/rhythm/form are rendered as triads and sevenths for listening.

Commonly taught minor blues scale approximation: {tuple(tonic + x for x in MINOR_BLUES)}.
Integer 12-TET makes Eb and E easy to encode but hides the expressive space between them. Bends, slides,
microtonal/variable intonation, vocal inflection, and guitar articulation are not captured by MIDI-like integers.

Melody/harmony friction (descriptive, never an error or quality score)
Pitch     I7 chord-tone?   IV7 chord-tone?
{chr(10).join(f'{pitch_to_name(p):<9} {str(a):<16} {b}' for p, a, b in zip(phrase[:6], flags_i, flags_iv, strict=True))}
The unchanged motif receives different classifications in a changed context. A high non-chord-tone count does
not imply poor music; Eb against C7 can be meaningful tension.

Straight onsets: {straight_eighth_onsets()} | simplified shuffle onsets: {shuffle_eighth_onsets()}.
One beat is treated as three equal thirds: X . X. Blues can be straight, swung, shuffled, or use other feels.
The 2/3 + 1/3 ratio is a useful controlled model, not a prescription for human timing.

Call/response: A → A' changes one ending; B contrasts; later A''/A'''/B' derive from stored material.
Each short attack group leaves silence in its four-bar window. The riff/motif remains the existing NoteEvent
representation, repeated over changing harmony rather than becoming a new data type.
Bass comparison recipe: roots only versus transposed intervals {tuple(x for x in (0,4,7,9,9,7,4,0))}.
Bar 12 uses V7 as a simple turnaround into chorus 2; chorus 2 uses the documented quick-change variation.

Capstone report (description, not a blues score)
Form: two choruses / 24 bars / {study.beats} beats | tempo: {study.bpm:g} BPM | seed: {study.seed}
Harmony: I7/IV7/V7, one chord per bar | melody range: {max(phrase)-min(phrase)} semitones
Pitch classes: {dict(sorted(Counter(p % 12 for p in phrase).items()))}
Repetition: six related four-bar phrase windows | attack density: {len(phrase)/study.beats:.3f} melody attacks/beat
Harmony alignment first motif: I7 {sum(flags_i)}/{len(flags_i)} chord tones; IV7 {sum(flags_iv)}/{len(flags_iv)}
Bass: root-relative moving pattern; range reported in symbolic artifact. Playback maps change SynthDefs, not events.

What This Model Does Not Capture
--------------------------------
Microtonal pitch inflection; variable human swing; vocal phrasing; guitar-specific articulation; tone production;
interaction among musicians; regional and historical styles; lyrical traditions; improvisational vocabulary;
individual performer identity; or the cultural and historical context carried by people and practices.
It generates no lyrics, authenticity metric, style score, classifier, mechanical “human feel,” or generalized bend.

Listening worksheet: What changes with sevenths, blues-scale material, shuffle timing, silence, repetition,
moving bass, changed notes over IV7, and the turnaround? Where do chord/non-chord classifications change?

Artifacts
{chr(10).join(map(str, paths))}
""")
    if live:
        schedule = build_osc_schedule(study.events, study.layers, bpm=bpm, playback_by_layer=PLAYBACK_LAYERED)
        client = OscNoteClient(host, port); client.ping(); execute_osc_schedule(schedule, client)
