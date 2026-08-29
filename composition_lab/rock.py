"""Small, objective recipes used by the Chapter 30 rock style lab.

These functions are arrangements of the general event, motif, harmony, and
groove tools.  They deliberately do not attempt to identify or score a genre.
"""
from __future__ import annotations

from dataclasses import replace

from .events import NoteEvent
from .motifs import repeat_motif, transpose_motif


VERSE_DEGREES = (1, 4, 6, 5)
CHORUS_DEGREES = (1, 5, 6, 4)
BRIDGE_DEGREES = (6, 4, 1, 5)


def power_chord(root: int, double_root: bool = True) -> tuple[int, ...]:
    """Return a root/fifth sonority, optionally with its octave-doubled root."""
    pitches = (root, root + 7, root + 12) if double_root else (root, root + 7)
    if not all(0 <= pitch <= 127 for pitch in pitches):
        raise ValueError("power-chord pitches must remain between 0 and 127")
    return pitches


def opening_riff() -> tuple[NoteEvent, ...]:
    """Return the original one-bar E-centred motif used as a structural riff."""
    # Ends exactly at beat four. Gaps after 0.35, 1.35, and 3.35 are rests.
    return (
        NoteEvent(40, 0.0, .35, 88), NoteEvent(40, .5, .35, 82),
        NoteEvent(43, 1.0, .35, 86), NoteEvent(45, 1.5, .75, 90),
        NoteEvent(40, 2.5, .35, 88), NoteEvent(47, 3.0, .35, 92),
        NoteEvent(50, 3.5, .5, 94),
    )


def ending_variation(riff: tuple[NoteEvent, ...], semitones: int = -3) -> tuple[NoteEvent, ...]:
    """Change only the last pitch of a riff (A')."""
    return riff[:-1] + (replace(riff[-1], pitch=riff[-1].pitch + semitones),)


def rhythmic_variation(riff: tuple[NoteEvent, ...]) -> tuple[NoteEvent, ...]:
    """Lengthen one attack and shorten another without changing the bar span."""
    return tuple(replace(e, duration=.6 if i == 2 else (.5 if i == 3 else e.duration))
                 for i, e in enumerate(riff))


def syncopated_riff(riff: tuple[NoteEvent, ...]) -> tuple[NoteEvent, ...]:
    """Move selected attacks one eighth-note later, preserving pitches."""
    return tuple(replace(e, start=e.start + .5) if i in (2, 5) else e
                 for i, e in enumerate(riff))


def riff_variations(riff: tuple[NoteEvent, ...]) -> dict[str, tuple[NoteEvent, ...]]:
    """Expose five intentionally small transformations, not a generator."""
    return {"ending": ending_variation(riff), "rhythm": rhythmic_variation(riff),
            "register": tuple(transpose_motif(riff, 12)),
            "transposition_E_to_A": tuple(transpose_motif(riff, 5)),
            "fragment": tuple(e for e in riff if e.start < 2)}


def four_repetitions(riff: tuple[NoteEvent, ...], varied_ending: bool = False) -> tuple[NoteEvent, ...]:
    """Build A A A A or A A A A' at exact four-beat offsets."""
    result = tuple(repeat_motif(riff, 3))
    final = ending_variation(riff) if varied_ending else riff
    return result + tuple(replace(e, start=e.start + 12) for e in final)


def backbeat_bar() -> dict[str, tuple[NoteEvent, ...]]:
    """A pitched proxy model: kick 1/3, snare 2/4, high eighth-note pulse."""
    return {
        "kick": tuple(NoteEvent(28, beat, .18, 88) for beat in (0.0, 2.0)),
        "snare": tuple(NoteEvent(40, beat, .18, 92) for beat in (1.0, 3.0)),
        "high_pulse": tuple(NoteEvent(76, beat / 2, .12, 55) for beat in range(8)),
    }


def bass_lines(riff: tuple[NoteEvent, ...], roots: tuple[int, ...] = (28, 33, 37, 35)) -> dict[str, tuple[NoteEvent, ...]]:
    """Three objectively distinct four-bar bass strategies."""
    doubling = tuple(replace(e, pitch=e.pitch - 12) for e in repeat_motif(riff, 4))
    root_following = tuple(NoteEvent(root, bar * 4, 3.8, 76) for bar, root in enumerate(roots))
    independent_pitches = (28, 35, 33, 36, 37, 35, 32, 35)
    independent = tuple(NoteEvent(p, i * 2, 1.5, 74) for i, p in enumerate(independent_pitches))
    return {"riff-doubling": doubling, "root-following": root_following,
            "independent": independent}


def riff_over_roots(riff: tuple[NoteEvent, ...], root_offsets: tuple[int, ...],
                    *, adapt: bool) -> tuple[NoteEvent, ...]:
    """Repeat a riff fixed, or transpose each copy with the current chord root.

    This narrow helper makes the contextual Chapter 12 comparison inspectable;
    it does not decide which treatment is preferable.
    """
    result = []
    for bar, offset in enumerate(root_offsets):
        source = transpose_motif(riff, offset) if adapt else riff
        result.extend(replace(e, start=e.start + bar * 4) for e in source)
    return tuple(result)
