# Chapter 4 — Scales, Keys, and Tonality

> How can a computer represent a tonal system so that pitches are chosen
> according to musical relationships rather than arbitrary numbers?

Chapter 3 can represent this perfectly well:

```python
[
    NoteEvent(60, 0.0, 1.0),
    NoteEvent(62, 1.0, 1.0),
    NoteEvent(63, 2.0, 1.0),
    NoteEvent(67, 3.0, 1.0),
]
```

Yet no field in `NoteEvent` tells us whether those pitches share a tonal
system. If the piece is in C major, which pitch classes are expected? The
diatonic collection is C D E F G A B; C#, D#, F#, G#, and A# are chromatic in
relation to it. Chromatic does not mean *wrong*. **A key establishes a tonal
reference system. Notes inside and outside the scale have different
relationships to that system.**

Our new progression is:

```text
PITCH → PITCH CLASS → SCALE → KEY → SCALE DEGREE
```

## Pitch identity without register

Chapter 1 assigned C=0, C#=1, D=2, D#=3, E=4, F=5, F#=6, G=7, G#=8,
A=9, A#=10, and B=11. Remainder arithmetic removes the octave:

```text
60 % 12 = 0 → C
72 % 12 = 0 → C
84 % 12 = 0 → C
```

That makes it possible to test membership across registers. C3, E4, G5, and
B3 can all relate to C major. A key is not restricted to one octave; an
ascending octave scale is only a convenient presentation of its structure.

## A scale is an interval pattern

`composition_lab/scales.py` exposes the data directly:

```python
MAJOR = (0, 2, 4, 5, 7, 9, 11, 12)
NATURAL_MINOR = (0, 2, 3, 5, 7, 8, 10, 12)
```

The offsets are semitone distances from a tonic, not fixed pitches. For C4:

```text
60 + 0  = 60 C4       60 + 7  = 67 G4
60 + 2  = 62 D4       60 + 9  = 69 A4
60 + 4  = 64 E4       60 + 11 = 71 B4
60 + 5  = 65 F4       60 + 12 = 72 C5
```

The major-scale steps are **W W H W W W H**, where W is two semitones and H
is one: C→D=2, D→E=2, E→F=1, F→G=2, G→A=2, A→B=2, B→C=1. Natural minor is
**W H W W H W W**. This structural definition is the important idea; this
chapter is not an exhaustive scale catalogue.

The construction remains readable:

```python
scale_pitch = tonic + interval
```

`build_scale`, `major_scale`, and `natural_minor_scale` apply exactly that
operation.

## Scale degree: a pitch's tonal role

Musicians label the ordered notes 1 through 8. In C major, 1=C, 2=D, 3=E,
4=F, 5=G, 6=A, 7=B, and 8=C one octave higher. The public helper
`scale_degree` follows this musical 1-based convention and rejects values
outside 1–8 rather than silently wrapping them.

This lets a compositional idea exist before its absolute pitches:

```text
IDEA       1  2  3  5  3  2  1
             ↓ C major
PITCHES   60 62 64 67 64 62 60
             ↓ F major
PITCHES   65 67 69 72 69 67 65
```

The key changes; the degree relationships survive. This resembles Chapter 1's
transposition experiment, now expressed in tonal roles.

`events_from_degrees` makes the complete path visible:

```text
degree → pitch from tonic + scale pattern → NoteEvent on the timeline
```

It accepts one duration per degree and accumulates sequential starts. It is a
focused bridge to Chapter 3, not a melody-generation framework.

## Membership and tonic

`pitch_in_scale` compares pitch classes. In C major, 60 (C4) and 72 (C5)
return `True`; 61 (C#4) and 66 (F#4) return `False`. Here `False` means outside
this diatonic reference collection, never prohibited or artistically invalid.

The tonic is degree 1 and acts as the tonal center, not merely tuple item zero.
Compare `1 2 3 2 1` with `1 2 3 2 7`. Which ending feels more settled? This is
an introductory listening question, not a universal claim about every listener
or musical style.

## Run the listening laboratory

```bash
python -m composition_lab chapter-04
```

The command prints a C-major scale inspector with degree, absolute pitch, name,
and frequency, then creates controlled comparisons at 120 BPM with the same
sine waveform, velocity, register, and half-beat rhythm:

1. **C major / C natural minor** — tonic fixed, interval pattern changed.
   What changes when the tonic stays the same?
2. **C / D / F major scales** — structure fixed, tonic changed. What remains
   recognizable as absolute pitch moves?
3. **Degree melody in C / F major** — the same `1 2 3 5 3 2 1` idea resolved
   through two keys.
4. **Diatonic / chromatic** — the E in that phrase becomes E-flat while every
   other condition stays fixed. Listen for tension, surprise, instability, or
   color rather than “better” or “worse.”
5. **Tonic / degree-7 ending** — compare `1 2 3 2 1` and `1 2 3 2 7`.

## Reader experiments

- **A — Change the tonic.** Render the degree melody in C, D, E, F, and G.
  Notice what changes and what remains structurally identical.
- **B — Major versus minor.** Keep tonic and degree numbers fixed; replace
  `MAJOR` with `NATURAL_MINOR` and compare the resulting pitches.
- **C — Change one degree.** Compare `1 2 3 5 3 2 1` with
  `1 2 4 5 3 2 1`.
- **D — Add a chromatic pitch.** Move one scale pitch by a semitone. Does it
  sound outside the system? Does it create useful tension?
- **E — Ending degree.** End the same phrase on 1, 3, 5, and 7 and compare its
  sense of closure.

## Boundaries of this model

We are using 12-tone equal temperament, major, natural minor, and basic tonal
relationships because they make the computation easy to inspect. They are a
useful model, not a complete theory of music. Other scales, tunings, modal and
chromatic approaches, and non-Western pitch organizations deserve their own
contexts; none is implemented here.

Nor does this chapter implement chords, Roman-numeral harmony, voice leading,
MIDI, generation, or melodic-motion analysis. Chapter 5 will ask how one pitch
moves to the next. For now our question remains: **which tonal relationship
does this pitch occupy?**

## Bridge forward

A scale limits available pitches; it does not describe the shape made by moving among them. Chapter 5 measures interval, direction, contour, and range.
