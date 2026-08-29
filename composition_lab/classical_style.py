"""Deterministic recipes for the Chapter 31 motivic-development study.

This module composes existing event and Chapter 6 transformations.  It is not
a style classifier, an authenticity measure, or a second composition engine.
"""
from __future__ import annotations

from dataclasses import dataclass, replace

from .events import NoteEvent
from .motifs import (augment_motif, diminish_motif, invert_motif,
                     retrograde_motif, sequence_motif)
from .voice_leading import smooth_progression_voicings

SECTION_PLAN = (("Opening", 0.0, 16.0), ("Development", 16.0, 40.0),
                ("Return", 40.0, 56.0), ("Coda", 56.0, 64.0))
HARMONIC_PLAN = ((1, 4, 5, 1), (6, 2, 5, 3, 4, 5), (1, 4, 5, 1), (5, 1))


@dataclass(frozen=True)
class DerivedMaterial:
    label: str
    source_label: str
    transformation: str
    events: tuple[NoteEvent, ...]


@dataclass(frozen=True)
class ProvenanceRecord:
    material_label: str
    source: str
    transformation: str
    section: str
    start_beat: float


@dataclass(frozen=True)
class DevelopmentSection:
    name: str
    start: float
    end: float
    motif_state: str
    harmony: tuple[int, ...]
    register: str
    density: str


@dataclass(frozen=True)
class DevelopmentStudy:
    title: str
    tonic: int
    mode: str
    bpm: float
    motif: tuple[NoteEvent, ...]
    materials: tuple[DerivedMaterial, ...]
    sections: tuple[DevelopmentSection, ...]
    provenance: tuple[ProvenanceRecord, ...]
    events: tuple[NoteEvent, ...]
    layers: tuple[str, ...]


def source_motif() -> tuple[NoteEvent, ...]:
    """An original four-note, two-beat C-major motif."""
    return (NoteEvent(60, 0, .5, 92), NoteEvent(62, .5, .5, 88),
            NoteEvent(67, 1, .5, 94), NoteEvent(64, 1.5, .5, 86))


def fragment(motif: tuple[NoteEvent, ...], size: int = 2) -> tuple[NoteEvent, ...]:
    """Take an explicit leading subset and normalize no other property."""
    if not 1 <= size <= len(motif):
        raise ValueError("fragment size must select at least one source event")
    return motif[:size]


def adapt_for_vi(motif: tuple[NoteEvent, ...]) -> tuple[NoteEvent, ...]:
    """Change only G4 to A4 for the controlled vi-harmony comparison."""
    return tuple(replace(event, pitch=69) if index == 2 else event
                 for index, event in enumerate(motif))


def developed_phrase(motif: tuple[NoteEvent, ...], expanded: bool = False) -> tuple[NoteEvent, ...]:
    """Build an 8-beat phrase, or add sequence/fragment/cadence to reach 12."""
    # opening 0–2, sequence 2–4, four attacks from the fragment 4–6, close 6–8
    result = list(motif)
    result += [replace(e, start=e.start + 2) for e in sequence_motif(motif, (2,))]
    cell = tuple(diminish_motif(fragment(motif)))
    result += [replace(e, start=e.start + 4 + n) for n in range(2) for e in cell]
    result += [NoteEvent(62, 6, 1, 78), NoteEvent(60, 7, 1, 82)]
    if expanded:
        # Added beats 8–10: fragment repetition; 10–12: V–I cadential extension.
        result += [replace(e, start=e.start + 8) for n in range(2)
                   for e in cell for _ in (n,) ]
        # Correct the second cell's placement without hiding the explicit added beats.
        result[-2:] = [replace(e, start=e.start + 1) for e in result[-2:]]
        result += [NoteEvent(67, 10, 1, 76), NoteEvent(60, 11, 1, 82)]
    return tuple(sorted(result, key=lambda e: e.start))


def _place(events: tuple[NoteEvent, ...] | list[NoteEvent], start: float) -> tuple[NoteEvent, ...]:
    return tuple(replace(e, start=e.start + start) for e in events)


def _triad(degree: int, octave: int = 48) -> tuple[int, int, int]:
    roots = (0, 2, 4, 5, 7, 9, 11); qualities = ((0, 4, 7), (0, 3, 7), (0, 3, 7),
        (0, 4, 7), (0, 4, 7), (0, 3, 7), (0, 3, 6))
    root = octave + roots[degree - 1]
    return tuple(root + interval for interval in qualities[degree - 1])


