# Computational Music Composition Lab

## An Executable Textbook for Composition, Generative Music, and Sound Design with Python and SuperCollider

This is a music composition textbook that you **read and execute**. Its central
question is:

> How can we represent musical ideas as data, transform them computationally,
> hear the results, and use those experiments to become better composers?

Python is the compositional and analytical engine: it makes musical decisions
visible as inspectable data and small transformations. Much later,
SuperCollider will become the synthesis, sound-design, and real-time performance
engine. It is intentionally **not required now**. The completed chapters use
only Python's standard library and keep every step through audio visible.

## The laboratory model

Every chapter should produce something audible. The book distinguishes three
layers, even when an early experiment temporarily combines them:

```text
COMPOSITION — What musical events happen and when?
       ↓
PERFORMANCE — How are those events performed?
       ↓
SOUND — What acoustic signal is produced?
```

Code is introduced when a musical question requires it—not as syntax for its
own sake. Important musical mechanics remain transparent, and future experiments
involving randomness will use explicit seeds so results can be reproduced.

## Requirements and setup

- Python 3.11 or newer
- No runtime dependencies for Chapters 0–2

From the repository root, either run directly:

```bash
python -m composition_lab chapter-00
python -m composition_lab chapter-01
python -m composition_lab chapter-02
```

or install an editable copy and use its console command:

```bash
python -m pip install -e .
composition-lab chapter-00
composition-lab chapter-01
composition-lab chapter-02
```

The commands create ordinary WAV files in `outputs/`; open them in any audio
player. Generated audio is ignored by Git; only `outputs/.gitkeep` preserves the
output directory.

## Completed chapters

- [Chapter 0 — The Composition Laboratory](chapters/00_composition_lab/README.md)
  carries one hard-coded-frequency idea from musical choice through waveform to
  listening, establishing the executable-textbook method.
- [Chapter 1 — Pitch Becomes Computable](chapters/01_pitch_becomes_computable/README.md)
  replaces stored frequencies with pitch names and integers, then makes
  transposition and interval preservation audible.
- [Chapter 2 — Time and Rhythm](chapters/02_time_and_rhythm/README.md)
  separates beats from seconds, then makes rhythm, tempo, rests, meter,
  subdivision, and syncopation audible.

The progression so far is direct: Chapter 0 shows that sound can be generated
from numerical musical decisions; Chapter 1 makes pitch relationships
computable; Chapter 2 makes musical time computable.

## Planned journey

Only Chapters 0, 1, and 2 exist today. The broad route—not a claim of implemented
features beyond those chapters—is:

```text
sound / notes → pitch → rhythm → musical events → scales and tonality
→ intervals → motifs → phrases → chords → harmony → voice leading
→ melody against harmony → groove → bass → texture → variation → form
→ constraint-based composition → controlled randomness
→ generative composition → musical analysis → synthesis → SuperCollider
→ OSC → algorithmic performance → style laboratories → complete composition
```

## Run the tests

```bash
python -m unittest discover -s tests -v
```
