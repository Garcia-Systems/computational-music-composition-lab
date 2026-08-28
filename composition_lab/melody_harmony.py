"""Conservative melody-against-harmony tools for Chapter 12.

Chord membership and interval overlap are objective computations.  The local
names supplied here are deliberately narrow descriptions, not judgments about
quality, consonance, or style.
"""

from __future__ import annotations

from collections.abc import Sequence
from dataclasses import dataclass

from .events import NoteEvent


@dataclass(frozen=True)
class HarmonicSpan:
    """A chord occupying the half-open beat interval ``[start, end)``."""

    start: float
    duration: float
    pitches: tuple[int, ...]
    degree: int | None = None

    def __post_init__(self) -> None:
        if self.start < 0 or self.duration <= 0:
            raise ValueError("harmonic spans require start >= 0 and duration > 0")
        if not self.pitches:
            raise ValueError("a harmonic span requires at least one pitch")

    @property
    def end(self) -> float:
        return self.start + self.duration


@dataclass(frozen=True)
class MelodyHarmonyRelation:
    """Objective chord membership plus an optional conservative local label."""

    event: NoteEvent
    harmony: HarmonicSpan
    chord_tone: bool
    relation: str


def active_harmony_at(beat: float, spans: Sequence[HarmonicSpan]) -> HarmonicSpan | None:
    """Return the span satisfying ``start <= beat < end``, or ``None``.

    Thus an onset exactly at a chord boundary belongs to the new chord. Spans
    must not overlap, because overlapping answers would be ambiguous.
    """
    matches = [span for span in spans if span.start <= beat < span.end]
    if len(matches) > 1:
        raise ValueError("harmonic spans must not overlap")
    return matches[0] if matches else None


def harmonies_during_event(event: NoteEvent, spans: Sequence[HarmonicSpan]) -> tuple[HarmonicSpan, ...]:
    """Return spans with positive-duration overlap with an event.

    Merely touching at an endpoint is not overlap: ``event.start < span.end``
    and ``event.end > span.start`` must both hold.
    """
    end = event.start + event.duration
    return tuple(span for span in spans if event.start < span.end and end > span.start)


def is_chord_tone(pitch: int, chord_pitches: Sequence[int]) -> bool:
    """Test octave-independent pitch-class membership in a chord."""
    return pitch % 12 in {member % 12 for member in chord_pitches}


def _step(first: NoteEvent, second: NoteEvent) -> bool:
    return abs(second.pitch - first.pitch) in (1, 2)


def is_passing_tone(previous: NoteEvent, current: NoteEvent, next_event: NoteEvent,
                    chord: Sequence[int]) -> bool:
    """Recognize only chord-tone → same-direction steps → chord-tone."""
    into = current.pitch - previous.pitch
    out = next_event.pitch - current.pitch
    return (not is_chord_tone(current.pitch, chord)
            and is_chord_tone(previous.pitch, chord)
            and is_chord_tone(next_event.pitch, chord)
            and abs(into) in (1, 2) and abs(out) in (1, 2)
            and into * out > 0)


def is_neighbor_tone(previous: NoteEvent, current: NoteEvent, next_event: NoteEvent,
                     chord: Sequence[int]) -> bool:
    """Recognize a one-step departure from and return to one absolute pitch."""
    return (previous.pitch == next_event.pitch
            and is_chord_tone(previous.pitch, chord)
            and not is_chord_tone(current.pitch, chord)
            and _step(previous, current) and _step(current, next_event))


def is_approach_tone(current: NoteEvent, next_event: NoteEvent,
                     chord: Sequence[int]) -> bool:
    """Recognize a non-chord pitch moving one chromatic/diatonic step to a chord tone."""
    return (not is_chord_tone(current.pitch, chord)
            and is_chord_tone(next_event.pitch, chord) and _step(current, next_event))


def resolves_to_chord_tone(current: NoteEvent, next_event: NoteEvent,
                           chord: Sequence[int]) -> bool:
    """Report the narrow operation non-chord tone → nearby chord tone."""
    return is_approach_tone(current, next_event, chord)


def is_suspension_like(held: NoteEvent, resolution: NoteEvent,
                       spans: Sequence[HarmonicSpan]) -> bool:
    """Detect the chapter example, without claiming every held tone is a suspension.

    The held event must overlap at least two harmonies, be a chord tone in the
    first but not the second, and resolve by step to a tone of the second.
    """
    crossed = harmonies_during_event(held, spans)
    return (len(crossed) >= 2
            and is_chord_tone(held.pitch, crossed[0].pitches)
            and not is_chord_tone(held.pitch, crossed[1].pitches)
            and resolution.start >= crossed[1].start
            and is_approach_tone(held, resolution, crossed[1].pitches))


def analyze_melody(events: Sequence[NoteEvent], spans: Sequence[HarmonicSpan]) -> tuple[MelodyHarmonyRelation, ...]:
    """Classify each onset, leaving unclear non-chord tones explicitly unforced."""
    result: list[MelodyHarmonyRelation] = []
    for index, event in enumerate(events):
        harmony = active_harmony_at(event.start, spans)
        if harmony is None:
            raise ValueError(f"no active harmony at beat {event.start}")
        tone = is_chord_tone(event.pitch, harmony.pitches)
        relation = "chord-tone" if tone else "other-non-chord-tone"
        previous = events[index - 1] if index else None
        following = events[index + 1] if index + 1 < len(events) else None
        # Pattern labels require all involved onsets to have the same harmony.
        same_context = previous is not None and following is not None and (
            active_harmony_at(previous.start, spans) == harmony ==
            active_harmony_at(following.start, spans))
        if not tone and same_context and is_passing_tone(previous, event, following, harmony.pitches):
            relation = "passing"
        elif not tone and same_context and is_neighbor_tone(previous, event, following, harmony.pitches):
            relation = "neighbor"
        elif not tone and following is not None and active_harmony_at(following.start, spans) == harmony \
                and is_approach_tone(event, following, harmony.pitches):
            relation = "approach"
        result.append(MelodyHarmonyRelation(event, harmony, tone, relation))
    return tuple(result)


def chord_tone_percentage(relations: Sequence[MelodyHarmonyRelation]) -> float:
    """Return objective chord-tone event percentage (not a melody score)."""
    return 0.0 if not relations else 100 * sum(r.chord_tone for r in relations) / len(relations)


def chord_tone_duration_percentage(relations: Sequence[MelodyHarmonyRelation]) -> float:
    """Return duration-weighted alignment; overlapping notes count independently."""
    total = sum(r.event.duration for r in relations)
    return 0.0 if not total else 100 * sum(r.event.duration for r in relations if r.chord_tone) / total
