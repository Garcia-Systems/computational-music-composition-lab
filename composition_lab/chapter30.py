"""Chapter 30: an offline-first riff-to-song style laboratory."""
from __future__ import annotations

from collections import Counter
from dataclasses import asdict, dataclass, replace
import json
from pathlib import Path

from .chords import major_triad, minor_triad
from .event_rendering import render_events
from .events import NoteEvent
from .osc import (OSC_HOST, OSC_PORT, OscNoteClient, PlaybackChoice,
                  build_osc_schedule, execute_osc_schedule)
from .rock import (BRIDGE_DEGREES, CHORUS_DEGREES, VERSE_DEGREES, backbeat_bar,
                   bass_lines, four_repetitions, opening_riff, power_chord,
                   riff_variations, syncopated_riff)
from .waveform import write_wav

FORM = ("Intro", "Verse 1", "Chorus 1", "Verse 2", "Chorus 2", "Bridge",
        "Final Chorus", "Outro")
SECTION_BARS = {name: 4 for name in FORM}
ARRANGEMENT = {
    "Intro": ("riff",),
    "Verse 1": ("riff", "bass", "groove", "lead"),
    "Chorus 1": ("bass", "harmony", "groove", "lead"),
    "Verse 2": ("riff", "bass", "groove", "lead"),
    "Chorus 2": ("bass", "harmony", "groove", "lead"),
    "Bridge": ("riff", "bass", "harmony", "groove"),
    "Final Chorus": ("riff", "bass", "harmony", "groove", "lead"),
    "Outro": ("riff", "harmony"),
}
PLAYBACK_RICH = {"riff": PlaybackChoice("articulated_saw", -.2),
                 "bass": PlaybackChoice("sine", 0),
                 "harmony": PlaybackChoice("saw", .15),
                 "groove": PlaybackChoice("pulse", 0),
                 "lead": PlaybackChoice("articulated_saw", .25)}
PLAYBACK_SIMPLE = {name: PlaybackChoice("sine", 0) for name in PLAYBACK_RICH}


@dataclass(frozen=True)
class RockSection:
    name: str
    start: float
    end: float
    harmony: tuple[int, ...]
    riff: str
    lead: str
    bass_strategy: str
    active_layers: tuple[str, ...]


@dataclass(frozen=True)
class RockSongStudy:
    title: str
    tonic: int
    bpm: float
    meter: str
    seed: int
    sections: tuple[RockSection, ...]
    events: tuple[NoteEvent, ...]
    layers: tuple[str, ...]
    hook_locations: tuple[str, ...]

    @property
    def beats(self) -> float:
        return self.sections[-1].end


def _roots(tonic: int, degrees: tuple[int, ...], bass: bool = False) -> tuple[int, ...]:
    offsets = (0, 2, 4, 5, 7, 9, 11)
    base = tonic - 12 if bass else tonic
    return tuple(base + offsets[d - 1] for d in degrees)


def _groove_16() -> tuple[NoteEvent, ...]:
    bar = tuple(e for events in backbeat_bar().values() for e in events)
    return tuple(replace(e, start=e.start + offset) for offset in (0, 4, 8, 12) for e in bar)


def _harmony(tonic: int, degrees: tuple[int, ...], velocity: int) -> tuple[NoteEvent, ...]:
    result = []
    for bar, (degree, root) in enumerate(zip(degrees, _roots(tonic, degrees), strict=True)):
        triad = minor_triad(root) if degree == 6 else major_triad(root)
        result.extend(NoteEvent(p, bar * 4, 3.8, velocity) for p in triad)
    return tuple(result)


def _hook() -> tuple[NoteEvent, ...]:
    # Original instrumental, vocal-like two-bar phrase; repeated at a fixed location.
    pitches, starts, durations = (64, 66, 68, 71, 69), (0, 1, 2, 3, 4), (.8, .8, .8, .8, 4)
    return tuple(NoteEvent(p, s, d, 98) for p, s, d in zip(pitches, starts, durations, strict=True))


