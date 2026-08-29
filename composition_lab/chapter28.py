"""Chapter 28: bounded, deterministic, phrase-at-a-time performance."""
from __future__ import annotations

from dataclasses import asdict, dataclass, replace
import json
from pathlib import Path
import random
import time
from collections.abc import Mapping, Sequence

from .composition import DEFAULT_PLAYBACK
from .evaluation import melody_profile
from .event_rendering import render_events
from .events import NoteEvent
from .osc import OSC_HOST, OSC_PORT, OscNoteClient, build_osc_schedule
from .scales import MAJOR
from .texture import MusicalLayer
from .waveform import write_wav


FORM = ("A", "A'", "B", "A")
HARMONY = ((1, 4), (1, 6), (6, 4), (5, 1))
RHYTHMS = ((1.0, 1.0, 1.0, 1.0), (.5, .5, 1.0, 1.0, 1.0),
           (1.5, .5, 1.0, 1.0))
ACTIVE_LAYERS = (("melody", "harmony", "bass"),
                 ("melody", "harmony", "bass", "groove"),
                 ("melody", "harmony", "bass", "groove"),
                 ("melody", "harmony", "bass"))


@dataclass(frozen=True)
class PerformancePlan:
    bpm: float = 108.0
    total_beats: float = 32.0
    section_beats: float = 8.0
    phrase_beats: float = 4.0
    lookahead_beats: float = 4.0
    seed: int = 2026
    tonic: int = 60
    maximum_leap: int = 5

    def __post_init__(self) -> None:
        if min(self.bpm, self.total_beats, self.section_beats,
               self.phrase_beats, self.lookahead_beats) <= 0:
            raise ValueError("tempo and beat quantities must be positive")
        if self.total_beats != len(FORM) * self.section_beats:
            raise ValueError("Chapter 28 uses four equal bounded sections")
        if self.section_beats % self.phrase_beats:
            raise ValueError("phrases must divide sections exactly")
        if self.maximum_leap < 0:
            raise ValueError("maximum_leap must not be negative")


@dataclass(frozen=True)
class PerformanceState:
    current_beat: float = 0.0
    section_index: int = 0
    phrase_index: int = 0
    last_pitch: int | None = None
    last_motif: tuple[int, ...] = ()
    a_motif: tuple[int, ...] = ()
    generation_step: int = 0


@dataclass(frozen=True)
class PerformanceControl:
    beat: float
    parameter: str
    value: int


@dataclass(frozen=True)
class DecisionTraceEntry:
    beat: float
    target_beat: float
    step: int
    section: str
    decision_type: str
    candidates: tuple[object, ...]
    chosen: object
    reason: str


@dataclass(frozen=True)
class GeneratedRegion:
    start_beat: float
    duration_beats: float
    layers: tuple[MusicalLayer, ...]
    rhythm: tuple[float, ...]
    motif_behavior: str
    fallback_used: bool = False

    def flattened(self) -> tuple[tuple[NoteEvent, str], ...]:
        return tuple((event, layer.name) for layer in self.layers for event in layer.events)


@dataclass(frozen=True)
class PerformanceResult:
    plan: PerformancePlan
    regions: tuple[GeneratedRegion, ...]
    trace: tuple[DecisionTraceEntry, ...]
    states: tuple[PerformanceState, ...]
    control_events: tuple[PerformanceControl, ...]

    def event_history(self) -> tuple[tuple[NoteEvent, str], ...]:
        return tuple(sorted((pair for region in self.regions for pair in region.flattened()),
                            key=lambda pair: (pair[0].start, pair[1], pair[0].pitch)))


def _scale(plan: PerformancePlan, section: int) -> tuple[int, ...]:
    ranges = ((60, 72), (64, 76), (57, 76), (60, 72))
    low, high = (x + plan.tonic - 60 for x in ranges[section])
    pcs = set(MAJOR[:-1])
    return tuple(p for p in range(low, high + 1) if (p - plan.tonic) % 12 in pcs)


def _fallback_pitches(plan: PerformancePlan, state: PerformanceState, section: int,
                      count: int) -> tuple[int, ...]:
    source = state.last_motif or (plan.tonic + 12,)
    scale, previous, result = _scale(plan, section), state.last_pitch, []
    for index in range(count):
        candidates = tuple(p for p in scale if previous is None or abs(p - previous) <= plan.maximum_leap)
        target = source[index % len(source)]
        chosen = min(candidates, key=lambda p: (abs(p - target), p))
        result.append(chosen); previous = chosen
    return tuple(result)


