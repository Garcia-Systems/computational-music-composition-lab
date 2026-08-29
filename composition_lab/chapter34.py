"""Chapter 34: a deterministic, provenance-rich complete composition."""
from __future__ import annotations

from collections import Counter
from dataclasses import asdict, dataclass, replace
import hashlib
import json
from pathlib import Path
import random

from .chapter33 import CompositionDecision, DecisionCategory
from .evaluation import melody_profile, repetition_profile, rhythm_profile
from .event_rendering import render_events
from .events import NoteEvent, composition_duration
from .osc import PlaybackChoice, OscNoteClient, build_osc_schedule, execute_osc_schedule
from .pitch import pitch_to_name
from .waveform import write_wav

TITLE = "Converging Paths"
MASTER_SEED = 2026
TEMPO = 96.0
FORM = ("intro", "a", "a_prime", "b", "development", "a_return", "coda")
SECTION_DURATIONS = (8, 24, 24, 24, 32, 24, 16)
SOURCE_MOTIF = (
    NoteEvent(60, 0, 1, 94), NoteEvent(64, 1, .5, 90),
    NoteEvent(67, 1.5, 1.5, 98), NoteEvent(65, 3, 1, 91),
    NoteEvent(62, 4, 2, 88),
)
RECORDED_A_PRIME_SELECTION = "a-prime-candidate-02"
RECORDED_B_SELECTION = "b-candidate-04"
REVISION_ID = "revision-b-01"
PLAYBACK = {
    "melody": PlaybackChoice("articulated_saw", .15),
    "harmony": PlaybackChoice("pulse", -.2),
    "bass": PlaybackChoice("sine", 0),
    "groove": PlaybackChoice("pulse", .35),
}
EFFECTS = {"melody": "moderate_reverb", "harmony": "light_reverb",
           "bass": "dry", "groove": "dry"}


@dataclass(frozen=True)
class Candidate:
    id: str
    seed: int | None
    transformation: str
    events: tuple[NoteEvent, ...]
    metrics: dict[str, object]
    constraints: dict[str, bool]


@dataclass(frozen=True)
class Section:
    id: str
    start: float
    duration: float
    layers: dict[str, tuple[NoteEvent, ...]]
    material_id: str


@dataclass(frozen=True)
class CompletePiece:
    brief: dict[str, object]
    sections: tuple[Section, ...]
    a_prime_candidates: tuple[Candidate, ...]
    b_candidates: tuple[Candidate, ...]
    b_before_revision: tuple[NoteEvent, ...]
    ledger: tuple[CompositionDecision, ...]
    provenance: tuple[dict[str, object], ...]
    harmonic_timeline: tuple[dict[str, object], ...]
    trace: dict[str, object]

    def flattened(self) -> tuple[tuple[NoteEvent, ...], tuple[str, ...]]:
        pairs = [(event, layer) for section in self.sections
                 for layer, events in section.layers.items() for event in events]
        pairs.sort(key=lambda pair: (pair[0].start, pair[1], pair[0].pitch))
        return tuple(p[0] for p in pairs), tuple(p[1] for p in pairs)


def composition_brief() -> dict[str, object]:
    return {"heading": "COMPOSITION BRIEF", "authorship": "human",
            "title": TITLE,
            "request": "Create an original, stylistically neutral instrumental piece.",
            "goals": ["clear opening identity", "contrasting middle region",
                      "recognizable return", "gradual textural growth",
                      "algorithm-generated melodic material",
                      "motif transformation", "audible designed ending",
                      "approximately 90–150 seconds"],
            "tempo": TEMPO, "meter": "4/4", "tonal_center": "C major",
            "master_seed": MASTER_SEED}


DELEGATION_PLAN = {
    "form": "human", "tonal center": "human", "section lengths": "human",
    "A motif": "human", "A' transformation": "algorithm-proposed / human-selected",
    "B melody": "algorithm-proposed / human-selected", "development process": "human-designed, algorithm-executed",
    "harmony": "human", "bass": "human strategy + derived events",
    "groove": "human strategy + derived events", "texture plan": "human",
    "playback map": "human", "OSC conversion": "derived"}


