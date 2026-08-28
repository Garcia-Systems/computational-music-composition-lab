"""Small, transparent sine-wave and WAV-writing helpers.

Samples are represented as floats while composing, then converted to signed
16-bit PCM only at the edge where a WAV file is written.
"""

from __future__ import annotations

from collections.abc import Iterable, Sequence
from math import pi, sin
from pathlib import Path
import struct
import wave

SAMPLE_RATE = 44_100
DEFAULT_AMPLITUDE = 0.35
PCM_MAX = 32_767


def sine_wave(
    frequency: float,
    duration: float,
    *,
    sample_rate: int = SAMPLE_RATE,
    amplitude: float = DEFAULT_AMPLITUDE,
    fade_duration: float = 0.01,
) -> list[float]:
    """Return samples for one faded sine-wave note.

    The short linear attack and release bring the waveform toward zero at note
    boundaries, preventing the abrupt jumps that listeners hear as clicks.
    """
    if frequency <= 0:
        raise ValueError("frequency must be greater than zero")
    if duration <= 0:
        raise ValueError("duration must be greater than zero")
    if sample_rate <= 0:
        raise ValueError("sample_rate must be greater than zero")
    if not 0 <= amplitude <= 1:
        raise ValueError("amplitude must be between 0 and 1")
    if fade_duration < 0:
        raise ValueError("fade_duration cannot be negative")

    sample_count = round(duration * sample_rate)
    if sample_count < 1:
        raise ValueError("duration is too short to create a sample")
    fade_samples = min(round(fade_duration * sample_rate), sample_count // 2)

    samples: list[float] = []
    for index in range(sample_count):
        time = index / sample_rate
        envelope = 1.0
        if fade_samples:
            if index < fade_samples:
                envelope = index / fade_samples
            elif index >= sample_count - fade_samples:
                envelope = (sample_count - 1 - index) / fade_samples
        samples.append(amplitude * envelope * sin(2 * pi * frequency * time))
    return samples


def render_notes(
    notes: Iterable[tuple[float, float]], *, sample_rate: int = SAMPLE_RATE
) -> list[float]:
    """Render ``(frequency, duration)`` pairs consecutively."""
    samples: list[float] = []
    for frequency, duration in notes:
        samples.extend(sine_wave(frequency, duration, sample_rate=sample_rate))
    return samples


def write_wav(
    path: Path, samples: Sequence[float], *, sample_rate: int = SAMPLE_RATE
) -> Path:
    """Write mono floating-point samples as a standard 16-bit PCM WAV file."""
    if sample_rate <= 0:
        raise ValueError("sample_rate must be greater than zero")
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    pcm_values = [round(max(-1.0, min(1.0, sample)) * PCM_MAX) for sample in samples]
    pcm_bytes = struct.pack(f"<{len(pcm_values)}h", *pcm_values)

    with wave.open(str(path), "wb") as wav_file:
        wav_file.setnchannels(1)
        wav_file.setsampwidth(2)
        wav_file.setframerate(sample_rate)
        wav_file.writeframes(pcm_bytes)
    return path
