"""Small Chapter 2 helpers for describing musical time in beats."""

from __future__ import annotations

from collections.abc import Sequence
from pathlib import Path

from .pitch import pitch_to_frequency
from .waveform import SAMPLE_RATE, silence, sine_wave, write_wav


def beats_to_seconds(beats: float, bpm: float) -> float:
    """Convert composition time to rendering time: seconds = beats * 60 / BPM."""
    if beats <= 0:
        raise ValueError("beats must be greater than zero")
    if bpm <= 0:
        raise ValueError("bpm must be greater than zero")
    return beats * 60.0 / bpm


def total_beats(durations: Sequence[float]) -> float:
    """Return the length of positive sequential beat durations."""
    if any(duration <= 0 for duration in durations):
        raise ValueError("durations must be greater than zero")
    return float(sum(durations))


def sequential_starts(durations: Sequence[float]) -> list[float]:
    """Calculate each item start from the durations preceding it."""
    total = 0.0
    starts: list[float] = []
    for duration in durations:
        if duration <= 0:
            raise ValueError("durations must be greater than zero")
        starts.append(total)
        total += duration
    return starts


def total_seconds(durations: Sequence[float], bpm: float) -> float:
    """Return the rendered duration of a sequential beat-duration list."""
    return beats_to_seconds(total_beats(durations), bpm)


def render_beat_sequence(
    pitches: Sequence[int | None],
    durations: Sequence[float],
    bpm: float,
    *,
    sample_rate: int = SAMPLE_RATE,
) -> list[float]:
    """Render aligned pitch/rest and duration lists; ``None`` means a rest."""
    if len(pitches) != len(durations):
        raise ValueError("pitches and durations must have the same length")
    samples: list[float] = []
    for pitch, beats in zip(pitches, durations, strict=True):
        seconds = beats_to_seconds(beats, bpm)
        if pitch is None:
            samples.extend(silence(seconds, sample_rate=sample_rate))
        else:
            samples.extend(
                sine_wave(pitch_to_frequency(pitch), seconds, sample_rate=sample_rate)
            )
    return samples


def write_beat_sequence(
    path: Path,
    pitches: Sequence[int | None],
    durations: Sequence[float],
    bpm: float,
) -> Path:
    """Render a Chapter 2 parallel-list sequence to a WAV file."""
    return write_wav(path, render_beat_sequence(pitches, durations, bpm))