def _seed(identity: str, master_seed: int = MASTER_SEED) -> int:
    return int.from_bytes(hashlib.sha256(f"chapter-34:{master_seed}:{identity}".encode()).digest()[:8], "big")


def _metrics(events: tuple[NoteEvent, ...]) -> dict[str, object]:
    pitches = tuple(e.pitch for e in events)
    mp, rp = melody_profile(pitches), rhythm_profile(events)
    intervals = tuple(b-a for a, b in zip(pitches, pitches[1:]))
    return {"range": mp.pitch_range, "steps": mp.step_count, "leaps": mp.leap_count,
            "average_interval": mp.average_absolute_interval,
            "attack_density": rp.attacks_per_beat,
            "repetition": repetition_profile(pitches)["immediate_pitch_repeats"],
            "chord_tone_percentage": round(100 * sum(p % 12 in {0, 4, 7} for p in pitches) / len(pitches), 2),
            "interval_distribution": dict(Counter(intervals))}


def generate_a_prime_candidates() -> tuple[Candidate, ...]:
    ending = SOURCE_MOTIF[:-1] + (replace(SOURCE_MOTIF[-1], pitch=60),)
    rhythm = tuple(replace(e, start=s, duration=d) for e, s, d in zip(
        SOURCE_MOTIF, (0, .5, 1.5, 2.5, 4), (.5, 1, 1, 1.5, 2), strict=True))
    register = tuple(replace(e, pitch=e.pitch + 12) for e in SOURCE_MOTIF)
    return tuple(Candidate(f"a-prime-candidate-0{i}", None, name, events,
                           _metrics(events), {"derived_from_motif-a": True})
                 for i, (name, events) in enumerate((("ending variation", ending),
                    ("rhythmic variation", rhythm), ("register variation", register)), 1))


def generate_b_candidates(master_seed: int = MASTER_SEED, count: int = 6) -> tuple[Candidate, ...]:
    scale, rhythms = (60, 62, 64, 65, 67, 69, 71, 72), (1.0, 1.5, .5)
    result, attempts, rejected = [], 0, Counter()
    for number in range(1, count + 1):
        identity, events = f"b-candidate-{number:02d}", []
        rng = random.Random(_seed(f"b-candidate-{number:02d}", master_seed)); start = 0.0
        pitch = rng.choice(scale[2:7])
        while start < 22.5:
            attempts += 1
            duration = min(rng.choice(rhythms), 22.5-start)
            events.append(NoteEvent(pitch, start, duration, 92)); start += duration
            pitch = rng.choice(tuple(p for p in scale if abs(p-pitch) <= 7))
        # Preserve the required tonic ending without silently relaxing the leap
        # constraint: deterministically redirect the approach note when needed.
        if events and abs(events[-1].pitch - 60) > 7:
            events[-1] = replace(events[-1], pitch=67)
        events.append(NoteEvent(60, start, 24-start, 88))
        candidate = tuple(events)
        checks = {"duration": composition_duration(candidate) == 24,
                  "pitch_range": all(60 <= e.pitch <= 72 for e in candidate),
                  "maximum_leap": all(abs(b.pitch-a.pitch) <= 7 for a, b in zip(candidate, candidate[1:])),
                  "allowed_ending": candidate[-1].pitch in (60, 64, 67),
                  "rhythm_vocabulary": all(e.duration in (.5, 1, 1.5) for e in candidate)}
        if not all(checks.values()):
            rejected.update(k for k, valid in checks.items() if not valid)
            raise RuntimeError(f"unable to create {count} valid B candidates: {dict(rejected)}")
        result.append(Candidate(identity, _seed(identity, master_seed), "seeded constrained random walk",
                                candidate, _metrics(candidate), checks))
    generate_b_candidates.last_trace = {"attempts": attempts, "valid_candidates": len(result),
                                        "rejection_reasons": dict(rejected)}
    return tuple(result)