def decide_next_region(plan: PerformancePlan, state: PerformanceState, rng: random.Random, *,
                       decision_beat: float | None = None, force_failure: bool = False,
                       deadline_missed: bool = False) -> tuple[GeneratedRegion, PerformanceState, tuple[DecisionTraceEntry, ...]]:
    """Make one musical decision without transport I/O or reseeding ``rng``."""
    start = state.current_beat
    section = min(int(start // plan.section_beats), len(FORM) - 1)
    label = FORM[section]
    trace: list[DecisionTraceEntry] = []
    at = max(0.0, start - plan.lookahead_beats) if decision_beat is None else decision_beat
    rhythm_candidates = RHYTHMS if section != 2 else RHYTHMS[1:]
    rhythm = rng.choice(rhythm_candidates)
    trace.append(DecisionTraceEntry(at, start, state.generation_step, label, "rhythm",
                                    tuple(rhythm_candidates), rhythm,
                                    "selected from finite patterns that sum to four beats"))
    if section == 0:
        behavior = "new motif" if not state.a_motif else "vary previous A motif"
    elif section == 1:
        behavior = "transpose stored A motif"
    elif section == 2:
        behavior = "new motif"
    else:
        behavior = "return stored A motif with bounded variation"
    trace.append(DecisionTraceEntry(at, start, state.generation_step, label, "motif_behavior",
                                    (behavior,), behavior, "explicit section rule"))
    fallback = force_failure or deadline_missed
    pitches: list[int] = []
    scale = _scale(plan, section)
    previous = state.last_pitch
    stored = state.a_motif if section in (1, 3) else ()
    for index in range(len(rhythm)):
        candidates = tuple(p for p in scale if previous is None or abs(p - previous) <= plan.maximum_leap)
        if force_failure:
            candidates = ()
        if fallback:
            pitches = list(_fallback_pitches(plan, state, section, len(rhythm)))
            trace.append(DecisionTraceEntry(at, start, state.generation_step, label, "fallback", candidates,
                                            "previous motif" if state.last_motif else "tonic phrase",
                                            "deadline missed" if deadline_missed else "no valid constrained candidate"))
            break
        if stored and index < len(stored):
            target = stored[index] + (12 if section == 1 else 0)
            nearest = min(candidates, key=lambda p: (abs(p - target), p))
            # The RNG stream is reserved for actual choices; stored-note placement is deterministic.
            chosen = nearest
        else:
            chosen = rng.choice(candidates)
        trace.append(DecisionTraceEntry(at, start, state.generation_step, label, "pitch", candidates, chosen,
                                        "scale, register, and maximum-leap constraints satisfied"))
        pitches.append(chosen)
        previous = chosen
    starts, elapsed = [], 0.0
    for duration in rhythm:
        starts.append(elapsed); elapsed += duration
    melody = tuple(NoteEvent(p, start + local, duration, 94)
                   for p, local, duration in zip(pitches, starts, rhythm, strict=True))
    degree = HARMONY[section][int((start % plan.section_beats) // plan.phrase_beats)]
    chord_pcs = (MAJOR[degree - 1], MAJOR[(degree + 1) % 7], MAJOR[(degree + 3) % 7])
    chord = tuple(plan.tonic + offset for offset in chord_pcs)
    harmony = tuple(NoteEvent(p, start, plan.phrase_beats, 60) for p in chord)
    bass = (NoteEvent(plan.tonic + MAJOR[degree - 1] - 12, start, 2, 76),
            NoteEvent(plan.tonic + MAJOR[degree - 1] - 5, start + 2, 2, 72))
    groove = tuple(NoteEvent(36, start + x, .25, 70) for x in (0, 1.5, 2, 3.5))
    layer_data = {"melody": melody, "harmony": harmony, "bass": bass, "groove": groove}
    layers = tuple(MusicalLayer(name, layer_data[name]) for name in ACTIVE_LAYERS[section])
    motif = tuple(pitches)
    a_motif = motif if section == 0 and not state.a_motif else state.a_motif
    next_start = start + plan.phrase_beats
    next_state = PerformanceState(next_start, min(int(next_start // plan.section_beats), len(FORM) - 1),
                                  state.phrase_index + 1, pitches[-1], motif, a_motif,
                                  state.generation_step + 1)
    trace.append(DecisionTraceEntry(at, start, state.generation_step, label, "state_transition",
                                    (state.current_beat,), next_start, "advance one fixed four-beat phrase"))
    return GeneratedRegion(start, plan.phrase_beats, layers, rhythm, behavior, fallback), next_state, tuple(trace)


def simulate_performance(plan: PerformancePlan = PerformancePlan(), *,
                         controls: Sequence[PerformanceControl] = (),
                         force_failure_at: frozenset[int] = frozenset(),
                         generation_costs: Mapping[int, float] | None = None) -> PerformanceResult:
    """Walk virtual time instantly. Generation costs are synthetic beat values."""
    rng, state = random.Random(plan.seed), PerformanceState()
    regions, trace, states = [], [], [state]
    costs = generation_costs or {}
    while state.current_beat < plan.total_beats:
        step = state.generation_step
        decision_beat = max(0.0, state.current_beat - plan.lookahead_beats)
        missed = costs.get(step, 0.0) > max(plan.lookahead_beats, state.current_beat)
        region, state, entries = decide_next_region(
            plan, state, rng, decision_beat=decision_beat,
            force_failure=step in force_failure_at, deadline_missed=missed)
        regions.append(region); trace.extend(entries); states.append(state)
    return PerformanceResult(plan, tuple(regions), tuple(trace), tuple(states), tuple(controls))


def replay_event_history(path: Path) -> tuple[tuple[NoteEvent, str], ...]:
    """Load recorded events without invoking the generator (trace replay)."""
    data = json.loads(path.read_text())
    return tuple((NoteEvent(**row["event"]), row["layer"]) for row in data)


def write_performance_artifacts(result: PerformanceResult, output_directory: Path) -> tuple[Path, ...]:
    output_directory.mkdir(parents=True, exist_ok=True)
    trace_path = output_directory / "chapter_28_decision_trace.json"
    events_path = output_directory / "chapter_28_performance_events.json"
    manifest_path = output_directory / "chapter_28_manifest.json"
    wav_path = output_directory / "chapter_28_reference.wav"
    trace_path.write_text(json.dumps([asdict(x) for x in result.trace], indent=2, sort_keys=True) + "\n")
    history = result.event_history()
    events_path.write_text(json.dumps([{"event": asdict(e), "layer": layer} for e, layer in history],
                                      indent=2, sort_keys=True) + "\n")
    manifest = {"chapter": 28, "seed": result.plan.seed, "tempo": result.plan.bpm,
                "lookahead": result.plan.lookahead_beats, "total_beats": result.plan.total_beats,
                "phrase_size": result.plan.phrase_beats, "form": FORM,
                "generator_strategy": "scale-constrained random walk with motif memory",
                "fallback_strategy": "repeat previous motif, otherwise tonic phrase",
                "control_events": [asdict(x) for x in result.control_events]}
    manifest_path.write_text(json.dumps(manifest, indent=2, sort_keys=True) + "\n")
    write_wav(wav_path, render_events(tuple(e for e, _ in history), result.plan.bpm))
    return trace_path, events_path, manifest_path, wav_path


def _send_live(result: PerformanceResult, host: str, port: int) -> None:
    """Submit region schedules incrementally against one monotonic origin."""
    client = OscNoteClient(host, port); client.ping()
    origin = time.monotonic()
    for region in result.regions:
        pairs = region.flattened()
        schedule = build_osc_schedule(tuple(x[0] for x in pairs), tuple(x[1] for x in pairs),
                                      bpm=result.plan.bpm, playback_by_layer=DEFAULT_PLAYBACK)
        for group in schedule:
            remaining = origin + group.at_seconds - time.monotonic()
            if remaining > 0: time.sleep(remaining)
            for message in group.messages: client.note(message.arguments)


def run_chapter_28(output_directory: Path = Path("outputs"), *, seed: int = 2026,
                   bpm: float = 108, lookahead: float = 4, replay: bool = False,
                   live: bool = False, host: str = OSC_HOST, port: int = OSC_PORT) -> None:
    events_path = output_directory / "chapter_28_performance_events.json"
    if replay:
        history = replay_event_history(events_path)
        print(f"Chapter 28 — Algorithmic Performance\n\nMode: trace replay\nLoaded {len(history)} recorded events from {events_path}; no decisions regenerated.")
        return
    plan = PerformancePlan(bpm=bpm, lookahead_beats=lookahead, seed=seed)
    controls = (PerformanceControl(0, "rhythm_activity", 1), PerformanceControl(16, "rhythm_activity", 2))
    result = simulate_performance(plan, controls=controls)
    paths = write_performance_artifacts(result, output_directory)
    melody = tuple(e.pitch for e, layer in result.event_history() if layer == "melody")
    profile = melody_profile(melody)
    print(f"""Chapter 28 — Algorithmic Performance

Mode: {'live' if live else 'simulation (virtual time; no sleeping or OSC)'}
Tempo: {bpm:g} BPM | Length: {plan.total_beats:g} beats | Lookahead: {lookahead:g} beats | Seed: {seed}
Preplanned: form, harmony, bass, texture. Generated online: melody, rhythm variants, motif transformations.

Decision timeline
-----------------
{chr(10).join(f'beat {max(0, r.start_beat-plan.lookahead_beats):>4g}: generate phrase {i} for {FORM[int(r.start_beat // 8)]} at target beat {r.start_beat:g} ({r.motif_behavior})' for i, r in enumerate(result.regions))}

Post-performance description (no score)
---------------------------------------
Regions: {len(result.regions)} | Events: {len(result.event_history())} | Decisions: {len(result.trace)}
Fallbacks: {sum(r.fallback_used for r in result.regions)} | Control changes: {len(controls)}
Melody range: {profile.pitch_range} semitones | Average interval: {profile.average_absolute_interval:.2f}
Steps: {profile.step_count} | Leaps: {profile.leap_count}

Artifacts
---------
{chr(10).join(map(str, paths))}

Lookahead prepares future control events; it is not audio-latency compensation or a hard real-time guarantee.
Before performance the melody is incomplete; afterward event history is a complete symbolic record.
""")
    if live:
        print("Sending each generated region through Chapter 26 /note payloads; the performance beat grid remains authoritative.")
        _send_live(result, host, port)
