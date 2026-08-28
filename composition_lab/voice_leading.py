"""Small, deterministic voice-leading operations for Chapter 11."""

from __future__ import annotations

from collections.abc import Sequence

from .chords import chord_pitch_classes, invert_chord
from .pitch import _validate_pitch

Voicing = tuple[int, ...]


def _voicing(pitches: Sequence[int], name: str) -> Voicing:
    result = tuple(pitches)
    if not result:
        raise ValueError(f"{name} must not be empty")
    for pitch in result:
        _validate_pitch(pitch)
    if result != tuple(sorted(result)):
        raise ValueError(f"{name} must be sorted ascending")
    return result


def voice_movements(previous: Sequence[int], current: Sequence[int]) -> tuple[int, ...]:
    """Return signed semitone movement at each fixed, sorted voice position."""
    before, after = _voicing(previous, "previous"), _voicing(current, "current")
    if len(before) != len(after):
        raise ValueError("voicings must contain the same number of voices")
    return tuple(now - old for old, now in zip(before, after, strict=True))


def total_voice_motion(previous: Sequence[int], current: Sequence[int]) -> int:
    """Sum absolute pitch displacement; this is a metric, not a quality judgment."""
    return sum(abs(motion) for motion in voice_movements(previous, current))


def maximum_voice_motion(previous: Sequence[int], current: Sequence[int]) -> int:
    """Return the largest absolute displacement made by one voice."""
    return max((abs(motion) for motion in voice_movements(previous, current)), default=0)


def common_pitch_classes(chord_a: Sequence[int], chord_b: Sequence[int]) -> tuple[int, ...]:
    """Return shared pitch classes, independently of octave or voice position."""
    return tuple(sorted(set(chord_pitch_classes(chord_a)) & set(chord_pitch_classes(chord_b))))


def stationary_common_tones(previous: Sequence[int], current: Sequence[int]) -> tuple[int, ...]:
    """Return absolute pitches held by the same fixed voice position."""
    movements = voice_movements(previous, current)
    return tuple(pitch for pitch, motion in zip(previous, movements, strict=True) if motion == 0)


def inversion_candidates(
    root_position_chord: Sequence[int], pitch_range: tuple[int, int] = (48, 84),
    octave_shifts: Sequence[int] = (-12, 0, 12),
) -> tuple[Voicing, ...]:
    """Generate close-position inversions in a small, explicit register search."""
    chord = _voicing(root_position_chord, "root_position_chord")
    if len(chord) != 3:
        raise ValueError("Chapter 11 candidates require a three-note triad")
    low, high = pitch_range
    if low > high or low < 0 or high > 127:
        raise ValueError("pitch_range must be an ascending MIDI range")
    candidates: list[Voicing] = []
    for inversion in range(3):
        shape = invert_chord(chord, inversion)
        for shift in octave_shifts:
            candidate = tuple(pitch + shift for pitch in shape)
            if low <= candidate[0] and candidate[-1] <= high and candidate not in candidates:
                candidates.append(candidate)
    return tuple(candidates)


def choose_nearest_inversion(
    previous_voicing: Sequence[int], root_position_chord: Sequence[int],
    pitch_range: tuple[int, int] = (48, 84),
) -> Voicing:
    """Choose by total motion, maximum motion, mean register, then pitch tuple."""
    previous = _voicing(previous_voicing, "previous_voicing")
    candidates = inversion_candidates(root_position_chord, pitch_range)
    if not candidates:
        raise ValueError("no inversion candidate fits the pitch range")
    if any(len(candidate) != len(previous) for candidate in candidates):
        raise ValueError("previous voicing must contain three voices")
    return min(candidates, key=lambda candidate: (
        total_voice_motion(previous, candidate),
        maximum_voice_motion(previous, candidate),
        sum(candidate), candidate,
    ))


def smooth_progression_voicings(
    root_position_chords: Sequence[Sequence[int]],
    pitch_range: tuple[int, int] = (48, 84),
    starting_voicing: Sequence[int] | None = None,
) -> tuple[Voicing, ...]:
    """Greedily choose each nearest inversion; this is not global optimization."""
    if not root_position_chords:
        raise ValueError("progression must contain at least one chord")
    roots = tuple(_voicing(chord, "root_position_chord") for chord in root_position_chords)
    first = _voicing(starting_voicing, "starting_voicing") if starting_voicing else roots[0]
    if chord_pitch_classes(first) != chord_pitch_classes(roots[0]):
        raise ValueError("starting_voicing must preserve the first chord identity")
    result = [first]
    for chord in roots[1:]:
        result.append(choose_nearest_inversion(result[-1], chord, pitch_range))
    return tuple(result)


def progression_motion(voicings: Sequence[Sequence[int]]) -> tuple[tuple[int, ...], int]:
    """Return each transition score and their progression total."""
    transitions = tuple(total_voice_motion(a, b) for a, b in zip(voicings, voicings[1:]))
    return transitions, sum(transitions)


def extract_voice_lines(voicings: Sequence[Sequence[int]]) -> tuple[tuple[int, ...], ...]:
    """Transpose equal-sized sorted voicings into low/middle/high pitch lines."""
    if not voicings:
        return ()
    checked = tuple(_voicing(voicing, "voicing") for voicing in voicings)
    if any(len(voicing) != len(checked[0]) for voicing in checked):
        raise ValueError("all voicings must contain the same number of voices")
    return tuple(tuple(voicing[index] for voicing in checked) for index in range(len(checked[0])))


def bass_sequence(voicings: Sequence[Sequence[int]]) -> tuple[int, ...]:
    """Return sounding bass pitches, which need not be harmonic roots."""
    return tuple(_voicing(voicing, "voicing")[0] for voicing in voicings)


def within_motion_budget(previous: Sequence[int], current: Sequence[int], maximum: int) -> bool:
    """Report whether every voice moves no farther than ``maximum`` semitones."""
    if isinstance(maximum, bool) or not isinstance(maximum, int):
        raise TypeError("maximum must be an integer")
    if maximum < 0:
        raise ValueError("maximum must not be negative")
    return maximum_voice_motion(previous, current) <= maximum
