"""Small deterministic process helpers and the Chapter 32 composition recipe.

These functions describe operations on ordinary :class:`NoteEvent` values.  They
are deliberately not a generic process framework or a claim about minimalist
music as a whole.
"""
from __future__ import annotations

from dataclasses import dataclass, replace
from math import gcd
from typing import Sequence, TypeVar

from .events import NoteEvent

T = TypeVar("T")


def rotate_sequence(values: Sequence[T], steps: int) -> tuple[T, ...]:
    """Rotate left by ``steps``; negative steps rotate right."""
    result = tuple(values)
    if not result:
        return result
    offset = steps % len(result)
    return result[offset:] + result[:offset]


def rotate_pattern(pattern: Sequence[NoteEvent], steps: int, *, pitches: bool = True,
                   rhythm: bool = False) -> tuple[NoteEvent, ...]:
    """Rotate pitch order and/or inter-onset durations independently."""
    source = tuple(pattern)
    pitch_values = rotate_sequence([e.pitch for e in source], steps) if pitches else tuple(e.pitch for e in source)
    durations = rotate_sequence([e.duration for e in source], steps) if rhythm else tuple(e.duration for e in source)
    starts: list[float] = []
    cursor = 0.0
    for duration in durations:
        starts.append(cursor); cursor += duration
    return tuple(replace(e, pitch=pitch_values[i], start=starts[i], duration=durations[i])
                 for i, e in enumerate(source))


def additive_patterns(pattern: Sequence[T]) -> tuple[tuple[T, ...], ...]:
    """Return deterministic leading prefixes of sizes one through N."""
    source = tuple(pattern)
    return tuple(source[:size] for size in range(1, len(source) + 1))


def subtractive_patterns(pattern: Sequence[T]) -> tuple[tuple[T, ...], ...]:
    """Return deterministic leading prefixes of sizes N through one."""
    source = tuple(pattern)
    return tuple(source[:size] for size in range(len(source), 0, -1))


def substitute_pattern_steps(source: Sequence[T], target: Sequence[T]) -> tuple[tuple[T, ...], ...]:
    """Replace one position from left to right, including both endpoints."""
    a, b = tuple(source), tuple(target)
    if len(a) != len(b):
        raise ValueError("source and target must have equal lengths")
    return tuple(b[:count] + a[count:] for count in range(len(a) + 1))


def phase_offsets(cycles: int, step: float = .25, cycle_length: float = 1.0) -> tuple[float, ...]:
    """Return bounded discrete offsets which wrap at ``cycle_length``."""
    if cycles < 0 or step <= 0 or cycle_length <= 0:
        raise ValueError("cycles must be nonnegative and timing values positive")
    return tuple(round((cycle * step) % cycle_length, 10) for cycle in range(cycles))


def realignment_period(first: int, second: int) -> int:
    """Return the least common multiple of positive integer cycle lengths."""
    if first <= 0 or second <= 0:
        raise ValueError("cycle lengths must be positive")
    return first * second // gcd(first, second)


def accumulated_layers(order: Sequence[str]) -> tuple[tuple[str, ...], ...]:
    """Return the unchanged active set after each named layer enters."""
    names = tuple(order)
    return tuple(names[:count] for count in range(1, len(names) + 1))


@dataclass(frozen=True)
class ProcessTransition:
    beat: float
    cycle: int
    process: str
    previous_state: object
    new_state: object


@dataclass(frozen=True)
class ProcessStudy:
    title: str
    bpm: float
    meter: str
    total_beats: float
    source_a: tuple[NoteEvent, ...]
    source_b: tuple[NoteEvent, ...]
    events: tuple[NoteEvent, ...]
    layers: tuple[str, ...]
    trace: tuple[ProcessTransition, ...]


def source_pattern_a() -> tuple[NoteEvent, ...]:
    """Original four-note, two-beat material used throughout Chapter 32."""
    return (NoteEvent(60, 0, .5, 78), NoteEvent(63, .5, .5, 74),
            NoteEvent(67, 1, .5, 80), NoteEvent(62, 1.5, .5, 76))


def source_pattern_b() -> tuple[NoteEvent, ...]:
    """Original three-beat companion whose cycle crosses 4/4 barlines."""
    return (NoteEvent(72, 0, .5, 66), NoteEvent(69, 1, .5, 64),
            NoteEvent(74, 2, .5, 68))


def _repeat(pattern: Sequence[NoteEvent], start: float, end: float, cycle: float,
            offset: float = 0) -> list[NoteEvent]:
    events: list[NoteEvent] = []
    cursor = start + offset
    while cursor < end:
        events.extend(replace(e, start=e.start + cursor) for e in pattern
                      if e.start + cursor < end)
        cursor += cycle
    return events


def build_process_study(bpm: float = 96) -> ProcessStudy:
    """Build a deterministic, bounded 64-beat process arc in eight stages."""
    a, b = source_pattern_a(), source_pattern_b()
    tagged: list[tuple[NoteEvent, str]] = []
    trace: list[ProcessTransition] = []
    # A remains present; its state changes gradually, then returns alone.
    for stage in range(8):
        start, end = stage * 8.0, (stage + 1) * 8.0
        rotation = 0 if stage < 2 else min(stage - 1, 3)
        pitches = tuple(e.pitch for e in rotate_pattern(a, rotation))
        if stage in (5, 6):
            target = (65, 63, 70, 62)
            pitches = substitute_pattern_steps(pitches, target)[stage - 4]
        current = tuple(replace(e, pitch=pitches[i]) for i, e in enumerate(a))
        tagged += [(e, "pattern_a") for e in _repeat(current, start, end, 2)]
        if stage >= 1 and stage <= 6:
            roots = (36, 41, 45, 43)
            root = roots[int(start // 16)]
            tagged += [(NoteEvent(root, beat, 2, 58), "bass") for beat in (start, start + 4)]
        if 3 <= stage <= 6:
            offset = (0, .25, .5, .75)[stage - 3]
            tagged += [(e, "pattern_b") for e in _repeat(b, start, end, 3, offset)]
        if stage in (5, 6):
            high = tuple(replace(e, pitch=e.pitch + 12, duration=.25, velocity=55) for e in a)
            tagged += [(e, "high") for e in _repeat(high, start, end, 2)]
        active = ["pattern_a"] + (["bass"] if 1 <= stage <= 6 else []) + (["pattern_b"] if 3 <= stage <= 6 else []) + (["high"] if stage in (5, 6) else [])
        previous = [] if stage == 0 else trace[-1].new_state
        state = {"rotation": rotation, "active_layers": active,
                 "phase_offset": (0, .25, .5, .75)[stage - 3] if 3 <= stage <= 6 else 0,
                 "substitutions": stage - 4 if stage in (5, 6) else 0}
        trace.append(ProcessTransition(start, int(start / 2), "stage state", previous, state))
    tagged.sort(key=lambda item: (item[0].start, item[1], item[0].pitch))
    return ProcessStudy("Chapter 32 Process Music Study", bpm, "4/4", 64, a, b,
                        tuple(e for e, _ in tagged), tuple(layer for _, layer in tagged), tuple(trace))
