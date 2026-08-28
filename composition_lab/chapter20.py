"""Executable listening studies for Chapter 20: musical memory."""

from __future__ import annotations

from collections import Counter
from dataclasses import dataclass, replace
from pathlib import Path
import random
from collections.abc import Sequence

from .event_rendering import render_events
from .events import NoteEvent
from .markov import (ValidMarkovResult, build_transition_counts,
                     build_transition_counts_from_sequences,
                     generate_markov_sequence, generate_valid_markov_candidate)
from .scales import MAJOR, events_from_degrees
from .waveform import write_wav

TRAINING_PHRASES = (
    (1, 2, 3, 2, 1, 2, 5, 3, 2, 1),
    (1, 3, 5, 4, 3, 2, 1),
    (5, 4, 3, 2, 3, 2, 1),
)
TRAINING_RHYTHM = (1.0, .5, .5, 1.0, 2.0, 1.0, .5, .5, 1.0, 1.0)

CHAPTER_20_FILENAMES = (
    "chapter_20_first_markov_melody.wav",
    "chapter_20_training_sequence.wav", "chapter_20_generated_sequence.wav",
    "chapter_20_independent_random.wav", "chapter_20_markov_random.wav",
    "chapter_20_linear_model.wav", "chapter_20_cyclic_model.wav",
    "chapter_20_markov_c_major.wav", "chapter_20_markov_f_major.wav",
    "chapter_20_frequency_model.wav", "chapter_20_transition_model.wav",
    "chapter_20_independent_rhythm.wav", "chapter_20_markov_rhythm.wav",
    "chapter_20_pitch_rhythm_memory.wav",
    "chapter_20_phrase_training.wav", "chapter_20_phrase_generation.wav",
    "chapter_20_raw_markov.wav", "chapter_20_constrained_markov.wav",
    "chapter_20_seed_10.wav", "chapter_20_seed_20.wav", "chapter_20_seed_30.wav",
    "chapter_20_musical_memory_capstone.wav",
    "chapter_20_musical_memory_capstone_alt.wav",
)


def degrees_to_events(degrees: Sequence[int], tonic: int = 60,
                      durations: Sequence[float] | None = None,
                      velocity: int = 88) -> tuple[NoteEvent, ...]:
    durations = tuple(durations or (.5,) * len(degrees))
    return events_from_degrees(tuple(degrees), tonic, MAJOR, durations, velocity=velocity)


def melody_constraints(maximum_leap: int = 4):
    return (lambda candidate: candidate[-1] == 1,
            lambda candidate: all(abs(b - a) <= maximum_leap
                                  for a, b in zip(candidate, candidate[1:])),
            lambda candidate: all(1 <= degree <= 5 for degree in candidate))


@dataclass(frozen=True)
class MemorySection:
    label: str
    start_state: int
    degrees: tuple[int, ...]
    attempts: int


@dataclass(frozen=True)
class MemoryCapstone:
    seed: int
    sections: tuple[MemorySection, ...]
    events: tuple[NoteEvent, ...]
    valid: bool


def build_memory_capstone(seed: int) -> MemoryCapstone:
    """Generate local melody while retaining a deterministic A A' B A plan."""
    counts = build_transition_counts_from_sequences(TRAINING_PHRASES, cyclic=True)
    master = random.Random(seed)
    sections: list[MemorySection] = []
    for label, start in (("A", 1), ("A'", 1), ("B", 5)):
        result = generate_valid_markov_candidate(
            counts, start, 8, melody_constraints(), random.Random(master.randrange(2 ** 32)), 500)
        if result.candidate is None:
            raise RuntimeError("capstone constraints found no candidate")
        sections.append(MemorySection(label, start, result.candidate, result.attempts))
    sections.append(MemorySection("A", 1, sections[0].degrees, 0))
    events: list[NoteEvent] = []
    for section_index, section in enumerate(sections):
        melody = degrees_to_events(section.degrees, 60, (.5,) * 8, 90)
        events.extend(replace(event, start=event.start + section_index * 4)
                      for event in melody)
        # Fixed roots make the form audible without teaching a harmony-conditioned model.
        root = (48, 53, 55, 48)[section_index]
        events.append(NoteEvent(root, section_index * 4, 4, 54))
    valid = all(all(rule(section.degrees) for rule in melody_constraints())
                for section in sections)
    return MemoryCapstone(seed, tuple(sections), tuple(events), valid)


def _fixed_pitch_events(durations: Sequence[float]) -> tuple[NoteEvent, ...]:
    starts, events = 0.0, []
    for duration in durations:
        events.append(NoteEvent(60, starts, duration, 82))
        starts += duration
    return tuple(events)


def render_chapter_20(output_directory: Path = Path("outputs")) -> tuple[Path, ...]:
    counts = build_transition_counts_from_sequences(TRAINING_PHRASES, cyclic=True)
    generated = generate_markov_sequence(counts, 1, 16, random.Random(20))
    independent = tuple(random.Random(20).choices((1, 2, 3, 4, 5), k=16))
    frequency_rng = random.Random(2026)
    frequencies = Counter(value for phrase in TRAINING_PHRASES for value in phrase)
    frequency_model = tuple(frequency_rng.choices(tuple(sorted(frequencies)),
                                                 tuple(frequencies[k] for k in sorted(frequencies)), k=16))
    rhythm_counts = build_transition_counts(TRAINING_RHYTHM, cyclic=True)
    markov_rhythm = generate_markov_sequence(rhythm_counts, 1.0, 10, random.Random(220))
    independent_rhythm = tuple(random.Random(220).choices(tuple(sorted(set(TRAINING_RHYTHM))), k=10))
    constrained = generate_valid_markov_candidate(counts, 1, 16, melody_constraints(),
                                                   random.Random(221), 500)
    assert constrained.candidate is not None
    linear = generate_markov_sequence(build_transition_counts((1, 2, 3)), 1, 8,
                                      random.Random(1), dead_end="stop")
    cyclic = generate_markov_sequence(build_transition_counts((1, 2, 3), cyclic=True), 1, 8,
                                      random.Random(1))
    pitch_rhythm = generate_markov_sequence(counts, 1, 10, random.Random(222))
    scores = [
        degrees_to_events(generated), degrees_to_events(TRAINING_PHRASES[0]),
        degrees_to_events(generated[:len(TRAINING_PHRASES[0])]),
        degrees_to_events(independent), degrees_to_events(generated),
        degrees_to_events(linear), degrees_to_events(cyclic),
        degrees_to_events(generated, 60), degrees_to_events(generated, 65),
        degrees_to_events(frequency_model), degrees_to_events(generated),
        _fixed_pitch_events(independent_rhythm), _fixed_pitch_events(markov_rhythm),
        degrees_to_events(pitch_rhythm, durations=markov_rhythm),
        degrees_to_events(TRAINING_PHRASES[0]),
        degrees_to_events(generate_markov_sequence(counts, 1, len(TRAINING_PHRASES[0]), random.Random(223))),
        degrees_to_events(generate_markov_sequence(counts, 1, 16, random.Random(221))),
        degrees_to_events(constrained.candidate),
    ]
    scores.extend(degrees_to_events(generate_markov_sequence(counts, 1, 16, random.Random(seed)))
                  for seed in (10, 20, 30))
    scores.extend((build_memory_capstone(2026).events, build_memory_capstone(2027).events))
    paths = tuple(output_directory / name for name in CHAPTER_20_FILENAMES)
    for path, score in zip(paths, scores, strict=True):
        write_wav(path, render_events(score, 108))
    return paths
