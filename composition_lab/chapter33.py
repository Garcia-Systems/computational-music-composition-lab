"""Chapter 33: explicit human/algorithm decision allocation and provenance."""
from __future__ import annotations

from collections import Counter
from dataclasses import asdict, dataclass, replace
from enum import StrEnum
import hashlib
import json
from pathlib import Path
import random

from .bass import bass_from_progression
from .evaluation import melody_profile, repetition_profile, rhythm_profile
from .event_rendering import render_events
from .events import NoteEvent
from .osc import PlaybackChoice, build_osc_schedule, execute_osc_schedule, OscNoteClient
from .scales import MAJOR
from .waveform import write_wav


class DecisionCategory(StrEnum):
    HUMAN = "human"
    ALGORITHM = "algorithm"
    HUMAN_SELECTED_ALGORITHM_CANDIDATE = "human_selected_algorithm_candidate"
    DERIVED = "derived"


@dataclass(frozen=True)
class CompositionDecision:
    id: str
    stage: str
    description: str
    category: DecisionCategory
    source: str
    alternatives: tuple[str, ...] = ()
    selection: str | None = None
    seed: int | None = None
    reference: str | None = None
    depends_on: tuple[str, ...] = ()


@dataclass(frozen=True)
class MelodyCandidate:
    id: str
    seed: int
    events: tuple[NoteEvent, ...]
    metrics: dict[str, object]
    constraints: dict[str, bool]


@dataclass(frozen=True)
class Chapter33Study:
    brief: dict[str, object]
    candidates: tuple[MelodyCandidate, ...]
    selected_candidate_id: str
    selected_before_revision: tuple[NoteEvent, ...]
    revised_b: tuple[NoteEvent, ...]
    events: tuple[NoteEvent, ...]
    layers: tuple[str, ...]
    ledger: tuple[CompositionDecision, ...]
    ending_alternatives: dict[str, tuple[NoteEvent, ...]]


MASTER_SEED = 2026
RECORDED_B_SELECTION = "candidate-03"
RECORDED_ENDING_SELECTION = "ending-B-longer-note"
PLAYBACK = {"melody": PlaybackChoice("articulated_saw", .2),
            "bass": PlaybackChoice("sine", -.25), "groove": PlaybackChoice("pulse", .35)}


def derive_seed(master_seed: int, identity: str) -> int:
    """Derive a stable local seed without process-randomized ``hash()``."""
    digest = hashlib.sha256(f"chapter-33:{master_seed}:{identity}".encode()).digest()
    return int.from_bytes(digest[:8], "big")


def composition_brief(master_seed: int = MASTER_SEED, candidate_count: int = 4,
                      max_leap: int = 7) -> dict[str, object]:
    return {
        "goal": "Create a 32-beat instrumental study with clear return, moderate rhythmic activity, and contrasting middle material.",
        "constraints": {"key": "C major", "meter": "4/4", "form": "A B A'",
                        "duration_beats": 32, "melody_range": [60, 72],
                        "maximum_melody_leap": max_leap, "layers": 3,
                        "moderate_activity_translation": "1–2 attacks per beat"},
        "delegation_plan": {"goal": "human", "form": "human", "harmony": "human",
            "A_motif": "human", "B_candidates": "algorithm", "B_selection": "human-recorded",
            "bass_strategy": "human", "bass_events": "derived", "groove_recipe": "human",
            "groove_events": "derived", "playback_map": "human", "OSC_conversion": "derived"},
        "master_seed": master_seed, "candidate_count": candidate_count,
    }


def _candidate_metrics(events: tuple[NoteEvent, ...]) -> dict[str, object]:
    pitches = tuple(event.pitch for event in events)
    melody, rhythm = melody_profile(pitches), rhythm_profile(events)
    chord_tones = {0, 4, 7}
    return {"range": melody.pitch_range,
            "average_interval": melody.average_absolute_interval,
            "steps": melody.step_count, "leaps": melody.leap_count,
            "repetition": repetition_profile(pitches)["immediate_pitch_repeats"],
            "rhythm_density": rhythm.attacks_per_beat,
            "chord_tone_percentage": 100 * sum(p % 12 in chord_tones for p in pitches) / len(pitches)}


