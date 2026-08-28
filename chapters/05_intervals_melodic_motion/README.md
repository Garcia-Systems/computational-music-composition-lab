# Chapter 5 — Intervals and Melodic Motion

> How can we describe the way a melody moves from note to note?

Chapter 4 can place `1 2 3 5 3 2 1` in a key, but tonal roles do not explicitly
describe its motion. In C major the pitches are `60 62 64 67 64 62 60`; their
successive movements are `+2 +2 +3 -3 -2 -2`. **A melody is not only a
sequence of pitches. It is also a sequence of movements.**

```text
PITCH → INTERVAL → MOTION → CONTOUR → MELODY PROFILE
```

## Signed intervals: direction and size

`interval_between(first, second)` subtracts the first pitch from the second:

```text
60 → 64 = +4 (ascending)   64 → 60 = -4 (descending)
60 → 60 =  0 (stationary/repeated pitch)
```

The sign describes direction; `interval_size(-5)` is `abs(-5)`, or 5
semitones. Keeping these calculations separate prevents an opaque label from
hiding useful information. `interval_sequence` applies the same subtraction to
each adjacent pair. Empty and one-note melodies therefore have no movements.

For this practical laboratory, `classify_motion` calls 0 a **repeat**, 1–2
semitones a **step**, and 3 or more a **leap**. This is an intentional
computational simplification. Traditional interval identity depends on richer
context and spelling; semitone count alone is not a complete theory.
`motion_direction` separately returns `ascending`, `descending`, or
`stationary`.

## Structured events, ordered pitches

The audible studies remain `NoteEvent` sequences:

```text
NoteEvent sequence → extract pitches → calculate intervals
                   → analyze motion → render → listen
```

`pitches_from_events` preserves the sequence supplied by the composer; it does
not sort by start time. Thus pitch order alone controls this chapter's primary
calculation, while starts, durations, and velocities remain available to the
renderer. Analysis and rendering are separate operations.

## Range and contour

Melodic range is deliberately small arithmetic:

```text
highest pitch - lowest pitch
67 - 60 = 7 semitones
```

An empty melody has range 0 and no extrema; a one-note melody has range 0 with
that note as both extrema. `contour_directions` describes every adjacent pair.
For `C D E G F D C`, it reports three ascending and three descending motions.
Compact `+ + + - - -` symbols would convey the same rough shape.

Terms such as **ascending**, **descending**, **arch**, **inverted arch**,
**wave-like**, and **mostly static** are useful listening descriptions, not
classes that every melody must fit. The code intentionally does not pretend to
recognize a universal contour category. It exposes directions and statistics,
then leaves interpretation to the reader.

## The melodic profile

`melodic_profile` reports note and movement counts, extrema and range,
repeat/step/leap balance, direction balance, percentages, and mean absolute
interval size. For intervals `+2 +2 +5 -2 -2`, the average is
`(2 + 2 + 5 + 2 + 2) / 5 = 2.6`. Percentages use movements as their
denominator. When there are none, counts, percentages, and the average are zero.

These are descriptions, not scores. A smaller average interval is not a better
melody. Two melodies can share range, stepwise percentage, and average interval
while placing pitches in a different order and sounding plainly different.

## Run the listening laboratory

```bash
python -m composition_lab chapter-05
```

The command prints signed intervals, motion and direction sequences, and
side-by-side stepwise/leaping profiles. It renders every study at 120 BPM with
half-beat notes, velocity 90, and the existing sine synthesizer:

1. **Mostly stepwise / leaping** — same C-major context, note count, rhythm,
   velocity, and duration. How does character change when interval size changes?
2. **Continuous motion / repeated notes** — compare moving pitches with
   `C C D D E E D C`. Does repetition suggest stability, insistence, rhythmic
   focus, or something else?
3. **Narrow / wide range** — related arch contours occupy 4 and 9 semitones.
   Does width suggest energy, drama, instability, spaciousness, or simply
   difference?
4. **Arch / inverted arch** — `C D E G A G E D C` and
   `A G E D C D E G A` share rhythm and range. How does direction differ?

Scale-step motion and semitone motion are related, not identical. In C major,
degree 1→2 means C→D, or +2 semitones, while degree 3→4 means E→F, or +1.
We do not need a diatonic interval-naming system to observe that distinction.

## Reader experiments

- **A — Replace a step with a leap.** Change one pitch in the stepwise line,
  render both, and listen before reading their profiles.
- **B — Reduce the range.** Move the wide line's outlying pitches inward while
  preserving rhythm and note count.
- **C — Add repeated notes.** Replace movements with repeats without changing
  durations. Decide what the result communicates to you.
- **D — Reverse contour manually.** Rewrite an ascending pattern as descending.
  This is a listening comparison, not a formal inversion transformation.
- **E — Same statistics, different melody.** Reorder a line while trying to
  preserve range, step percentage, and average size. Do similar statistics make
  it the same melody? No: a profile omits pitch order and much musical context.

## Analytical restraint and boundary

```text
ANALYSIS CAN DESCRIBE              ANALYSIS DOES NOT DETERMINE
range                              beauty
interval sizes                     memorability
direction                          emotion
step/leap balance                  quality
repetition                         meaning
contour tendencies
```

Analysis explains how two melodies differ structurally. **Listening tells us
what those differences mean musically.** This chapter builds no automatic
quality measure and no brittle contour classifier. It introduces no motifs,
phrases, chords, harmony, voice leading, SuperCollider, OSC, or machine
learning. Formal motif transformations belong to a later chapter; Chapter 5
stops at measuring movement.
