# Chapter 14 — Bass as Harmony, Rhythm, and Melody

> How can a bass line connect harmony and groove while still behaving as a melodic line of its own?

```text
HARMONIC ROOT → BASS PITCH → RHYTHMIC PLACEMENT → BASS LINE
                                      ↓
                         HARMONY + GROOVE + MELODY
```

Bass is not merely “the bottom note of a chord.” It is a low-register melody whose
attacks participate in groove and whose pitches have changing relationships to
harmony. Run the deterministic listening laboratory:

```bash
python -m composition_lab chapter-14
```

## Root targets and register

`harmonic_root_pitch_classes()` reads scale-degree metadata; it never guesses a
root from a rendered voicing. Thus **harmonic root ≠ lowest voicing pitch**.
This chapter uses inclusive MIDI E1–C4 (28–60). `root_in_register()` lists the
in-range octave copies and chooses the lowest, or the nearest to an explicit
reference (with the lower pitch breaking a tie). `nearest_bass_pitch()` repeats
that inspectable one-line choice for successive targets. This is a contour option,
not a claim that minimum motion is best.

I–IV–V–I first yields C2–F2–G2–C2, one structural root target per four-beat chord.
Sustained roots and four repeated quarter-note roots keep pitch and harmony fixed,
so their difference isolates bass rhythm. **Harmonic rhythm** says when chords
change; **bass rhythm** says when bass attacks. One chord can last four beats while
bass attacks many times.

## Groove and chord roles

The Chapter 13 grid drives a repeating bass pattern. “Locking” means related attack
positions, not a rule that bass and a low rhythmic role must always coincide.
The same onset grid can follow I–V–vi–IV roots, or alternate each root with its
fifth. Rhythm retains an identity while harmonic content changes.

For a triad, `bass_chord_role()` reports `root`, `third`, `fifth`, or
`non-chord-tone`. Under C major, C is root, E third, G fifth, and D non-chord tone.
These labels describe harmonic effect; they do not rank the choices. E beneath the
same C-major upper pitches makes first inversion and G makes second inversion.

## Connection, approach, and pedal

Structural targets may be joined rather than merely juxtaposed:

```text
ROOT TARGET → PASSING / APPROACH MOTION → NEXT ROOT TARGET
C2          → D2 → E2                  → F2
```

The narrow `connect_bass_targets()` example fills ascending diatonic pitches. An
approach note leads by step: F2–G2 is diatonic, while F#2–G2 is chromatic. Neither
requires secondary-dominant theory, and connecting notes are not automatically
unimportant or better.

A tonic pedal holds C while I–IV–V–I changes. C is I's root but is not in the
G-major V triad. The changing label is intentional, not an automatic error:
harmonic function can move T–P–D–T while the physical bass pitch refuses to move.

## Bass as a measured melody

Chapter 5's tools report pitch and interval sequences, range, direction, repeats,
average interval size, and largest leap. C2–F2–G2–C2 and a voiced C2–C2–B1–C2
therefore expose different contours. Smoother does not mean better. Likewise,
fixed-octave C–G–A–F and nearest-register targets choose different octave paths.

The capstone deliberately combines four existing layers: melody, triadic harmony,
a pitched groove proxy, and one monophonic root/fifth bass. It is a composition
example—not a generalized arranger.

## Reader laboratory

1. Replace one root with a fifth without changing rhythm.
2. Double bass attacks while retaining structural targets.
3. Remove repeats and use one onset per chord.
4. Add one diatonic passing note.
5. Add one chromatic approach by semitone.
6. Hold C through several harmonies as a tonic pedal.
7. Change the starting octave.
8. Compare fixed-octave with nearest-register roots.
9. Move one attack by half a beat.
10. Mute melody, harmony, and groove. Does the bass contour cohere alone?

## Deliberate boundary

The model is triadic, regular-grid, deterministic, and monophonic. Bass practice
also includes walking bass, ostinatos, riffs, drones, slap patterns, chromatic and
contrapuntal lines, figured bass, independent melodies, extended harmony, and
style-specific articulation. Those are acknowledged, not implemented. This
chapter stops at bass: it leaves the combined texture/accompaniment engine to Chapter 15.

## Bridge forward

Bass connects harmony and groove, yet a piece also depends on how all layers share register and activity. Chapter 15 turns separate roles into texture and accompaniment.