def generate_candidates(master_seed: int = MASTER_SEED, candidate_count: int = 4,
                        max_leap: int = 7) -> tuple[MelodyCandidate, ...]:
    """Generate constraint-valid random-walk phrases; never select among them."""
    scale = (60, 62, 64, 65, 67, 69, 71, 72)
    result = []
    for number in range(1, candidate_count + 1):
        identity = f"candidate-{number:02d}"
        seed, rng = derive_seed(master_seed, identity), random.Random(derive_seed(master_seed, identity))
        pitches = [rng.choice(scale[:-1])]
        for _ in range(14):
            allowed = [pitch for pitch in scale if abs(pitch - pitches[-1]) <= max_leap]
            pitches.append(rng.choice(allowed))
        pitches.append(60)  # authored objective: required tonic ending
        if abs(pitches[-1] - pitches[-2]) > max_leap:
            pitches[-2] = rng.choice(tuple(p for p in scale if abs(p - 60) <= max_leap))
        events = tuple(NoteEvent(pitch, float(i), 1.0, 92) for i, pitch in enumerate(pitches))
        checks = {"pitch_range": all(60 <= p <= 72 for p in pitches),
                  "duration": events[-1].start + events[-1].duration == 16,
                  "maximum_leap": all(abs(b-a) <= max_leap for a, b in zip(pitches, pitches[1:])),
                  "required_ending": pitches[-1] == 60}
        if not all(checks.values()):
            raise AssertionError("generator produced an invalid candidate")
        result.append(MelodyCandidate(identity, seed, events, _candidate_metrics(events), checks))
    return tuple(result)


def _shift(events: tuple[NoteEvent, ...], amount: float) -> tuple[NoteEvent, ...]:
    return tuple(replace(event, start=event.start + amount) for event in events)