def build_development_study(bpm: float = 96, tonic: int = 60) -> DevelopmentStudy:
    """Build the authored 64-beat Opening–Development–Return–Coda form."""
    motif = tuple(replace(e, pitch=e.pitch + tonic - 60) for e in source_motif())
    frag = fragment(motif); inv = tuple(invert_motif(motif, tonic))
    materials = (DerivedMaterial("A", "source", "original", motif),
        DerivedMaterial("A1", "A", "exact semitone sequence +2/+4", tuple(sequence_motif(motif, (0, 2, 4)))),
        DerivedMaterial("A2", "A", "first-two-note fragment", frag),
        DerivedMaterial("A3", "A", f"pitch inversion around {tonic}", inv),
        DerivedMaterial("A4", "A", "augmentation ×2", tuple(augment_motif(motif))),
        DerivedMaterial("A5", "A2", "diminution ×0.5", tuple(diminish_motif(frag))),
        DerivedMaterial("A6", "A", "temporal retrograde", tuple(retrograde_motif(motif))))
    appearances = (("A", "Opening", 0, motif, "literal"), ("A", "Opening", 2, motif, "literal"),
        ("A1", "Opening", 4, tuple(sequence_motif(motif, (0, 2, 4))), "sequence"),
        ("A", "Opening", 10, motif, "literal"), ("A2", "Opening", 12, frag, "fragment repeated"),
        ("A2", "Development", 16, tuple(sequence_motif(frag, (0, 2, 4, 5))), "fragment sequence"),
        ("A3", "Development", 20, inv, "inversion"),
        ("A3", "Development", 22, tuple(sequence_motif(inv, (2, 4))), "inverted sequence"),
        ("A5", "Development", 26, tuple(diminish_motif(frag)), "diminution"),
        ("A5", "Development", 27, tuple(sequence_motif(diminish_motif(frag), (0, 2, 4, 5))), "diminished sequence"),
        ("A6", "Development", 31, tuple(retrograde_motif(motif)), "retrograde"),
        ("A2", "Development", 33, tuple(sequence_motif(frag, (7, 5, 4, 2, 0))), "descending fragment sequence"),
        ("A", "Return", 40, motif, "literal return"), ("A", "Return", 42, motif, "literal"),
        ("A1", "Return", 44, tuple(sequence_motif(motif, (0, 2, 4))), "sequence"),
        ("A", "Return", 50, motif, "literal"), ("A2", "Return", 52, frag, "closing fragment"),
        ("A4", "Coda", 56, tuple(augment_motif(frag)), "augmented fragment"),
        ("A2", "Coda", 60, frag, "cadential fragment"))
    melody: list[NoteEvent] = []; provenance = []
    for label, section, start, events, transformation in appearances:
        melody.extend(_place(events, start)); provenance.append(ProvenanceRecord(label, "A" if label != "A" else "source", transformation, section, start))
    # Explicit tonic arrivals fill closing space and make every section exactly bounded.
    melody += [NoteEvent(tonic, 14, 2, 80), NoteEvent(tonic + 7, 38, 1, 76),
               NoteEvent(tonic, 39, 1, 82), NoteEvent(tonic, 54, 2, 80),
               NoteEvent(tonic + 7, 62, 1, 74), NoteEvent(tonic, 63, 1, 84)]
    provenance += [ProvenanceRecord("cadence", "A", "V–I cadential extension", s, b)
                   for s, b in (("Opening", 14), ("Development", 38), ("Return", 54), ("Coda", 62))]
    harmony: list[NoteEvent] = []; bass: list[NoteEvent] = []
    harmonic_slots = []
    for (name, start, end), degrees in zip(SECTION_PLAN, HARMONIC_PLAN, strict=True):
        span = (end - start) / len(degrees)
        for i, degree in enumerate(degrees):
            beat = start + i * span
            harmonic_slots.append((beat, span, degree))
    roots = tuple(_triad(degree) for _, _, degree in harmonic_slots)
    voice_led = smooth_progression_voicings(roots, (48, 72))
    for (beat, span, degree), voicing in zip(harmonic_slots, voice_led, strict=True):
        harmony.extend(NoteEvent(p + tonic - 60, beat, span, 48) for p in voicing)
        bass.append(NoteEvent(_triad(degree, 36)[0] + tonic - 60, beat, span, 58))
    tagged = [(e, "motif") for e in melody] + [(e, "harmony") for e in harmony] + [(e, "bass") for e in bass]
    tagged = sorted(enumerate(tagged), key=lambda x: (x[1][0].start, x[0]))
    sections = tuple(DevelopmentSection(name, start, end,
        "sequence, fragment, inversion, diminution" if name == "Development" else "original motif" if name != "Coda" else "augmented/cadential fragment",
        HARMONIC_PLAN[i], "broadened" if name == "Development" else "opening mid register",
        "more attacks/shorter values" if name == "Development" else "reduced")
        for i, (name, start, end) in enumerate(SECTION_PLAN))
    return DevelopmentStudy("Chapter 31 Motivic Development Study", tonic, "major", bpm, motif,
        materials, sections, tuple(provenance), tuple(x[1][0] for x in tagged), tuple(x[1][1] for x in tagged))
