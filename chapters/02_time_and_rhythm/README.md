# Chapter 2 — Time and Rhythm

> How can we represent musical time so rhythm can be created, transformed,
> measured, and compared computationally?

Chapter 1's `melody = [60, 64, 67, 72]` says **what** happens: C4, E4,
G4, C5. It cannot distinguish `1 1 1 1` from `2 .5 .5 1`. The pitches are
identical; the music is not. Pitch asks what happens. Rhythm asks **when** it
happens and **for how long**. A melody is not merely an ordered pitch sequence:
music exists in time.

## Composition time and rendering time

Seconds are useful to a synthesizer, but beats let a composer say “C4 for one
beat” before choosing its speed:

```text
COMPOSITION TIME (beats) → TEMPO (beats per minute) → RENDERING TIME (seconds)
```

The conversion is deliberately visible:

```python
seconds = beats * 60 / bpm
```

Thus one beat lasts 1 second at 60 BPM, 0.5 seconds at 120 BPM, and about
0.667 seconds at 90 BPM. Tempo and note durations must be positive.

## Parallel lists: useful, but awkward

For now rhythm lives beside pitch:

```python
pitches = [60, 64, 67, 72]
durations = [1.0, 1.0, 1.0, 2.0]
```

This makes duration audible without hiding the mechanism. It also requires the
lists to stay aligned. That inconvenience is intentional; we do not introduce
a general event object in this chapter.

Run the experiments:

```bash
python -m composition_lab chapter-02
```

### Same pitch, different rhythm

The command renders even (`1 1 1 1`), long-short-short-long
(`2 .5 .5 1`), and short-short-long-long (`.5 .5 2 2`) versions of the
same four pitches. Listen for how identity changes when pitch does not.

### Same rhythm, different tempo

The long-short rhythm is rendered at 60, 90, and 120 BPM. **Rhythm** is the
relative timing relationship; **tempo** is the rate at which it unfolds. Its
proportions have not changed, although its performance speed has. This resembles
Chapter 1's separation of interval relationships from absolute register.

### Silence is composed time

The temporary pitch list may contain `None`, which means a rest—not a fake
pitch. Compare `chapter_02_rest_filled.wav` with `chapter_02_rest.wav`: the
same half beat is occupied in one and silent in the other.

## Meter, weight, and subdivision

For this practical starting model, 4/4 groups four quarter-note beats per
measure:

```text
Measure 1                 Measure 2
1     2     3     4       1     2     3     4
C4    E4    G4    C5      ...
```

Meter supplies a recurring framework. A useful simplified 4/4 weighting is
`strong, weak, medium, weak`; this is not a universal law for all music.
Subdividing exposes offbeats numerically:

```text
quarter notes: 1       2       3       4
eighth notes:  1   &   2   &   3   &   4   &
durations:     1 beat, 0.5 beat, or 0.25 beat
```

The onbeat and syncopated WAVs use identical ordered pitches. The second moves
each onset half a beat to an `&`. Moving activity relative to the grid changes
groove and momentum; this listening comparison does not attempt a universal
mathematical definition of syncopation.

## Start time is not duration

Sequential durations `1, .5, .5, 2` imply starts `0, 1, 1.5, 2`. A C4 starting
at beat 0 for two beats differs from one starting at beat 1 for two beats:

```text
START TIME — when does it begin?
DURATION   — how long does it continue?
```

We can now imagine parallel `pitches`, `starts`, `durations`, and `velocities`
lists describing the same objects. We deliberately preserve this strain for
Chapter 3 rather than solving it prematurely.

## Reader experiments

1. **One rhythmic change:** begin with `1 1 1 1`, change only one duration,
   and listen. How much can one duration alter the phrase?
2. **Tempo:** render one rhythm at 40, 80, and 160 BPM. At what point does the
   same structure begin to feel like different music? There is no single answer.
3. **Add silence:** replace one note with a rest while preserving total time.
4. **Move an onset:** shift one note by half a beat. Does it feel more or less
   stable?

Keep composition first: change one musical variable, render, and listen before
adding complexity.

## Bridge forward

Parallel pitch, onset, and duration lists expose the next problem: facts about one note can drift apart. Chapter 3 joins them in an immutable `NoteEvent`.
