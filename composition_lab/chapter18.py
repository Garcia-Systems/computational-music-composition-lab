"""Deterministic studies for Chapter 18: constraints define spaces, not taste."""

from __future__ import annotations

from dataclasses import dataclass, replace
from itertools import product
from pathlib import Path

from .constraints import (
    CandidateEvaluation, Constraint, SearchResult, all_pitches_in_scale,
    at_most_n_long_notes, constraint_funnel, contains_interval_pattern,
    ends_on_pitch_class, enumerate_pitch_candidates, find_valid_candidates,
    maximum_leap_at_most, melodic_range_at_most,
    melody_from_pitches_and_durations, minimum_stepwise_fraction,
    no_immediate_repeated_pitches, starts_on_pitch_class, has_note_count,
    strong_beat_chord_tones, total_duration_equals, within_pitch_range,
)
from .event_rendering import render_events
from .events import NoteEvent
from .melody_harmony import HarmonicSpan
from .scales import MAJOR
from .waveform import write_wav

PITCH_POOL = (60, 62, 64, 65, 67)
CAPSTONE_POOL = (60, 62, 64, 65, 67, 69, 71)
FIXED_DURATIONS = (1.0, 0.5, 0.5, 1.0)
CAPSTONE_DURATIONS = (1.0, 1.0, 2.0, 1.0, 1.0, 2.0)
HARMONY = (
    HarmonicSpan(0, 2, (48, 52, 55), 1),
    HarmonicSpan(2, 2, (53, 57, 60), 4),
    HarmonicSpan(4, 2, (55, 59, 62), 5),
    HarmonicSpan(6, 2, (48, 52, 55), 1),
)
CHAPTER_18_FILENAMES = (
    "chapter_18_valid_candidate_01.wav", "chapter_18_valid_candidate_02.wav",
    "chapter_18_valid_candidate_03.wav", "chapter_18_rhythm_candidate_01.wav",
    "chapter_18_rhythm_candidate_02.wav", "chapter_18_rhythm_candidate_03.wav",
    "chapter_18_harmony_constraint_fail.wav", "chapter_18_harmony_constraint_pass.wav",
    "chapter_18_constraint_capstone.wav",
)


def pitch_constraints(max_leap: int = 5) -> tuple[Constraint, ...]:
    """Return the chapter's simple rules in visible funnel order."""
    return (
        Constraint("4 notes", lambda p: has_note_count(p, 4)),
        Constraint("Pitch range C4-G4", lambda p: within_pitch_range(p, 60, 67)),
        Constraint("C-major collection", lambda p: all_pitches_in_scale(p, 60, MAJOR)),
        Constraint("Start on tonic", lambda p: starts_on_pitch_class(p, 0)),
        Constraint("End on tonic", lambda p: ends_on_pitch_class(p, 0)),
        Constraint(f"Maximum leap <= {max_leap}", lambda p: maximum_leap_at_most(p, max_leap)),
        Constraint("No immediate repeats", no_immediate_repeated_pitches),
    )


def capstone_constraints() -> tuple[Constraint, ...]:
    return (
        Constraint("Start on tonic", lambda p: starts_on_pitch_class(p, 0)),
        Constraint("End on tonic", lambda p: ends_on_pitch_class(p, 0)),
        Constraint("C-major collection", lambda p: all_pitches_in_scale(p, 60, MAJOR)),
        Constraint("Melodic range <= 12", lambda p: melodic_range_at_most(p, 12)),
        Constraint("Maximum leap <= 5", lambda p: maximum_leap_at_most(p, 5)),
        Constraint("At least 50% steps", lambda p: minimum_stepwise_fraction(p, .5)),
        Constraint("No immediate repeats", no_immediate_repeated_pitches),
        # The capstone's deliberately narrow interpretation checks chord-change
        # beats (0, 2, 4, 6); the reusable helper can check every integer beat.
        Constraint("Chord-change tones", lambda p: strong_beat_chord_tones(tuple(
            event for event in melody_from_pitches_and_durations(p, CAPSTONE_DURATIONS)
            if event.start % 2 == 0), HARMONY)),
    )


