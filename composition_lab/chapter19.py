"""Seeded, inspectable mechanisms for Chapter 19: controlled randomness."""

from __future__ import annotations

from collections.abc import Callable, Sequence
from dataclasses import dataclass, replace
from pathlib import Path
import random
from functools import lru_cache

from .chapter18 import FIXED_DURATIONS, build_chapter_18_study, pitch_constraints
from .constraints import candidate_is_valid, evaluate_candidate, melody_from_pitches_and_durations
from .event_rendering import render_events
from .events import NoteEvent
from .waveform import write_wav

Candidate = tuple[int, ...]


@lru_cache(maxsize=1)
def _chapter_18_study():
    """Reuse Chapter 18's sizeable exhaustive result within one process."""
    return build_chapter_18_study()

CHAPTER_19_FILENAMES = (
    "chapter_19_seed_10.wav", "chapter_19_seed_20.wav", "chapter_19_seed_30.wav",
    "chapter_19_uniform_pitch_choice.wav", "chapter_19_weighted_pitch_choice.wav",
    "chapter_19_rhythm_seed_1.wav", "chapter_19_rhythm_seed_2.wav",
    "chapter_19_rhythm_seed_3.wav", "chapter_19_random_motif_transpositions.wav",
    "chapter_19_fixed_velocity.wav", "chapter_19_random_velocity.wav",
    "chapter_19_independent_random_melody.wav", "chapter_19_random_walk_melody.wav",
    "chapter_19_weighted_random_walk.wav", "chapter_19_upward_bias.wav",
    "chapter_19_downward_bias.wav", "chapter_19_random_bass_variation.wav",
    "chapter_19_random_groove_variation.wav", "chapter_19_seed_12345.wav",
    "chapter_19_seed_12346.wav", "chapter_19_seeded_capstone.wav",
    "chapter_19_seeded_capstone_alt.wav",
)


def random_valid_candidate(valid_candidates: Sequence[Candidate], rng: random.Random) -> Candidate:
    """Uniformly select from an already validated set."""
    if not valid_candidates:
        raise ValueError("no valid candidates available")
    return rng.choice(valid_candidates)


def weighted_choice(choices: Sequence, weights: Sequence[float], rng: random.Random):
    """Select once after validating a transparent table of non-negative weights."""
    if not choices:
        raise ValueError("choices must not be empty")
    if len(choices) != len(weights):
        raise ValueError("choices and weights must have equal lengths")
    if any(weight < 0 for weight in weights):
        raise ValueError("weights must not be negative")
    if not any(weight > 0 for weight in weights):
        raise ValueError("at least one weight must be positive")
    return rng.choices(choices, weights=weights, k=1)[0]


def bounded_velocities(count: int, base: int, maximum_offset: int,
                       rng: random.Random) -> tuple[int, ...]:
    if count < 0 or maximum_offset < 0:
        raise ValueError("count and maximum_offset must not be negative")
    return tuple(max(0, min(127, base + rng.randint(-maximum_offset, maximum_offset)))
                 for _ in range(count))


@dataclass(frozen=True)
class RejectionResult:
    candidate: Candidate | None
    attempts: int

    @property
    def rejected(self) -> int:
        return self.attempts - int(self.candidate is not None)


def generate_valid_random_candidate(
    candidate_factory: Callable[[random.Random], Candidate],
    constraints: Sequence[Callable[[Candidate], bool]], rng: random.Random,
    max_attempts: int = 1000,
) -> RejectionResult:
    """Propose until every predicate passes, with an explicit finite limit."""
    if max_attempts <= 0:
        raise ValueError("max_attempts must be greater than zero")
    for attempt in range(1, max_attempts + 1):
        candidate = candidate_factory(rng)
        if all(constraint(candidate) for constraint in constraints):
            return RejectionResult(candidate, attempt)
    return RejectionResult(None, max_attempts)


