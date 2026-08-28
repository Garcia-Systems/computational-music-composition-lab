"""Transparent pitch arithmetic for Chapter 1.

Pitch numbers follow the familiar MIDI-style 0--127 range, but this module
does not read or write MIDI: integers are simply convenient musical data.
"""

from __future__ import annotations

import re

PITCH_CLASS_NAMES = (
    "C", "C#", "D", "D#", "E", "F", "F#", "G", "G#", "A", "A#", "B",
)
MIN_PITCH = 0
MAX_PITCH = 127
_NAME_PATTERN = re.compile(r"^(C#?|D#?|E|F#?|G#?|A#?|B)(-?\d+)$")


def _validate_pitch(pitch: int) -> None:
    if isinstance(pitch, bool) or not isinstance(pitch, int):
        raise TypeError("pitch must be an integer")
    if not MIN_PITCH <= pitch <= MAX_PITCH:
        raise ValueError("pitch must be between 0 and 127")


def pitch_to_frequency(pitch: int) -> float:
    """Convert a pitch number to hertz using A4 = pitch 69 = 440 Hz."""
    _validate_pitch(pitch)
    return 440.0 * 2 ** ((pitch - 69) / 12)


def pitch_to_name(pitch: int) -> str:
    """Return the canonical sharp-based name of a pitch number."""
    _validate_pitch(pitch)
    pitch_class = PITCH_CLASS_NAMES[pitch % 12]
    octave = pitch // 12 - 1
    return f"{pitch_class}{octave}"


def name_to_pitch(name: str) -> int:
    """Convert a canonical name such as ``C4`` or ``F#5`` to a pitch number."""
    if not isinstance(name, str):
        raise TypeError("name must be a string")
    match = _NAME_PATTERN.fullmatch(name)
    if match is None:
        raise ValueError(
            "name must use an uppercase note, optional #, and octave (for example C#4)"
        )
    pitch_class_name, octave_text = match.groups()
    pitch = (int(octave_text) + 1) * 12 + PITCH_CLASS_NAMES.index(pitch_class_name)
    _validate_pitch(pitch)
    return pitch


def transpose_pitch(pitch: int, semitones: int) -> int:
    """Move ``pitch`` by an integer number of semitones."""
    _validate_pitch(pitch)
    if isinstance(semitones, bool) or not isinstance(semitones, int):
        raise TypeError("semitones must be an integer")
    transposed = pitch + semitones
    _validate_pitch(transposed)
    return transposed


def interval_semitones(first: int, second: int) -> int:
    """Return the signed semitone distance from ``first`` to ``second``."""
    _validate_pitch(first)
    _validate_pitch(second)
    return second - first
