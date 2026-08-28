"""Deterministic section content and formal studies for Chapter 17."""

from __future__ import annotations

from dataclasses import replace

from .chapter16 import chapter_16_passages
from .events import NoteEvent
from .forms import FormAssembly, Section, assemble_form, bars_to_beats

BLUES_DEGREES = ("I", "I", "I", "I", "IV", "IV", "I", "I", "V", "IV", "I", "I")
BLUES_CHORDS = {"I": (48, 52, 55), "IV": (53, 57, 60), "V": (55, 59, 62)}


def _extend(section: Section, beats: float) -> Section:
    events = section.events + tuple(
        replace(e, start=e.start + section.duration)
        for e in section.events if e.start < beats - section.duration
    )
    return Section(section.label, events, section.role)


def chapter_17_sections() -> dict[str, Section]:
    """Return concise source sections; labels remain separate from behavior."""
    p = chapter_16_passages()
    a = Section("A", p["A_thin"].events)
    b = Section("B", p["B_thick"].events)
    a_prime = Section("A'", p["A_texture"].events)
    a_double = Section("A''", p["A_double"].events)
    b_prime = Section("B'", tuple(replace(e, velocity=max(1, e.velocity - 8)) for e in b.events))
    c = Section("C", tuple(replace(e, pitch=e.pitch - 5) for e in p["A_rhythm"].events))
    d = Section("D", tuple(replace(e, pitch=e.pitch + 7) for e in p["A_ending"].events))
    verse = Section("Verse", p["A_thin"].events, "verse")
    verse2 = Section("Verse 2", p["A_melodic_bass"].events, "verse")
    chorus = Section("Chorus", p["B_thick"].events, "chorus")
    chorus2 = Section("Chorus 2", p["B_thick"].events + tuple(
        replace(e, pitch=e.pitch + 12, velocity=52) for e in p["A"].events), "chorus")
    return {
        s.label: s for s in (a, b, a_prime, a_double, b_prime, c, d, verse, verse2, chorus, chorus2)
    } | {"B_long": _extend(Section("B_long", b.events), 12),
         "B_capstone": _extend(Section("B_capstone", b.events), 16)}


def blues_section(two_choruses: bool = False) -> Section:
    """Build the simplified C triad, root/fifth bass, and motif timeline."""
    events: list[NoteEvent] = []
    motif = (60, 63, 65, 67)
    cycles = 2 if two_choruses else 1
    for cycle in range(cycles):
        cycle_start = cycle * bars_to_beats(12)
        for bar, degree in enumerate(BLUES_DEGREES):
            start = cycle_start + bars_to_beats(bar)
            chord = BLUES_CHORDS[degree]
            events.extend(NoteEvent(pitch, start, 4, 55) for pitch in chord)
            events.extend((NoteEvent(chord[0] - 12, start, 2, 72), NoteEvent(chord[2] - 12, start + 2, 2, 68)))
            for beat, pitch in enumerate(motif):
                variation = 2 if cycle and beat == 3 else 0
                events.append(NoteEvent(pitch + variation, start + beat, .75, 86))
            events.extend(NoteEvent(31, start + beat / 2, .12, 48 if beat % 2 else 62) for beat in range(8))
    return Section("12-bar blues", tuple(events), "harmonic cycle")


def chapter_17_forms() -> dict[str, FormAssembly]:
    """Assemble every listening comparison from explicit plans."""
    s = chapter_17_sections()
    forms = {
        "binary_form": assemble_form(("A", "B"), s),
        "repeated_binary": assemble_form(("A", "A", "B", "B"), s),
        "varied_binary": assemble_form(("A", "A'", "B", "B'"), s),
        "ternary_form": assemble_form(("A", "B", "A"), s),
        "varied_ternary": assemble_form(("A", "B", "A'"), s),
        "binary_vs_ternary_binary": assemble_form(("A", "B"), s),
        "binary_vs_ternary_ternary": assemble_form(("A", "B", "A"), s),
        "AABA": assemble_form(("A", "A", "B", "A"), s),
        "varied_AABA": assemble_form(("A", "A'", "B", "A''"), s),
        "verse_chorus": assemble_form(("Verse", "Chorus", "Verse", "Chorus"), s),
        "varied_verse_chorus": assemble_form(("Verse", "Chorus", "Verse 2", "Chorus 2"), s),
        "through_composed": assemble_form(("A", "B", "C", "D"), s),
        "return_vs_new_material": assemble_form(("A", "B", "A", "A", "B", "C"), s, (0, 0, 2, 0, 0)),
        "symmetric_sections": assemble_form(("A", "B", "A"), s),
        "asymmetric_sections": assemble_form(("A", "B_long", "A"), s),
        "immediate_transition": assemble_form(("A", "B"), s),
        "gap_transition": assemble_form(("A", "B"), s, (1,)),
        "texture_marked_form": assemble_form(("A", "B", "A"), s),
        "uniform_texture_form": assemble_form(("A", "A'", "A"), s),
        "form_capstone": assemble_form(("A", "A'", "B_capstone", "A''"), s),
    }
    one_blues, two_blues = blues_section(), blues_section(True)
    forms["12_bar_blues"] = assemble_form((one_blues.label,), {one_blues.label: one_blues})
    forms["two_blues_choruses"] = assemble_form((two_blues.label,), {two_blues.label: two_blues})
    return forms