generate_b_candidates.last_trace = {}  # type: ignore[attr-defined]


def _place(events, start, repeats=1, transpose=0):
    span = 6
    return tuple(replace(e, pitch=e.pitch+transpose, start=start+r*span+e.start)
                 for r in range(repeats) for e in events)


CHORDS = {1: (60,64,67), 2: (62,65,69), 4: (60,65,69), 5: (59,62,67), 6: (60,64,69)}
PLANS = {
 "intro": (1,1), "a": (1,6,4,5,1,5), "a_prime": (1,6,4,5,1,5),
 "b": (6,4,2,5,6,5), "development": (2,5,6,4,2,5,4,5),
 "a_return": (1,6,4,5,1,1), "coda": (4,5,1,1)}


def build_complete_piece(master_seed=MASTER_SEED, a_prime_selection=RECORDED_A_PRIME_SELECTION,
                         b_selection=RECORDED_B_SELECTION) -> CompletePiece:
    ap, bc = generate_a_prime_candidates(), generate_b_candidates(master_seed)
    ap_by, b_by = {c.id:c for c in ap}, {c.id:c for c in bc}
    if a_prime_selection not in ap_by or b_selection not in b_by: raise ValueError("recorded selection must exist")
    selected_b = b_by[b_selection].events
    revised_b = selected_b[:-1] + (replace(selected_b[-1], start=22, duration=2, pitch=60),)
    starts, cursor = {}, 0
    for sid, duration in zip(FORM, SECTION_DURATIONS, strict=True): starts[sid]=cursor; cursor += duration
    melodies = {
      "intro": _place(SOURCE_MOTIF[:3], starts["intro"]),
      "a": _place(SOURCE_MOTIF, starts["a"], 4),
      "a_prime": _place(ap_by[a_prime_selection].events, starts["a_prime"], 4),
      "b": _place(revised_b, starts["b"]),
      "development": (_place(SOURCE_MOTIF[:3], starts["development"], 4) +
          _place(tuple(replace(e, start=e.start/2, duration=e.duration/2, pitch=72-(e.pitch-60)) for e in SOURCE_MOTIF[:3]), starts["development"]+24, 2)),
      "a_return": _place(SOURCE_MOTIF, starts["a_return"], 4, 12),
      "coda": _place(tuple(replace(e, start=e.start*2, duration=e.duration*2) for e in SOURCE_MOTIF[:3]), starts["coda"]),
    }
    texture = {"intro": ("melody", "bass"), "a": ("melody","bass","harmony"),
      "a_prime": ("melody","bass","harmony","groove"), "b": ("melody","harmony"),
      "development": ("melody","bass","harmony","groove"), "a_return": ("melody","bass","harmony","groove"),
      "coda": ("melody","bass","harmony")}
    harmonic, sections = [], []
    for sid, duration in zip(FORM, SECTION_DURATIONS, strict=True):
        start, layers = starts[sid], {"melody": melodies[sid]}
        plan = PLANS[sid]
        harmony=[]; bass=[]
        for i, degree in enumerate(plan):
            beat=start+i*4; chord=CHORDS[degree]
            harmonic.append({"section":sid,"beat":beat,"degree":degree,"chord":[pitch_to_name(p) for p in chord]})
            harmony.extend(NoteEvent(p, beat, 4, 55) for p in chord)
            bass.append(NoteEvent(chord[0]-24, beat, 2, 75)); bass.append(NoteEvent(chord[2]-24, beat+2, 2, 70))
        if "harmony" in texture[sid]: layers["harmony"]=tuple(harmony)
        if "bass" in texture[sid]: layers["bass"]=tuple(bass)
        if "groove" in texture[sid]: layers["groove"]=tuple(NoteEvent(36 if i%4 in (0,2) else 38,start+i,.2,48) for i in range(duration))
        sections.append(Section(sid,start,duration,layers, {"intro":"motif-a-fragment","a":"motif-a","a_prime":a_prime_selection,"b":b_selection,
            "development":"motif-a-development","a_return":"motif-a-return","coda":"motif-a-augmented-fragment"}[sid]))
    candidates = tuple(c.id for c in ap), tuple(c.id for c in bc)
    ledger=(
      CompositionDecision("brief","intention","Author composition brief",DecisionCategory.HUMAN,"authored brief"),
      CompositionDecision("form","structure","Choose explicit seven-section form",DecisionCategory.HUMAN,"authored plan",selection=" ".join(FORM)),
      CompositionDecision("motif-a","material","Author five-note source motif",DecisionCategory.HUMAN,"authored score"),
      CompositionDecision("a-prime-generation","generation","Transform motif",DecisionCategory.ALGORITHM,"Chapter 16 transformations",candidates[0]),
      CompositionDecision("a-prime-selection","selection","Apply recorded human selection",DecisionCategory.HUMAN_SELECTED_ALGORITHM_CANDIDATE,"recorded human selection",candidates[0],a_prime_selection,reference=a_prime_selection),
      CompositionDecision("b-generation","generation","Generate constrained random walks",DecisionCategory.ALGORITHM,"Chapter 19 seeded constrained random walk",candidates[1],seed=master_seed),
      CompositionDecision("b-selection","selection","Apply recorded human selection",DecisionCategory.HUMAN_SELECTED_ALGORITHM_CANDIDATE,"recorded human selection",candidates[1],b_selection,reference=b_selection),
      CompositionDecision(REVISION_ID,"revision","Lengthen final tonic to two beats",DecisionCategory.HUMAN,"authored edit",selection="final C4 at beat 22 for 2 beats",reference=b_selection),
      CompositionDecision("development","development","Fragment, sequence, diminish, and invert motif",DecisionCategory.DERIVED,"human-designed / algorithm-executed",reference="motif-a"),
      CompositionDecision("harmony","harmony","Choose diatonic harmonic plans",DecisionCategory.HUMAN,"authored plan"),
      CompositionDecision("bass-strategy","arrangement","Choose roots_and_fifths",DecisionCategory.HUMAN,"authored strategy",selection="roots_and_fifths"),
      CompositionDecision("bass-events","arrangement","Derive bass from harmony",DecisionCategory.DERIVED,"Chapter 14"),
      CompositionDecision("groove-strategy","arrangement","Choose light quarter pulse/backbeat",DecisionCategory.HUMAN,"authored strategy"),
      CompositionDecision("groove-events","arrangement","Derive groove events",DecisionCategory.DERIVED,"Chapter 13"),
      CompositionDecision("texture","arrangement","Choose layer-entry plan",DecisionCategory.HUMAN,"authored plan"),
      CompositionDecision("playback","playback","Choose instruments, pan, effects",DecisionCategory.HUMAN,"authored playback map"),
      CompositionDecision("osc","playback","Convert finalized events",DecisionCategory.DERIVED,"Chapter 26"),
      CompositionDecision("finished","stopping","Declare composition finished",DecisionCategory.HUMAN,"recorded human decision"),)
    transformations={"intro":"fragmentation","a":"authored source repeated","a_prime":ap_by[a_prime_selection].transformation,
      "b":"seeded generation then revision","development":"fragmentation → sequence → diminution + inversion",
      "a_return":"source motif transposed one octave","coda":"fragmentation + augmentation"}
    provenance=tuple({"label":s.material_id,"section":s.id,"source_material":"generated B candidate" if s.id=="b" else "motif-a",
      "transformation":transformations[s.id],"generator":"seeded constrained random walk" if s.id=="b" else None,
      "candidate_id":s.material_id if "candidate" in s.material_id else None,
      "selection_source":"recorded human selection" if s.id in ("a_prime","b") else "human/derived plan",
      "revision_history":[REVISION_ID] if s.id=="b" else []} for s in sections)
    return CompletePiece(composition_brief(),tuple(sections),ap,bc,selected_b,ledger,provenance,tuple(harmonic),dict(generate_b_candidates.last_trace))