def _verse_lead(variation: bool = False) -> tuple[NoteEvent, ...]:
    pitches = (59, 61, 64, 62) if not variation else (59, 61, 66, 62)
    # The final event is a pickup into the following chorus, not a negative-time event.
    starts = (2, 6, 10, 15.5)
    return tuple(NoteEvent(p, s, .4 if s == 15.5 else 1.0, 78) for p, s in zip(pitches, starts, strict=True))


def build_rock_song(seed: int = 2026, bpm: float = 112, tonic: int = 52) -> RockSongStudy:
    """Assemble the explicit human-authored 32-bar plan deterministically."""
    riff = opening_riff()
    section_events: list[tuple[NoteEvent, str]] = []
    sections: list[RockSection] = []
    hook_locations: list[str] = []
    cursor = 0.0
    for name in FORM:
        is_chorus = "Chorus" in name
        degrees = CHORUS_DEGREES if is_chorus else BRIDGE_DEGREES if name == "Bridge" else VERSE_DEGREES
        bass_strategy = "root-following" if is_chorus else "independent" if name == "Bridge" else "riff-doubling"
        local: dict[str, tuple[NoteEvent, ...]] = {}
        if "riff" in ARRANGEMENT[name]:
            if name == "Bridge":
                fragment = riff_variations(riff)["fragment"]
                local["riff"] = tuple(replace(e, start=e.start + offset) for offset in range(0, 16, 2) for e in fragment)
            elif name == "Verse 2":
                local["riff"] = four_repetitions(riff, varied_ending=True)
            else:
                local["riff"] = four_repetitions(riff)
        if "bass" in ARRANGEMENT[name]:
            local["bass"] = bass_lines(riff, _roots(tonic, degrees, bass=True))[bass_strategy]
        if "harmony" in ARRANGEMENT[name]:
            local["harmony"] = _harmony(tonic, degrees, 86 if is_chorus else 68)
        if "groove" in ARRANGEMENT[name]:
            local["groove"] = _groove_16()
        lead_label = "none"
        if "lead" in ARRANGEMENT[name]:
            if is_chorus:
                hook = _hook()
                local["lead"] = hook + tuple(replace(e, start=e.start + 8) for e in hook)
                hook_locations.append(name); lead_label = "hook B ×2"
            else:
                local["lead"] = _verse_lead(name == "Verse 2"); lead_label = "sparse phrase"
        for layer, events in local.items():
            section_events.extend((replace(e, start=e.start + cursor), layer) for e in events)
        sections.append(RockSection(name, cursor, cursor + 16, degrees,
                                    "A' ending" if name == "Verse 2" else "A fragment" if name == "Bridge" else "A" if "riff" in local else "none",
                                    lead_label, bass_strategy if "bass" in local else "none", ARRANGEMENT[name]))
        cursor += 16
    indexed = sorted(enumerate(section_events), key=lambda item: (item[1][0].start, item[0]))
    return RockSongStudy("Chapter 30 Rock Song Study", tonic, bpm, "4/4", seed,
                         tuple(sections), tuple(section_events[i][0] for i, _ in indexed),
                         tuple(section_events[i][1] for i, _ in indexed), tuple(hook_locations))


def _layer_metrics(study: RockSongStudy, section: RockSection) -> tuple[int, float, tuple[int, int], float]:
    events = [e for e in study.events if section.start <= e.start < section.end]
    return (len(events), len(events) / 16, (min(e.pitch for e in events), max(e.pitch for e in events)),
            sum(e.velocity for e in events) / len(events))


