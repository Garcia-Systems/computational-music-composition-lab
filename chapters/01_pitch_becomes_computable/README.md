# Chapter 1 — Pitch Becomes Computable

> How can we represent pitch so a computer can reason about musical relationships,
> rather than merely store frequencies?

## The musical problem

Chapter 0 composed `C4 → E4 → G4 → C5` by storing rendering data:

```python
frequencies = [261.63, 329.63, 392.00, 523.25]
```

That works for listening, but try moving the idea up five semitones. What is
seven semitones above C4? How far apart are E4 and C5? What does an octave move
do? Raw hertz makes each question a lookup or a frequency calculation. We want
the composition to store **musical information**, deriving acoustic information
only when sound is rendered.

## Twelve pitch classes

Western equal temperament divides the octave into twelve equal steps. For now,
the laboratory uses one canonical, sharp-based name for each pitch class:

```text
C  C# D  D# E  F  F# G  G# A  A# B
0  1  2  3  4  5  6  7  8  9  10 11
```

Pitch classes repeat modulo 12: 0, 12, 24, and 36 all have pitch class C, in
different octaves. In equal temperament C# and Db sound at the same frequency,
as do D# and Eb, and so on. Spelling nevertheless carries theoretical meaning.
Our simple model deliberately does not preserve that meaning yet and emits
sharps only.

## MIDI-style pitch numbers (without MIDI)

We borrow a familiar integer convention:

```text
C4 = 60   C#4 = 61   D4 = 62   ...   A4 = 69   ...   C5 = 72
```

These are **MIDI-style pitch numbers used as numerical representation**. We are
not producing MIDI files or learning the MIDI protocol. The benefit is ordinary
integer arithmetic:

```text
E4 - C4 = 64 - 60 = 4 semitones
C4 + 7  = 67 = G4
C4 + 12 = 72 = C5
```

The lab supports pitch numbers 0–127 and straightforward uppercase names with
optional sharps, such as `C4`, `C#4`, and `A4`. Flats are not parsed. The lowest
names require octave -1 (`C-1` is 0); the upper boundary is `G9`.

## Frequency becomes a derived value

Equal temperament anchors A4 at pitch 69 and 440 Hz. Each twelve-semitone rise
doubles frequency, so a renderer computes:

```text
frequency = 440 × 2^((pitch - 69) / 12)
```

Checkpoints make the formula concrete:

```text
69 → A4 → 440.00 Hz
60 → C4 → 261.63 Hz (approximately)
72 → C5 → 523.25 Hz (approximately)
```

Thus C5 − C4 is 72 − 60 = 12 semitones, while C5's frequency is about twice
C4's. Likewise A3, A4, and A5 are 220, 440, and 880 Hz. Integer octave distance
and physical frequency doubling describe the same relationship from musical
and acoustic viewpoints.

## Rebuilding the first composition

Chapter 0 remains unchanged: its hard-coded frequencies create the problem this
chapter solves. Chapter 1 reconstructs its idea as composition data:

```python
melody = [60, 64, 67, 72]
```

Only at the rendering boundary does each integer pass through
`pitch_to_frequency()`:

```text
COMPOSITION [60, 64, 67, 72]
                 ↓ pitch_to_frequency()
RENDERING   [261.63, 329.63, 392.00, 523.25]
                 ↓ sine waves → WAV
LISTENING
```

Run the experiment:

```bash
python -m composition_lab chapter-01
```

It creates, in listening order:

1. `outputs/chapter_01_original.wav` — `[60, 64, 67, 72]`
2. `outputs/chapter_01_transposed_5.wav` — `[65, 69, 72, 77]`
3. `outputs/chapter_01_transposed_octave.wav` — `[72, 76, 79, 84]`

The +5 version is `F4 → A4 → C5 → F5`. What changed? Absolute pitch moved.
What stayed the same? Every pitch moved by the same amount, preserving the
successive interval pattern:

```text
60 → 64 = +4       65 → 69 = +4
64 → 67 = +3       69 → 72 = +3
67 → 72 = +5       72 → 77 = +5
```

This is an early computational notion of melodic identity: pitches can change
while their pattern of distances stays. The +12 version sounds especially close
because it preserves both that pattern and every pitch class; it changes only
register. A later chapter will study intervals deeply—here they only make
transposition audible and inspectable.

## Reader experiments

Change one musical variable at a time, render, and listen before judging.

### Experiment A — Change the transposition

Replace `5` with `+1`, `+2`, `+7`, `-5`, and `-12`. How does the same interval
pattern feel from each starting pitch?

### Experiment B — Break the relationship

Change only one note: `[60, 64, 67, 72]` becomes `[60, 64, 68, 72]`. That single
semitone changes two adjacent interval movements. Listen before inspecting them.

### Experiment C — Compare registers

Transpose the whole melody by `-12`, `0`, `+12`, and `+24`. Pitch-class and
interval relationships remain, but does register affect weight or brightness?

## The next unsolved musical problem

Pitch is now expressive, but every note still uses a fixed, primitive duration.
We can describe *what pitches* happen far better than *when they happen*. That
intentional imbalance motivates Chapter 2; rhythm, tempo, rests, meter, and
accent are not implemented here.

## Bridge forward

Pitch relationships are now computable, but their timing is still primitive. Chapter 2 separates musical beats from rendered seconds so rhythm can become an independent variable.
