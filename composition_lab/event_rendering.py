"""Translate beat-based NoteEvent composition data into audio samples."""

from __future__ import annotations

from collections.abc import Sequence

from .events import NoteEvent, composition_duration
from .pitch import pitch_to_frequency
from .waveform import DEFAULT_AMPLITUDE, SAMPLE_RATE, sine_wave


def render_events(
    events: Sequence[NoteEvent], bpm: float, *, sample_rate: int = SAMPLE_RATE
) -> list[float]:
    """Mix events on a shared timeline, normalizing only when mixing clips."""
    if bpm <= 0:
        raise ValueError("bpm must be greater than zero")
    if sample_rate <= 0:
        raise ValueError("sample_rate must be greater than zero")

    seconds_per_beat = 60.0 / bpm
    sample_count = round(composition_duration(events) * seconds_per_beat * sample_rate)
    mixed = [0.0] * sample_count
    for event in events:
        start_sample = round(event.start * seconds_per_beat * sample_rate)
        duration_seconds = event.duration * seconds_per_beat
        # Velocity is performance intensity, not universal loudness.  This
        # simple synthesizer maps it linearly onto its safe single-note level.
        amplitude = DEFAULT_AMPLITUDE * event.velocity / 127
        note = sine_wave(
            pitch_to_frequency(event.pitch), duration_seconds,
            sample_rate=sample_rate, amplitude=amplitude,
        )
        for offset, sample in enumerate(note):
            if start_sample + offset < len(mixed):
                mixed[start_sample + offset] += sample

    peak = max((abs(sample) for sample in mixed), default=0.0)
    if peak > 1.0:
        mixed = [sample / peak for sample in mixed]
    return mixed