def write_rock_artifacts(study: RockSongStudy, output: Path) -> tuple[Path, ...]:
    output.mkdir(parents=True, exist_ok=True)
    song = output / "chapter_30_rock_song.json"
    manifest = output / "chapter_30_manifest.json"
    wav = output / "chapter_30_reference.wav"
    osc = output / "chapter_30_osc_schedule.json"
    song.write_text(json.dumps([{"event": asdict(e), "layer": layer} for e, layer in zip(study.events, study.layers, strict=True)], indent=2, sort_keys=True) + "\n")
    manifest_data = {"chapter": 30, "title": study.title, "key_tonal_center": "E",
        "tonic_midi": study.tonic, "tempo": study.bpm, "meter": study.meter,
        "form": FORM, "section_lengths_bars": SECTION_BARS, "riff_strategy": "one-bar motif A; A' ending in Verse 2; fragment in Bridge",
        "verse_harmony": VERSE_DEGREES, "chorus_harmony": CHORUS_DEGREES,
        "bridge_harmony": BRIDGE_DEGREES, "groove_strategy": "pitched proxy kick 1/3, snare 2/4, eighth pulse",
        "bass_strategies": {s.name: s.bass_strategy for s in study.sections},
        "hook_source": "original two-bar instrumental motif B, twice per chorus",
        "hook_locations": study.hook_locations, "seed": study.seed,
        "transition": "lead pickup at beat 15.5 of each verse",
        "arrangement_plan": {s.name: s.active_layers for s in study.sections}}
    manifest.write_text(json.dumps(manifest_data, indent=2, sort_keys=True) + "\n")
    write_wav(wav, render_events(study.events, study.bpm))
    schedule = build_osc_schedule(study.events, study.layers, bpm=study.bpm, playback_by_layer=PLAYBACK_RICH)
    osc.write_text(json.dumps([asdict(group) for group in schedule], indent=2, sort_keys=True) + "\n")
    return song, manifest, wav, osc