def build_chapter_33_study(master_seed: int = MASTER_SEED,
                           selected_candidate_id: str = RECORDED_B_SELECTION,
                           max_leap: int = 7) -> Chapter33Study:
    brief = composition_brief(master_seed, 4, max_leap)
    candidates = generate_candidates(master_seed, 4, max_leap)
    by_id = {candidate.id: candidate for candidate in candidates}
    if selected_candidate_id not in by_id:
        raise ValueError("recorded selection must identify an existing candidate")
    selected = by_id[selected_candidate_id].events
    # A factual human-directed edit. It may be a no-op only if generator rules change,
    # so preserve the before value and enforce the authored target.
    # The recipe asks for a calmer approach to the required tonic: this is the
    # explicit structural translation, not natural-language interpretation.
    human_revised = selected[:-2] + (replace(selected[-2], pitch=62), selected[-1])
    ending_alternatives = {
        "ending-A-tonic": human_revised,
        "ending-B-longer-note": human_revised[:-2] + (replace(human_revised[-2], start=14, duration=2),),
        "ending-C-descending": human_revised[:-3] + (NoteEvent(64, 13, 1, 92), NoteEvent(62, 14, 1, 92), NoteEvent(60, 15, 1, 92)),
    }
    revised_b = ending_alternatives[RECORDED_ENDING_SELECTION]
    motif = tuple(NoteEvent(p, s, d, 96) for p, s, d in
                  ((60, 0, 1), (64, 1, 1), (67, 2, 2), (64, 4, 1), (62, 5, 1), (60, 6, 2)))
    a_prime_options = {"ending variation": motif[:-1] + (replace(motif[-1], duration=2),),
                       "rhythmic variation": tuple(replace(e, duration=min(e.duration, 1)) for e in motif),
                       "register variation": tuple(replace(e, pitch=e.pitch + 12) for e in motif)}
    a_prime = _shift(a_prime_options["register variation"], 24)
    melody = motif + _shift(revised_b, 8) + a_prime
    bass = bass_from_progression(60, MAJOR, (1, 4, 5, 1), (8, 8, 8, 8), strategy="roots_and_fifths")
    groove = tuple(NoteEvent(36, float(beat), .2, 55) for beat in range(32))
    events, layers = melody + bass + groove, (("melody",) * len(melody) +
        ("bass",) * len(bass) + ("groove",) * len(groove))
    candidate_ids = tuple(by_id)
    ledger = (
        CompositionDecision("brief-goal", "intention", "Goal, C-major context, 32 beats, and three layers", DecisionCategory.HUMAN, "authored recipe", reference="brief"),
        CompositionDecision("activity-translation", "constraint", "Translate ‘moderate activity’ to 1–2 attacks per beat", DecisionCategory.HUMAN, "authored recipe", selection="1–2 attacks per beat", reference="brief"),
        CompositionDecision("form", "structure", "Choose A B A'", DecisionCategory.HUMAN, "authored recipe", selection="A B A'", reference="form"),
        CompositionDecision("harmony", "structure", "Choose I–IV–V–I", DecisionCategory.HUMAN, "authored recipe", selection="I IV V I", reference="harmony"),
        CompositionDecision("a-motif", "generation", "Specify section A motif", DecisionCategory.HUMAN, "authored recipe", reference="section-A"),
        CompositionDecision("b-generation", "generation", "Generate bounded random-walk B candidates", DecisionCategory.ALGORITHM, "seeded random walk", candidate_ids, seed=master_seed, reference="candidates"),
        CompositionDecision("b-selection", "selection", "Apply recorded stand-in for authored human selection", DecisionCategory.HUMAN_SELECTED_ALGORITHM_CANDIDATE, "human-recorded", candidate_ids, selected_candidate_id, reference=selected_candidate_id, depends_on=("b-generation",)),
        CompositionDecision("revision-01", "revision", "Set B penultimate pitch to D4 before the required tonic", DecisionCategory.HUMAN, "authored edit", selection="penultimate pitch = 62", reference="section-B", depends_on=("b-selection",)),
        CompositionDecision("ending-generation", "revision", "Propose three structurally explicit endings", DecisionCategory.ALGORITHM, "ending variation recipe", tuple(ending_alternatives), reference="ending-alternatives", depends_on=("revision-01",)),
        CompositionDecision("ending-selection", "selection", "Apply recorded ending selection", DecisionCategory.HUMAN_SELECTED_ALGORITHM_CANDIDATE, "human-recorded", tuple(ending_alternatives), RECORDED_ENDING_SELECTION, reference="section-B", depends_on=("ending-generation",)),
        CompositionDecision("a-prime-generation", "generation", "Propose three A' transformations", DecisionCategory.ALGORITHM, "motif transformations", tuple(a_prime_options), reference="section-A-prime"),
        CompositionDecision("a-prime-selection", "selection", "Apply recorded A' register-variation choice", DecisionCategory.HUMAN_SELECTED_ALGORITHM_CANDIDATE, "human-recorded", tuple(a_prime_options), "register variation", reference="section-A-prime", depends_on=("a-prime-generation",)),
        CompositionDecision("bass-strategy", "arrangement", "Choose roots-and-fifths bass strategy", DecisionCategory.HUMAN, "authored recipe", selection="roots_and_fifths", reference="bass"),
        CompositionDecision("bass-events", "arrangement", "Instantiate bass from harmony", DecisionCategory.DERIVED, "Chapter 14 bass derivation", reference="bass", depends_on=("bass-strategy", "harmony")),
        CompositionDecision("groove-recipe", "arrangement", "Choose quarter-pulse groove", DecisionCategory.HUMAN, "authored recipe", selection="quarter pulse", reference="groove"),
        CompositionDecision("groove-events", "arrangement", "Instantiate groove events", DecisionCategory.DERIVED, "groove recipe", reference="groove", depends_on=("groove-recipe",)),
        CompositionDecision("playback-map", "playback", "Choose instruments and pan by layer", DecisionCategory.HUMAN, "authored recipe", tuple(PLAYBACK), reference="playback"),
        CompositionDecision("event-placement", "assembly", "Place sections and combine layers", DecisionCategory.DERIVED, "timeline assembly", reference="score"),
        CompositionDecision("osc-conversion", "playback", "Convert finalized events to frequency/time OSC schedule", DecisionCategory.DERIVED, "Chapter 26 conversion", reference="osc-schedule", depends_on=("event-placement", "playback-map")),
    )
    return Chapter33Study(brief, candidates, selected_candidate_id, selected, revised_b,
                          events, layers, ledger, ending_alternatives)


def write_artifacts(study: Chapter33Study, output: Path, bpm: float = 96) -> tuple[Path, ...]:
    output.mkdir(parents=True, exist_ok=True)
    def dump(path: Path, value: object) -> None:
        path.write_text(json.dumps(value, indent=2, sort_keys=True) + "\n")
    brief, candidates, ledger = (output / "chapter_33_brief.json", output / "chapter_33_candidates.json", output / "chapter_33_decision_ledger.json")
    score, manifest = output / "chapter_33_human_algorithm_study.json", output / "chapter_33_manifest.json"
    wav, osc = output / "chapter_33_human_algorithm_study.wav", output / "chapter_33_osc_schedule.json"
    dump(brief, study.brief)
    dump(candidates, [{**asdict(c), "events": [asdict(e) for e in c.events]} for c in study.candidates])
    dump(ledger, [asdict(d) for d in study.ledger])
    dump(score, {"events": [{"event": asdict(e), "layer": layer} for e, layer in zip(study.events, study.layers, strict=True)],
                 "sections": {"A": [0, 8], "B": [8, 24], "A_prime": [24, 32]},
                 "revision_history": {"before": [asdict(e) for e in study.selected_before_revision], "after": [asdict(e) for e in study.revised_b]}})
    dump(manifest, {"brief": study.brief["goal"], "key": "C major", "tempo": bpm, "form": "A B A'",
        "constraints": study.brief["constraints"], "master_seed": study.brief["master_seed"],
        "candidate_count": len(study.candidates), "recorded_selections": {"B": study.selected_candidate_id,
        "ending": RECORDED_ENDING_SELECTION, "A_prime": "register variation"},
        "revision_operations": ["set penultimate pitch to 62", "replace final two attacks with one two-beat note"],
        "playback_map": {k: asdict(v) for k, v in PLAYBACK.items()}})
    write_wav(wav, render_events(study.events, bpm))
    schedule = build_osc_schedule(study.events, study.layers, bpm=bpm, playback_by_layer=PLAYBACK)
    dump(osc, [asdict(group) for group in schedule])
    candidate_wavs = []
    for candidate in study.candidates:
        path = output / f"chapter_33_{candidate.id.replace('-', '_')}.wav"
        write_wav(path, render_events(candidate.events, bpm)); candidate_wavs.append(path)
    return brief, candidates, ledger, score, manifest, wav, osc, *candidate_wavs