def random_walk_degrees(start_degree: int, length: int, allowed_steps: Sequence[int],
                        min_degree: int, max_degree: int, rng: random.Random,
                        weights: Sequence[float] | None = None) -> tuple[int, ...]:
    """Walk by choosing only moves that are valid at the current boundary."""
    if length < 1 or not min_degree <= start_degree <= max_degree:
        raise ValueError("length must be positive and start_degree must be in range")
    if not allowed_steps:
        raise ValueError("allowed_steps must not be empty")
    if weights is not None and len(weights) != len(allowed_steps):
        raise ValueError("steps and weights must have equal lengths")
    degrees = [start_degree]
    for _ in range(length - 1):
        valid = [(step, weights[index] if weights is not None else 1)
                 for index, step in enumerate(allowed_steps)
                 if min_degree <= degrees[-1] + step <= max_degree]
        if not valid:
            raise ValueError("no allowed move is valid at the current degree")
        step = weighted_choice(tuple(v[0] for v in valid), tuple(v[1] for v in valid), rng)
        degrees.append(degrees[-1] + step)
    return tuple(degrees)


def degrees_to_c_major(degrees: Sequence[int]) -> tuple[int, ...]:
    scale = (60, 62, 64, 65, 67, 69, 71, 72)
    return tuple(scale[degree - 1] for degree in degrees)


def motif_transformations(seed: int, repetitions: int = 4) -> tuple[str, ...]:
    rng = random.Random(seed)
    return tuple(rng.choice(("original", "transpose +5", "retrograde"))
                 for _ in range(repetitions))


@dataclass(frozen=True)
class SeedManifest:
    master: int
    melody: int
    rhythm: int
    bass: int
    motif: int
    texture: int


def seed_manifest(master_seed: int) -> SeedManifest:
    rng = random.Random(master_seed)
    seeds = tuple(rng.randrange(2 ** 32) for _ in range(5))
    return SeedManifest(master_seed, *seeds)


@dataclass(frozen=True)
class SeededComposition:
    manifest: SeedManifest
    events: tuple[NoteEvent, ...]
    decisions: tuple[str, ...]
    valid: bool


def build_seeded_composition(master_seed: int) -> SeededComposition:
    """Build fixed A A' B A form while randomizing logged local decisions."""
    manifest = seed_manifest(master_seed)
    study = _chapter_18_study()
    melody_rng, rhythm_rng = random.Random(manifest.melody), random.Random(manifest.rhythm)
    bass_rng, motif_rng = random.Random(manifest.bass), random.Random(manifest.motif)
    texture_rng = random.Random(manifest.texture)
    melody_index = melody_rng.randrange(len(study.pitch_search.valid))
    melody = study.pitch_search.valid[melody_index]
    rhythm_index = rhythm_rng.randrange(len(study.rhythm_candidates))
    rhythm = study.rhythm_candidates[rhythm_index]
    transformations = tuple(motif_rng.choice(("original", "transpose +5", "retrograde"))
                            for _ in range(4))
    textures = tuple(texture_rng.choice(("sustained", "block", "broken")) for _ in range(4))
    events: list[NoteEvent] = []
    bass_roles: list[str] = []
    for section, transformation in enumerate(transformations):
        pitches = melody[::-1] if transformation == "retrograde" else melody
        if transformation == "transpose +5":
            pitches = tuple(pitch + 5 for pitch in pitches)
        start = section * 4.0
        phrase = melody_from_pitches_and_durations(pitches, rhythm, velocity=88)
        events.extend(replace(event, start=event.start + start) for event in phrase)
        # Hard rule: the first event in every harmonic span is always its root.
        for local_start in (0.0, 2.0):
            root = (48, 53, 55, 48)[section]
            role = weighted_choice(("root", "fifth"), (4, 1), bass_rng)
            bass_roles.extend(("root", role))
            events.append(NoteEvent(root, start + local_start, 1.0, 66))
            events.append(NoteEvent(root if role == "root" else root + 7,
                                    start + local_start + 1.0, 1.0, 62))
    valid = candidate_is_valid(evaluate_candidate(melody, pitch_constraints()))
    decisions = (
        f"melody candidate index: {melody_index}", f"rhythm candidate index: {rhythm_index}",
        f"motif transformations: {', '.join(transformations)}",
        f"bass choices: {' '.join(bass_roles)}", f"textures: {' -> '.join(textures)}",
    )
    return SeededComposition(manifest, tuple(events), decisions, valid)