def _serialize_event(e): return asdict(e)


def write_artifacts(piece: CompletePiece, output: Path, bpm=TEMPO) -> tuple[Path,...]:
    output.mkdir(parents=True,exist_ok=True)
    def dump(name,value):
        path=output/name; path.write_text(json.dumps(value,indent=2,sort_keys=True)+"\n"); return path
    events,layers=piece.flattened()
    texture={s.id:list(s.layers) for s in piece.sections}
    brief=dump("chapter_34_brief.json",piece.brief)
    candidates=dump("chapter_34_candidates.json",{"constraint_trace":piece.trace,"a_prime":[{**asdict(c),"events":[_serialize_event(e) for e in c.events]} for c in piece.a_prime_candidates],"b":[{**asdict(c),"events":[_serialize_event(e) for e in c.events]} for c in piece.b_candidates]})
    ledger=dump("chapter_34_decision_ledger.json",[asdict(d) for d in piece.ledger])
    provenance=dump("chapter_34_provenance.json",piece.provenance)
    score=dump("chapter_34_complete_piece.json",{"metadata":piece.brief,"sections":[{"id":s.id,"start":s.start,"duration":s.duration,"material_id":s.material_id,"layers":{k:[_serialize_event(e) for e in v] for k,v in s.layers.items()}} for s in piece.sections]})
    manifest=dump("chapter_34_manifest.json",{"title":TITLE,"tempo":bpm,"meter":"4/4","tonal_center":"C major","total_beats":sum(SECTION_DURATIONS),"form":FORM,"section_durations":dict(zip(FORM,SECTION_DURATIONS)),"harmonic_plans":PLANS,"source_motif":[_serialize_event(e) for e in SOURCE_MOTIF],"master_seed":MASTER_SEED,"candidate_counts":{"a_prime":3,"b":6},"recorded_selections":{"a_prime":RECORDED_A_PRIME_SELECTION,"b":RECORDED_B_SELECTION},"revisions":[REVISION_ID],"bass_strategy":"roots_and_fifths","groove_strategy":"light quarter pulse/backbeat","texture_plan":texture,"playback_map":{k:{**asdict(v),"effect":EFFECTS[k]} for k,v in PLAYBACK.items()}})
    osc_schedule=build_osc_schedule(events,layers,bpm=bpm,playback_by_layer=PLAYBACK)
    osc=dump("chapter_34_osc_schedule.json",[asdict(g) for g in osc_schedule])
    # Eight kHz keeps the 95-second structural reference inexpensive; rich
    # playback remains the separate SuperCollider/OSC path.
    wav=output/"chapter_34_complete_piece_reference.wav"
    write_wav(wav,render_events(events,bpm,sample_rate=8000),sample_rate=8000)
    return brief,candidates,ledger,provenance,score,manifest,wav,osc


