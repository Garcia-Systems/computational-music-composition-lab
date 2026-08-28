"""Deterministic musical material for Chapter 16's listening laboratory."""

from __future__ import annotations

from dataclasses import replace

from .events import NoteEvent
from .passages import Passage, append_passages, repeat_passage


def _line(pitches: tuple[int, ...], starts: tuple[float, ...], durations: tuple[float, ...], velocity: int = 96) -> tuple[NoteEvent, ...]:
    return tuple(NoteEvent(p, s, d, velocity) for p, s, d in zip(pitches, starts, durations, strict=True))


def chapter_16_passages() -> dict[str, Passage]:
    """Build eight-beat A variations and a deliberately contrasting B."""
    starts = (0, 1, 2, 3, 4, 5, 6, 7)
    durations = (1,) * 8
    a = _line((60, 62, 64, 67, 64, 62, 60, 60), starts, durations)
    ending = _line((60, 62, 64, 67, 64, 65, 62, 60), starts, durations)
    pitch = _line((60, 62, 65, 69, 64, 62, 60, 60), starts, durations)
    rhythm = _line((60, 62, 64, 67, 64, 62, 60, 60),
                   (0, .5, 1, 2, 4, 4.5, 5, 6), (.5, .5, 1, 2, .5, .5, 1, 2))
    register = tuple(replace(event, pitch=event.pitch + 12) for event in a)
    b = _line((67, 74, 71, 79, 76, 72, 77, 67),
              (0, .5, 1, 1.5, 2, 3, 4, 6), (.5, .5, .5, .5, 1, 1, 2, 2), 100)
    bass = tuple(NoteEvent(p, s, 2, 76) for p, s in zip((36, 41, 43, 36), (0, 2, 4, 6), strict=True))
    melodic_bass = _line((36, 40, 41, 42, 43, 38, 36, 36), starts, durations, 76)
    harmony = tuple(NoteEvent(p, s, 2, 62) for s, chord in zip((0, 2, 4, 6),
                    ((48, 52, 55), (53, 57, 60), (55, 59, 62), (48, 52, 55)), strict=True) for p in chord)
    harmony_ii = tuple(NoteEvent(p, s, 2, 62) for s, chord in zip((0, 2, 4, 6),
                    ((48, 52, 55), (50, 53, 57), (55, 59, 62), (48, 52, 55)), strict=True) for p in chord)
    accompaniment = tuple(NoteEvent(p, s + offset, .5, 58) for s, chord in zip((0, 2, 4, 6),
                    ((48, 52, 55), (53, 57, 60), (55, 59, 62), (48, 52, 55)), strict=True)
                    for offset, p in zip((0, .5, 1, 1.5), (chord[0], chord[1], chord[2], chord[1]), strict=True))
    groove = tuple(NoteEvent(31, s, .2, 55 if s % 2 else 72) for s in range(8))
    offbeat = groove + (NoteEvent(31, 5.5, .2, 64),)
    return {
        "A": Passage("A", a), "A_ending": Passage("A'", ending),
        "A_pitch": Passage("A_pitch", pitch), "A_rhythm": Passage("A_rhythm", rhythm),
        "A_register": Passage("A_register", register), "B": Passage("B", b),
        "A_thin": Passage("A thin", a + bass),
        "A_texture": Passage("A texture", a + bass + accompaniment + groove),
        "A_harmony": Passage("A harmony", a + harmony + bass),
        "A_harmony_ii": Passage("A harmony variation", a + harmony_ii + bass),
        "A_root_bass": Passage("A root bass", a + harmony + bass + groove),
        "A_melodic_bass": Passage("A melodic bass", a + harmony + melodic_bass + groove),
        "A_groove": Passage("A groove", a + harmony + bass + groove),
        "A_offbeat": Passage("A groove variation", a + harmony + bass + offbeat),
        "B_thick": Passage("B thick", b + harmony_ii + melodic_bass + accompaniment + offbeat),
        "A_double": Passage("A''", ending + bass + accompaniment + groove),
    }


def chapter_16_scores() -> dict[str, tuple[NoteEvent, ...]]:
    """Return every named listening experiment as transparent passage assembly."""
    p = chapter_16_passages()
    pair = lambda x, y: append_passages(p[x], p[y])
    return {
        "literal_repetition": repeat_passage(p["A"], 2),
        "A_A_prime_ending": pair("A", "A_ending"), "pitch_variation": pair("A", "A_pitch"),
        "rhythm_variation": pair("A", "A_rhythm"), "register_variation": pair("A", "A_register"),
        "texture_variation": pair("A_thin", "A_texture"), "harmony_variation": pair("A_harmony", "A_harmony_ii"),
        "bass_variation": pair("A_root_bass", "A_melodic_bass"), "groove_variation": pair("A_groove", "A_offbeat"),
        "A_B_contrast": pair("A_thin", "B_thick"), "A_B_A_return": append_passages(p["A_thin"], p["B_thick"], p["A_thin"]),
        "literal_return": append_passages(p["A_thin"], p["B_thick"], p["A_thin"]),
        "varied_return": append_passages(p["A_thin"], p["B_thick"], p["A_double"]),
        "three_repeats_then_variation": append_passages(p["A"], p["A"], p["A"], p["A_ending"]),
        "early_variation": append_passages(p["A"], p["A_ending"], p["A"], p["A"]),
        "late_variation": append_passages(p["A"], p["A"], p["A"], p["A_ending"]),
        "contrast_with_motif_link": pair("A", "B"),
        "texture_continuity": pair("A_thin", "B"), "texture_contrast": pair("A_thin", "B_thick"),
        "return_with_new_texture": append_passages(p["A_thin"], p["B_thick"], p["A_texture"]),
        "A_A_prime_study": append_passages(p["A_thin"], p["A_double"]),
        "A_B_study": pair("A_thin", "B_thick"), "A_B_A_study": append_passages(p["A_thin"], p["B_thick"], p["A_thin"]),
        "A_B_A_prime_study": append_passages(p["A_thin"], p["B_thick"], p["A_double"]),
        "development_capstone": append_passages(p["A_thin"], p["A_rhythm"], p["B_thick"], p["A_double"]),
    }
