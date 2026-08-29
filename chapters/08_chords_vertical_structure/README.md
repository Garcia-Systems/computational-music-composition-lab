# Chapter 8 — Chords and Vertical Structure

> How can we organize several simultaneous pitches into recognizable harmonic structures?

Chapter 3 made overlap mechanically possible. Here simultaneity gains musical
organization: **a chord is a group of pitches organized to function as one
harmonic sonority**. Not every collection sounding at once must be heard as a
chord; this laboratory concentrates on familiar tertian triads in 12-tone equal
temperament.

## Horizontal and vertical

Melody unfolds horizontally: `C → E → G`. Harmony can present the same material
vertically, with C, E, and G heard together. Sequential and simultaneous notes
therefore can carry different meaning even when their pitch collection matches.
A triad names three relationships above a root:

```text
              ROOT  THIRD  FIFTH
major          0      4      7
minor          0      3      7
diminished     0      3      6
```

These are patterns, not chords tied to C. `60 + (0, 4, 7)` gives C4–E4–G4;
`65 + (0, 4, 7)` gives F4–A4–C5. Thus **structure + reference pitch = absolute
pitches**. `build_chord` keeps that addition visible, while `chord_events`
gives every tone the same start and duration.

Run the complete experiment:

```bash
python -m composition_lab chapter-08
```

## Quality: one semitone at a time

The first files hold root, register, duration, velocity, tempo, and sine waveform
constant. C major `(60, 64, 67)` becomes C minor `(60, 63, 67)` by lowering only
the third. C minor becomes diminished `(60, 63, 66)` by lowering only the fifth.
How much can one semitone change the character? Compare stability or tension,
without assuming that every listener must attach the same emotion.

## Root position, bass, and inversion

In root position the root is also the bass (the lowest sounding pitch):

```text
root position       first inversion     second inversion
C4 E4 G4            E4 G4 C5            G4 C5 E5
60 64 67            64 67 72            67 72 76
```

The **root** defines the chord structurally; the **bass** is whichever pitch is
lowest now. First-inversion C major still has root C but bass E. Each inversion
moves the lowest tone up an octave. Its pitch classes remain C, E, and G, while
bass, register, and spacing make it sound different.

This is not Chapter 6's melodic inversion. **Melodic inversion** reverses interval
direction around an axis. **Chord inversion** reorders chord tones so another
member is in the bass. The shared word does not make them the same operation.

## Voicing, spacing, and doubling

Closed C major is C4–E4–G4. An open example, C4–G4–E5, keeps chord identity while
changing spacing. Identity and voicing are related but not identical. Likewise,
C4–E4–G4–C5 remains a C-major sonority: C has simply been doubled. This chapter
does not generalize these examples into a voicing or orchestration engine.

## Block and broken chords

A block chord starts all tones together. An **arpeggio** presents chord tones
sequentially. The files compare the same C–E–G collection in both forms. When
does a harmonic structure begin to behave like a melodic pattern? Duration and
velocity are separate layers too: changing either affects temporal role or
performance intensity without changing the chord's interval pattern.

## Triads from a scale

Stack alternate scale degrees—root, third, fifth. In C major, degrees 1–3–5 give
C–E–G, while 2–4–6 give D–F–A. When a selected degree wraps past degree 7, it is
raised by an octave so every triad remains ascending. Degree 7 is therefore
B4–D5–F5, not B4–D4–F4.

```text
Reference  Degree  Notes   Quality
I          1       C E G   major
ii         2       D F A   minor
iii        3       E G B   minor
IV         4       F A C   major
V          5       G B D   major
vi         6       A C E   minor
vii°       7       B D F   diminished
```

Roman numerals are labels here, not progression or harmonic-function analysis.
The important discovery is that chord quality emerges from scale structure.
Listen to I, IV, and V in the inventory: if all belong to one scale, why are
their sonorities distinct? The final C–F–G–C file is only a **harmonic sequence
preview**, motivating the next chapter rather than teaching progression theory.

## Reader experiments

1. **Change only the third.** Compare C–E–G with C–E♭–G, then choose a new root.
2. **Change only the fifth.** Compare C–E♭–G with C–E♭–G♭.
3. **Invert.** Hear root, first, and second inversion. Which sounds most grounded
   in this deliberately simple context?
4. **Open the voicing.** Raise one upper tone an octave but preserve pitch classes.
5. **Arpeggiate.** Try low–middle–high, then high–middle–low.
6. **Change the tonic.** Construct all seven triads in another major key.
7. **Extension:** apply the same alternate-degree procedure to natural minor.

Harmony also includes seventh and extended chords, suspensions, quartal harmony,
clusters, modal and chromatic harmony, non-tertian structures, and other tuning
systems. They are acknowledged, not implemented. General progression objects,
Roman-numeral progression analysis, harmonic function, transposable progression
patterns, and voice-leading optimization remain deliberately outside Chapter 8.

## Listening artifacts

- `chapter_08_c_major.wav`, `chapter_08_c_minor.wav`, `chapter_08_c_diminished.wav`
- `chapter_08_c_major_root.wav`, `chapter_08_c_major_first_inversion.wav`,
  `chapter_08_c_major_second_inversion.wav`
- `chapter_08_closed_voicing.wav`, `chapter_08_open_voicing.wav`
- `chapter_08_block_chord.wav`, `chapter_08_broken_chord.wav`
- `chapter_08_c_major_diatonic_triads.wav`
- `chapter_08_harmony_preview.wav`

## Bridge forward

One chord is a vertical object; harmony also unfolds through time. Chapter 9 orders chords into progressions and separates chord order from harmonic rhythm.