def run_chapter_34(output=Path("outputs"),*,master_seed=MASTER_SEED,bpm=TEMPO,candidates=False,live=False,host="127.0.0.1",port=57121):
    piece=build_complete_piece(master_seed); paths=write_artifacts(piece,output,bpm)
    events,layers=piece.flattened()
    motif_pitches=tuple(e.pitch for e in SOURCE_MOTIF)
    intervals=tuple(b-a for a,b in zip(motif_pitches,motif_pitches[1:]))
    contour=tuple("up" if x>0 else "down" if x<0 else "same" for x in intervals)
    section_rows=[]
    for s in piece.sections:
        melody=s.layers["melody"]; m=_metrics(tuple(replace(e,start=e.start-s.start) for e in melody))
        section_rows.append(f"{s.id:<12} {s.duration:>5g} {m['range']:>7} {m['attack_density']:>13.2f} {len(s.layers):>6}   {s.material_id}")
    print(f"""COMPOSITION BRIEF
{piece.brief['request']}
Goals: {', '.join(piece.brief['goals'])}

Chapter 34 — Compose a Complete Piece: {TITLE}
Tempo {bpm:g} BPM | meter 4/4 | tonal center C major | {sum(SECTION_DURATIONS)} beats ({sum(SECTION_DURATIONS)*60/bpm:.1f} seconds)

DELEGATION PLAN (established before note generation)
{chr(10).join(f'{k.upper()}: {v}' for k,v in DELEGATION_PLAN.items())}

SOURCE MOTIF (human-authored motif-a)
pitch sequence: {motif_pitches} ({' '.join(pitch_to_name(p) for p in motif_pitches)})
intervals: {intervals} | contour: {contour}
rhythm: {tuple(e.duration for e in SOURCE_MOTIF)} | range: {max(motif_pitches)-min(motif_pitches)} | duration: 6 beats

FORM / ARRANGEMENT TIMELINE
{chr(10).join(f'{s.id:<12} {s.start:g}–{s.start+s.duration:g}  {", ".join(s.layers)}' for s in piece.sections)}

A: motif-a in four phrases; stable I–vi–IV–V–I–V harmony; roots-and-fifths bass; sustained voice-led-register chords.
A' candidates: {', '.join(c.id+" ("+c.transformation+")" for c in piece.a_prime_candidates)}
Selected {RECORDED_A_PRIME_SELECTION}; selection source: recorded human selection; alternatives preserved.
B: six seeded constrained-random-walk candidates; constraints C4–C5, <=7-semitone leap, finite rhythm, 24 beats, tonic ending.
Trace: {piece.trace}
Selected {RECORDED_B_SELECTION}; selection source: recorded human selection; no preference was inferred.
Human revision {REVISION_ID}: final C4 changed from {piece.b_before_revision[-1].start:g}/{piece.b_before_revision[-1].duration:g} to beat 22/duration 2.

Section      Beats   Range   Attacks/Beat Layers   Source
{chr(10).join(section_rows)}

A / A' / A'': motif source shared; A' rhythm changed; A'' register and texture changed; primary rhythmic identity returns.
B / A: source, event rhythm, register profile, and harmonic plan are reported separately; this is objective contrast, not an aesthetic judgment.
DEVELOPMENT PROVENANCE: motif-a → first-three-note fragment → sequence repetitions → diminished and inverted fragment.
RETURN MAP: motif pitches/interval pattern and rhythmic shape return one octave higher; harmony, bass, and full texture change.
CODA: existing three-note fragment is augmented over IV–V–I–I; attack density falls and the final tonic harmony lasts four beats.

HARMONIC TIMELINE
{chr(10).join(f"{h['section']:<12} beat {h['beat']:>5g} degree {h['degree']} chord {' '.join(h['chord'])}" for h in piece.harmonic_timeline)}

WORKFLOW
1. Brief authored; 2. Form chosen; 3. Source motif authored; 4. A built; 5. A' candidates generated; 6. A' selected; 7. B candidates generated; 8. B selected; 9. B revised; 10. Development derived; 11. A'' returned; 12. Coda designed; 13. Layers arranged; 14. Score finalized; 15. Playback configured; 16. Audio rendered / OSC prepared.

The final score is generation + selection + transformation + revision + arrangement, not raw generator output. Instrument, pan, and effects remain playback metadata and do not alter the symbolic score. Composition finished is a recorded human decision.
Created:
{chr(10).join(map(str,paths))}""")
    if candidates:
        print("\nCANDIDATE DETAILS\n"+"\n".join(f"{c.id}: {c.metrics}" for c in piece.a_prime_candidates+piece.b_candidates))
    if live:
        client=OscNoteClient(host,port); client.ping(); execute_osc_schedule(build_osc_schedule(events,layers,bpm=bpm,playback_by_layer=PLAYBACK),client,verbose=True)
