# Chapter 0 — The Composition Laboratory

## The question

> Can we describe a tiny musical idea as numbers, turn those numbers into
> sound, and hear the relationship between the representation and the result?

This first experiment is intentionally modest. We will compose an ascending
four-note idea—C4, E4, G4, C5—and save it as a WAV file. The goal is not a
beautiful virtual instrument. The goal is to establish a direct, audible link
between a musical decision and its representation.

## Three layers of a musical system

```text
COMPOSITION
What notes happen and when?
        ↓
PERFORMANCE
How are those notes played?
        ↓
SOUND
What do those notes actually sound like?
```

A composition might say “play C4, then E4.” Performance adds choices such as
timing, articulation, and loudness. Sound describes the vibrating result: a
waveform rendered by an instrument or loudspeaker. Keeping these layers separate
will later let us change a melody without changing an instrument, or change an
instrument without rewriting a melody.

Chapter 0 deliberately collapses parts of performance and sound. Every note has
a fixed duration and amplitude, and every note uses the same sine waveform. That
restriction lets us observe the entire path:

```text
musical decision
→ numerical representation
→ generated waveform
→ WAV file
→ listening
```

## Representing the first composition

For now, a note is only a name for the reader, a frequency in hertz, and a
duration in seconds:

| Name | Frequency | Duration |
|---|---:|---:|
| C4 | 261.63 Hz | 0.40 s |
| E4 | 329.63 Hz | 0.40 s |
| G4 | 392.00 Hz | 0.40 s |
| C5 | 523.25 Hz | 0.60 s |

This representation is deliberately primitive. We are not yet calculating
frequencies from pitch names, using MIDI numbers, or transposing notes. Those
are musical problems for a later chapter; hard-coded frequencies make today's
mechanism easier to see.

The composition lives as `CHAPTER_00_NOTES` in `composition_lab/cli.py`. Run it:

```bash
python -m composition_lab chapter-00
```

Then listen to `outputs/chapter_00_first_composition.wav`. Before reading on,
describe what you hear: its direction, pacing, and degree of completion.

## From frequency to samples

Digital audio is a sequence of numbers measured at regular moments. At a sample
rate of 44,100 Hz, the program calculates 44,100 sample values per second. For a
sine wave, each value follows this relationship:

```text
sample(t) = amplitude × sin(2π × frequency × t)
```

Frequency controls how many cycles occur each second and therefore the pitch we
hear. Duration controls how many samples are generated. Amplitude controls the
wave's height and perceived loudness. `sine_wave` calculates these values one at
a time; `render_notes` joins the notes; and `write_wav` safely scales the values
to signed 16-bit PCM integers understood by ordinary audio players.

Each note also receives a 10 ms linear attack and release. Starting or stopping
a nonzero waveform instantaneously makes a discontinuity, often heard as a
click. The tiny fade brings note boundaries toward zero without pretending to
be an expressive instrument.

## Experiment 1: change one pitch

**Hypothesis:** If only E4's frequency changes, the contour and character of the
whole idea will change even though its rhythm and sound remain fixed.

1. In `composition_lab/cli.py`, find the E4 row in `CHAPTER_00_NOTES`.
2. Change `329.63` to `349.23` (approximately F4). You may rename its label to
   `F4` so the printed description stays honest.
3. Run `python -m composition_lab chapter-00` again.
4. Listen and compare it with the original (save a copy first if useful).
5. Explain: Did the altered middle interval make the arrival on C5 feel
   different?

One small change in data has made an immediately audible musical change. Restore
the original value when finished.

## Optional experiment: change time

Keep every frequency fixed, but change G4's duration from `0.40` to `0.80`.
Predict whether the longer note will sound like emphasis, hesitation, or a point
of arrival. Generate, listen, compare, and explain. Notice that the pitches have
not changed; only the performance in time has.

## The recurring laboratory loop

These are not editing exercises with a hidden correct answer. They are controlled
listening experiments. We will return throughout the book to this method:

```text
HYPOTHESIS
    ↓
CHANGE ONE MUSICAL VARIABLE
    ↓
GENERATE
    ↓
LISTEN
    ↓
COMPARE
    ↓
EXPLAIN
```

Changing one variable makes cause and effect easier to hear. Explaining the
result turns an impression into compositional knowledge. Chapter 0 has proved
the essential premise: musical choices can become data, data can become sound,
and listening can guide the next choice.

## Bridge forward

The first experiment stores frequency directly. Chapter 1 asks how pitch can become a reusable symbolic relationship instead of a list of unrelated Hz values.