def _events(pitches: Sequence[int], durations: Sequence[float] | None = None,
            velocities: Sequence[int] | None = None) -> tuple[NoteEvent, ...]:
    durations = durations or (0.5,) * len(pitches)
    score = melody_from_pitches_and_durations(tuple(pitches), tuple(durations))
    if velocities is not None:
        score = tuple(replace(event, velocity=velocities[i]) for i, event in enumerate(score))
    return score


def render_chapter_19(output_directory: Path = Path("outputs")) -> tuple[Path, ...]:
    study = _chapter_18_study()
    scores: list[tuple[NoteEvent, ...]] = []
    for seed in (10, 20, 30):
        scores.append(_events(random_valid_candidate(study.pitch_search.valid, random.Random(seed)),
                              FIXED_DURATIONS))
    pool, weights = (60, 62, 64, 65, 67, 69, 71), (4, 1, 2, 1, 3, 1, 1)
    scores.append(_events(tuple(random.Random(51).choices(pool, k=12))))
    scores.append(_events(tuple(random.Random(51).choices(pool, weights=weights, k=12))))
    for seed in (1, 2, 3):
        scores.append(_events((60, 62, 64, 60), random_valid_candidate(
            study.rhythm_candidates, random.Random(seed))))
    motif = (60, 62, 64, 67)
    transposition_rng = random.Random(61)
    transpositions = tuple(transposition_rng.choice((0, 2, 5, 7, 12)) for _ in range(4))
    scores.append(_events(tuple(p + shift for shift in transpositions for p in motif)))
    scores.append(_events(motif * 2, velocities=(80,) * 8))
    scores.append(_events(motif * 2, velocities=bounded_velocities(8, 80, 5, random.Random(71))))
    independent = tuple(random.Random(81).choice(pool) for _ in range(12))
    walk = degrees_to_c_major(random_walk_degrees(1, 12, (-2, -1, 1, 2), 1, 8, random.Random(81)))
    weighted_walk = degrees_to_c_major(random_walk_degrees(
        1, 12, (-2, -1, 0, 1, 2), 1, 8, random.Random(82), (1, 4, 1, 4, 1)))
    upward = degrees_to_c_major(random_walk_degrees(4, 12, (-2, -1, 1, 2), 1, 8,
                                                    random.Random(83), (1, 1, 4, 3)))
    downward = degrees_to_c_major(random_walk_degrees(4, 12, (-2, -1, 1, 2), 1, 8,
                                                      random.Random(83), (3, 4, 1, 1)))
    scores.extend((_events(independent), _events(walk), _events(weighted_walk),
                   _events(upward), _events(downward)))
    cap = build_seeded_composition(12345)
    scores.append(tuple(event for event in cap.events if event.pitch < 60))  # constrained bass
    groove = tuple(NoteEvent(36, beat, .15, 70 if beat % 1 == 0 else 50)
                   for beat in (0, .5, 1, 2, 2.5, 3))
    scores.append(groove)
    scores.extend((build_seeded_composition(12345).events, build_seeded_composition(12346).events,
                   build_seeded_composition(2026).events, build_seeded_composition(2027).events))
    paths = tuple(output_directory / filename for filename in CHAPTER_19_FILENAMES)
    for path, score in zip(paths, scores, strict=True):
        write_wav(path, render_events(score, 108))
    return paths