@dataclass(frozen=True)
class Chapter18Study:
    pitch_candidates: tuple[tuple[int, ...], ...]
    pitch_search: SearchResult
    pitch_funnel: tuple[tuple[str, int], ...]
    impossible_funnel: tuple[tuple[str, int], ...]
    rhythm_candidates: tuple[tuple[float, ...], ...]
    capstone_candidates: tuple[tuple[int, ...], ...]
    capstone_funnel: tuple[tuple[str, int], ...]


def build_chapter_18_study() -> Chapter18Study:
    pitches = enumerate_pitch_candidates(PITCH_POOL, 4)
    constraints = pitch_constraints()
    search = find_valid_candidates(pitches, constraints)
    impossible = constraints[:5] + (
        Constraint("Also end on G", lambda p: ends_on_pitch_class(p, 7)),
    )
    rhythm_space = tuple(product((0.5, 1.0, 2.0), repeat=4))
    rhythms = tuple(r for r in rhythm_space
                    if total_duration_equals(r, 4).passed
                    and at_most_n_long_notes(r, 1).passed)
    capstone_space = enumerate_pitch_candidates(CAPSTONE_POOL, 6)
    cap_constraints = capstone_constraints()
    capstone = find_valid_candidates(capstone_space, cap_constraints).valid
    return Chapter18Study(
        pitches, search, constraint_funnel(pitches, constraints),
        constraint_funnel(pitches, impossible), rhythms, capstone,
        constraint_funnel(capstone_space, cap_constraints),
    )


def selected_candidates(candidates: tuple[tuple[int, ...], ...]) -> tuple[tuple[int, ...], ...]:
    """Choose first, middle, last solely for deterministic audible comparison."""
    if not candidates:
        return ()
    indices = (0, len(candidates) // 2, len(candidates) - 1)
    return tuple(candidates[index] for index in indices)


def _harmony_events() -> tuple[NoteEvent, ...]:
    return tuple(NoteEvent(pitch, span.start, span.duration, 42)
                 for span in HARMONY for pitch in span.pitches)


def render_chapter_18(output_directory: Path = Path("outputs")) -> tuple[Path, ...]:
    """Render a deliberately small set of deterministic listening examples."""
    study = build_chapter_18_study()
    paths = tuple(output_directory / name for name in CHAPTER_18_FILENAMES)
    selected = selected_candidates(study.pitch_search.valid)
    scores: list[tuple[NoteEvent, ...]] = [
        melody_from_pitches_and_durations(candidate, FIXED_DURATIONS)
        for candidate in selected
    ]
    rhythm_pitches = (60, 62, 64, 60)
    scores.extend(melody_from_pitches_and_durations(rhythm_pitches, rhythm)
                  for rhythm in study.rhythm_candidates[:3])
    harmony_fail = melody_from_pitches_and_durations((60, 62, 64, 60), (1, 1, 1, 1))
    harmony_pass = melody_from_pitches_and_durations((60, 64, 65, 60), (1, 1, 1, 1))
    scores.extend((_harmony_events() + harmony_fail, _harmony_events() + harmony_pass))

    capstone_events: list[NoteEvent] = []
    offset = 0.0
    for candidate in selected_candidates(study.capstone_candidates):
        phrase = _harmony_events() + melody_from_pitches_and_durations(
            candidate, CAPSTONE_DURATIONS, velocity=92)
        capstone_events.extend(replace(event, start=event.start + offset) for event in phrase)
        offset += 9.0  # eight-beat phrase plus one beat of comparative silence
    scores.append(tuple(capstone_events))
    for path, score in zip(paths, scores, strict=True):
        write_wav(path, render_events(score, 108))
    return paths


def failure_counts(search: SearchResult) -> tuple[tuple[str, int], ...]:
    """Count overlapping failure reasons: one candidate can increment many rows."""
    names = tuple(result.name for result in search.rejected[0].results) if search.rejected else ()
    return tuple((name, sum(not evaluation.results[index].passed
                            for evaluation in search.rejected))
                 for index, name in enumerate(names))


def rejected_example(study: Chapter18Study) -> CandidateEvaluation:
    """Return a deterministic rejection whose leap failure is easy to inspect."""
    wanted = (60, 67, 62, 60)
    return next(item for item in study.pitch_search.rejected if item.candidate == wanted)
