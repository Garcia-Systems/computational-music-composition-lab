# Chapter 3 — The Musical Event

> What is the smallest useful unit of a computational composition?

## The problem Chapter 2 leaves us

Chapter 2 can describe the familiar melody with parallel lists:

```python
pitches = [60, 64, 67, 72]
starts = [0.0, 1.0, 1.5, 2.0]
durations = [1.0, 0.5, 0.5, 2.0]
```

Which duration belongs to G4? We must trust that matching indexes stay aligned:

```text
pitches[2]
starts[2]
durations[2]

all describe ONE musical event
```

The data structure should reflect the musical idea. Those values become
`NoteEvent(pitch=67, start=1.5, duration=0.5)`: properties that belong together
now live together. A melody is a sequence of musical events—our first
approximation of a computational score.

## A musical object requires a data class

We have discovered a musical object with several related properties. Python
needs a clean way to represent that object:

```python
from dataclasses import dataclass

@dataclass(frozen=True)
class NoteEvent:
    pitch: int
    start: float
    duration: float
    velocity: int = 90
```

- **pitch** is the MIDI-style pitch number established in Chapter 1.
- **start** is its onset in beats from the composition's beginning.
- **duration** is its length in beats.
- **velocity** is an intensity value on the convenient MIDI-style 0–127 scale.

We borrow that familiar velocity scale; we are neither generating MIDI nor
teaching the MIDI protocol. Velocity is abstract performance intensity, not a
universal synonym for loudness. Our simple synthesizer transparently maps
`0` to silence and `127` to its maximum single-note amplitude.

The event validates pitch and velocity as 0–127, start as nonnegative, and
duration as positive. `frozen=True` makes an event a stable compositional fact:
C4 starts at beat 0, lasts one beat, and has velocity 90. A transposition returns
a new fact rather than secretly editing the old one. That makes experiments
reproducible, transformations safer, and originals easy to compare with results.

```text
original → transpose +5 → new event
```

## Rebuilding the melody

```python
melody = [
    NoteEvent(pitch=60, start=0.0, duration=1.0),
    NoteEvent(pitch=64, start=1.0, duration=0.5),
    NoteEvent(pitch=67, start=1.5, duration=0.5),
    NoteEvent(pitch=72, start=2.0, duration=2.0),
]
```

```text
BEFORE                              AFTER
pitches / starts / durations   →    NoteEvent / NoteEvent / NoteEvent / NoteEvent
```

The composition ends at `max(start + duration)`, which is 4 beats here. It is
not necessarily the sum of durations: events can overlap or leave gaps. An
event from beat 0 for 4 beats plus one from beat 1 for 1 beat has durations
totaling 5, but the composition still ends at beat 4.

Silence needs no fake note. If one event ends at beat 1 and the next starts at
beat 2, the unoccupied timeline from beat 1 to 2 is silent. Chapter 2 retains
`None` rests because that limitation is part of its historical lesson.

## Events share a timeline

The renderer, rather than `NoteEvent`, performs tempo, pitch, sample-position,
and velocity conversions:

```text
COMPOSITION DATA                         AUDIO
pitch / beat start / beat duration       frequency / samples / amplitude
NoteEvent → tempo, pitch, velocity conversion → mixed buffer → WAV
```

It first allocates the complete timeline, synthesizes every event, adds it at
its start sample, and normalizes the mix only if it would clip. This replaces
concatenation with placement:

```text
timeline  ────────────────────────────>
event 1   ███████
event 2       █████
event 3       █████████
```

Consequently C4, E4, and G4 can occur sequentially or all start at beat zero.
The representation supports melody-like succession and simultaneous sound;
pitch-set and chord theory deliberately wait for a later chapter.

## Experiments

Run `python -m composition_lab chapter-03`. It renders:

1. the familiar **structured melody**;
2. **even velocity** `90 90 90 90` against **shaped velocity** `60 80 105 75`—can intensity alone create direction?;
3. C4, E4, G4 **sequentially** and **simultaneously**—the pitches are identical, so why is the result dramatically different?;
4. the original score and a new score **transposed +5 semitones**.

Small helpers also transpose, shift, or scale an event and wrap those operations
across a score. Each returns new events; the originals remain unchanged.

## Reader experiments

- **Move one note:** change the G4 start from `1.5` to `2.0`. Hear the gap and
  consider what would instead create overlap.
- **Lengthen one note:** keep its start and extend its duration until it overlaps
  its successor.
- **Shape intensity:** compare `50, 70, 90, 110` with the reverse contour.
- **Build simultaneity:** give several events `start=0` and listen.
- **Shift the score:** move everything two beats later. Did its internal
  composition change, or only its position on the timeline?

This chapter stops at arbitrary pitch-number events. Scales, keys, modes,
chord construction, and tonal choice are intentionally outside its scope.
