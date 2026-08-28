# Chapter 6 — Motifs and Transformation

> How can a small musical idea be transformed into enough related material to
> build a larger passage?

```text
NOTE → MOTION → MOTIF → TRANSFORMATION → DEVELOPMENT
```

A **motif is a short musical idea recognizable enough to be repeated, varied,
or developed**. Its identity may live in pitch relationships, rhythm, contour,
accent, or repetition. Here it is simply a short sequence of immutable
`NoteEvent` objects:

```text
C4       D4       E4          G4
0.5      0.5      1.0         1.0 beats
velocity 84       88          94          100
```

This is the book's transition from representing and analyzing music to helping
develop material systematically. The mechanics remain small, deterministic,
and inspectable.

## Portable musical time

`normalize_events` subtracts the earliest onset from every start. Starts
`4.0 4.5 5.0` become `0.0 0.5 1.0`; pitch, duration, and velocity do not
change. `motif_duration` calculates `latest end - earliest start`, rather than
assuming beat zero. This makes a motif portable even when its source events
began later in a score.

All operations return new events. They never edit their input. Supplied order
is retained except for retrograde, whose output is explicitly ordered by its
new sounding time.

## Transform one variable at a time

| Transformation | Transparent operation | Preserves | Changes |
|---|---|---|---|
| repetition | copies at `0, span, 2×span…` | everything inside the motif | timeline length |
| transposition | add one semitone offset to every pitch | intervals, rhythm, accent | absolute pitch |
| sequence | transpose each successive copy | recognizable idea and internal rhythm | pitch level and time |
| retrograde | reflect each event in the full span | pitch set and rhythm values | event order, contour, rhythmic order |
| inversion | `new = 2 × axis - old` | interval magnitudes, rhythm, accent | interval direction, register |
| augmentation | multiply relative starts and durations | pitches and temporal proportions | absolute time scale |
| diminution | multiply relative starts and durations | pitches and temporal proportions | absolute time scale |
| displacement | add `0.5` to normalized starts | every internal relationship | relationship to beat grid |

Transposition of `C D E G` by five semitones produces `F G A C` and preserves
`+2 +2 +3`. Inversion around C4 produces `C Bb Ab F`, whose intervals are
`-2 -2 -3`. This is **melodic/intervallic inversion**, not chord inversion.

Retrograde is not `reversed(events)` with the old starts. Each event is
reflected across the motif span:

```text
new start = span - (old start + old duration)
```

Consequently `C D E G` actually sounds as `G E D C`. With asymmetric rhythm,
the duration travels with its note, so the whole temporal pattern sounds
backward too. Likewise augmentation scales both onset spacing and duration;
merely lengthening notes would not augment the complete idea.

## Sequence and recognizable change

`sequence_motif(motif, (0, 2, 4, 5))` produces four consecutive copies at
chromatic transposition levels. It preserves exact semitone structure inside
each copy. A diatonic sequence would instead move notes by scale degrees and
preserve scale-relative structure; that distinction is worth exploring, but
this chapter deliberately avoids a generalized tonal-transformation engine.

> How can repetition remain recognizable without being literal?

## Run the listening laboratory

```bash
python -m composition_lab chapter-06
```

The command prints pitch, onset, duration, and Chapter 5 interval comparisons,
then renders original, four repetitions, +5 transposition, chromatic sequence,
retrograde, C4 inversion, augmentation, diminution, displacement, and a
development study. Inspect first; then listen. How quickly does repetition
establish identity? Does a changed temporal scale alter identity?

The 33-beat capstone is just over eight 4/4 measures:

```text
beats  0–3   original
beats  3–6   literal repeat
beats  6–18  sequence at 0, +2, +4, +5
beats 18–24  retrograde twice
beats 24–30  augmentation ×2
beats 30–33  return
```

This is a **motif-development study**, not formal phrase or cadence analysis.
The printed labels allow every heard section to be correlated with its data.

## Identity versus change

What must remain for recognition: interval pattern, rhythm, contour, event
order, timing proportions, accent shape—or only some combination? Retrograde's
intervals are the original intervals in reverse order with reversed signs;
inversion keeps their order and magnitude but reverses their signs. Chapter 5's
analysis has become a compositional inspection tool, while listening remains
the test of perceived identity.

## Reader experiments

1. **Change the motif.** Replace one pitch and rerun everything. How does one
   change propagate through the study?
2. **Change transposition distance.** Compare `+2`, `+5`, `+7`, and `+12`.
3. **Change inversion axis.** Compare register and contour around several axes.
4. **Use asymmetric rhythm.** Try `0.25, 0.75, 0.5, 1.5`, then retrograde it.
5. **Change development order.** Try original, retrograde, transpose,
   augmentation, return. Does order change musical direction?
6. **Transform too much.** Radically alter every occurrence. At what point does
   the motif stop feeling recognizable? There is no single correct answer.

## Deliberate boundary

This chapter introduces no phrase, cadence, chord progression, harmony, voice
leading, probability, SuperCollider, or OSC machinery. It does not decide when
a passage feels like a question or ending. Those require later concepts;
Chapter 6 stays with transparent transformations of a small musical idea.