def run_chapter_30(output: Path = Path("outputs"), *, seed: int = 2026, bpm: float = 112,
                   tonic: int = 52, live: bool = False, host: str = OSC_HOST,
                   port: int = OSC_PORT) -> None:
    riff = opening_riff(); study = build_rock_song(seed, bpm, tonic); paths = write_rock_artifacts(study, output)
    pitches = tuple(e.pitch for e in riff); onsets = tuple(e.start for e in riff)
    rests = tuple(round(b.start - (a.start + a.duration), 2) for a, b in zip(riff, riff[1:]) if b.start > a.start + a.duration)
    verse, chorus = study.sections[1], study.sections[2]
    print(f"""Chapter 30 — Rock and Songwriting

Rock is not a formula. This lab models selected devices, never a rock score, authenticity score, or genre
classifier. Power chords + backbeat + distortion does not equal rock. Rock developed through blues, rhythm
and blues, country, gospel, and rock and roll, then diversified into many practices rather than one grammar.

Chapter 29 begins form → harmony → phrase → groove → blues study.
Chapter 30 begins riff → groove → chord loop → section → arrangement → song.
What if the seed of the composition is just a riff?

A riff is a recurring musical figure that can provide melodic, rhythmic, harmonic, or textural identity.
Here it is Chapter 6's motif used as a recurring structural layer, not a new class. A motif becomes riff-like
contextually when prominent, groove-tied, accompanying, or section-identifying.

Riff inspector (one original E-centred bar)
pitches {pitches} | intervals {tuple(b-a for a,b in zip(pitches,pitches[1:]))}
onsets {onsets} | durations {tuple(e.duration for e in riff)} | rests {rests}
pitch range {max(pitches)-min(pitches)} | attacks {len(riff)} | attacks/beat {len(riff)/4:.2f}
A A A A offsets (0, 4, 8, 12); A A A A' changes only the final pitch.
Variations: {tuple(riff_variations(riff))}; E→A transposition reuses the same interval/rhythm structure.
What happens when a one-bar idea becomes a repeated four-bar texture?

Power chord E5: {power_chord(40)}; without doubled root: {power_chord(40, False)}.
A root-and-fifth power chord omits the third, so it does not specify major/minor quality like a triad.
Triad/power comparison keeps root motion, register, rhythm, and tempo fixed. E5/G5/A5 can remain ambiguous
until thirds in melody or harmony add context. Power chords are useful in many rock styles; they do not define it.
Loops compared: I–V–vi–IV, I–IV–V–IV, vi–IV–I–V. Root-position, voice-led, and root/fifth voicings are
different realizations of abstract degrees. The study uses verse {VERSE_DEGREES}, chorus {CHORUS_DEGREES},
bridge {BRIDGE_DEGREES}. A fixed riff over changing chords can be melody, accompaniment, or both;
non-chord tone ≠ wrong note. A harmony-adapted alternative may selectively transpose attacks without ranking it.

Groove model: low proxy beats 1/3; mid proxy beats 2/4; high eighths. Accenting 2 and 4 is common in many
rock and related styles, not universal. Straight versus syncopated onsets:
{onsets} → {tuple(e.start for e in syncopated_riff(riff))}; pitches remain fixed.
Bass choices: riff reinforcement, chord roots, or an independent connecting line. No choice is universal.
Riff attacks align to main beats and offbeats; modeled backbeats are zero-based beats 1 and 3 (heard as 2 and 4).

Riff and lead are separate layers: repeating low-mid identity versus foreground mid-high phrase. Deliberately
placing both in one range creates collision; octave separation changes register without changing phrase shape.
A hook is an idea given structural emphasis through repetition or placement. The program counts its returns;
it cannot measure memorability. Hook B occurs twice in {study.hook_locations}.

Song report
Section        Bars Beats Harmony       Riff        Lead          Bass             Active layers
{chr(10).join(f'{s.name:<14} 4    16    {s.harmony!s:<13} {s.riff:<11} {s.lead:<13} {s.bass_strategy:<16} {", ".join(s.active_layers)}' for s in study.sections)}

Arrangement timeline
{chr(10).join(f'{s.name:<14} {s.start:>5g}–{s.end:<5g} {", ".join(s.active_layers)}' for s in study.sections)}
Verse/chorus objective comparison (event count, attacks/beat, register, average velocity):
Verse 1 {_layer_metrics(study, verse)} | Chorus 1 {_layer_metrics(study, chorus)}
Controlled contrast can isolate texture, then harmony, then register, then riff. Tempo/key/meter need not change.
Bridge comparison: V–C–V–C–C versus V–C–V–C–B–C; this study's bridge uses A' fragments and new harmony.
Bridges are optional and the term varies among traditions. Verse 2 reuses A with one ending; Chorus 2 reuses B.
A pickup at beat 15.5 of each verse begins before the chorus downbeat without a negative composition time.

Repetition map: riff A—Intro, Verse 1, Verse 2, Outro; hook B—Chorus 1, Chorus 2, Final Chorus;
riff fragment A'—Bridge. Repetition, variation, contrast, return, layering, and recontextualization avoid requiring
wholly new material in every section. MIDI-style velocity is not measured acoustic loudness.

SONG STRUCTURE (riff, melody, harmony, form, rhythm) differs from ARRANGEMENT/SOUND (entrances, register,
instrument, pan, effects). Simple-sine and richer maps leave the symbolic song unchanged. Lyrics and syllable
mapping are out of scope; the lead is only vocal-like and instrumental. No amplifier, pedalboard, cabinet, or
distortion architecture is required.

What This Model Does Not Capture
--------------------------------
Human ensemble interaction; guitar technique; amplifier/speaker behavior; drum nuance; microtiming; vocal
delivery; lyrics; studio production; historical subgenres; performer identity; or cultural context. NoteEvent
stores pitch/start/duration/velocity, not palm muting, pick direction, string choice, feedback, bends, slides,
vibrato, or drum articulation. Do not generalize this recipe automatically to punk, metal, progressive, indie,
hard, psychedelic, or alternative rock, jam bands, or other traditions. It knows repetition, layers, register,
and changed loops—not whether a riff is catchy, a chorus exciting, or a song “rocks.” Chapter 31 remains out
of scope: no classical-style development system is introduced here.

Artifacts
{chr(10).join(map(str, paths))}
""")
    if live:
        schedule = build_osc_schedule(study.events, study.layers, bpm=bpm, playback_by_layer=PLAYBACK_RICH)
        client = OscNoteClient(host, port); client.ping(); execute_osc_schedule(schedule, client)