def run_chapter_33(output: Path = Path("outputs"), *, master_seed: int = MASTER_SEED,
                   bpm: float = 96, live: bool = False, host: str = "127.0.0.1", port: int = 57121) -> None:
    study = build_chapter_33_study(master_seed)
    paths = write_artifacts(study, output, bpm)
    counts = Counter(d.category for d in study.ledger)
    print(f"""Part X — Capstone
Chapter 33 — Human + Algorithm

The final part stops asking what the computer can do and starts asking how those capabilities should be used inside an actual compositional process.

HUMAN INTENTION → DELEGATION → ALGORITHMIC CANDIDATES → INSPECTION → LISTENING → SELECTION → REVISION → FINAL MUSICAL DECISION

Decision categories: human-decided; algorithm-decided; algorithm-proposed / human-selected; derived / mechanical.
Decision provenance records observable choices, alternatives, constraints, selections, and seeds—not hidden reasoning.

BRIEF
{study.brief['goal']}
Constraints: {study.brief['constraints']}
Delegation plan: {study.brief['delegation_plan']}

Candidates (descriptive facts only):
{chr(10).join(f'{c.id} seed={c.seed} metrics={c.metrics} valid={all(c.constraints.values())}' for c in study.candidates)}

VALID ≠ PREFERRED. Metrics and constraints describe candidates; they do not replace listening or select a candidate.
Recorded selection: {study.selected_candidate_id}. In the executable textbook, this is a recorded stand-in for a human selection made during the authored experiment; the program inferred no preference.
Human annotation (authored, not a metric): the selected phrase leaves space for the final return.
Revision: set the penultimate pitch to D4 before the required tonic; translate “less active ending” into fewer attacks/longer durations; propose three endings; recorded selection={RECORDED_ENDING_SELECTION}.

Total decisions recorded: {len(study.ledger)}
Human-decided: {counts[DecisionCategory.HUMAN]}
Algorithm-decided: {counts[DecisionCategory.ALGORITHM]}
Algorithm-proposed / human-selected: {counts[DecisionCategory.HUMAN_SELECTED_ALGORITHM_CANDIDATE]}
Derived: {counts[DecisionCategory.DERIVED]}
Counting decisions does not measure creative contribution; no creativity or authorship percentage is implied.

PROVENANCE BY LAYER / SECTION
FORM human | HARMONY human | A melody human | B melody algorithm-proposed/human-selected/revised
A' transformation algorithm-proposed/human-selected | BASS human strategy + derived events
GROOVE human recipe + derived events | PLAYBACK human map + derived conversion

Composition Brief
├── Form [human]
├── Harmony [human]
├── A motif [human]
├── B candidates [algorithm]
│   └── {study.selected_candidate_id} [human-selected] → revision [human]
├── A' candidates [algorithm] → register variation [human-selected]
└── Bass/groove/OSC events [derived]

Choosing possibility-space rules and the generator is a compositional act. A seed matters only inside that design.
Randomness supplies variation, not intention. Constraints are not taste; metrics are not taste; provenance is not aesthetics.
A system is not simply human- or computer-composed: authorship is layered, and Version A would still be bounded by human-designed vocabularies and stopping conditions.

Artifacts:
{chr(10).join(map(str, paths))}
""")
    if live:
        schedule = build_osc_schedule(study.events, study.layers, bpm=bpm, playback_by_layer=PLAYBACK)
        execute_osc_schedule(schedule, OscNoteClient(host, port))
