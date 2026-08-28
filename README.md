# Computational Music Composition Lab

## An Executable Textbook for Composition, Generative Music, and Sound Design with Python and SuperCollider

This is a music composition textbook that you **read and execute**. Its central
question is:

> How can we represent musical ideas as data, transform them computationally,
> hear the results, and use those experiments to become better composers?

Python is the compositional and analytical engine: it makes musical decisions
visible as inspectable data and small transformations. Much later,
SuperCollider will become the synthesis, sound-design, and real-time performance
engine. It is intentionally **not required now**. Chapter 0 uses only Python's
standard library and keeps every step from frequency to audio sample visible.

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
- No runtime dependencies for Chapter 0

From the repository root, either run directly:

```bash
python -m composition_lab chapter-00
```

or install an editable copy and use its console command:

```bash
python -m pip install -e .
composition-lab chapter-00
```

The experiment creates `outputs/chapter_00_first_composition.wav`. Open that
ordinary WAV file in any audio player. Generated audio is ignored by Git; only
`outputs/.gitkeep` preserves the output directory.

Continue with [Chapter 0 — The Composition Laboratory](chapters/00_composition_lab/README.md)
to connect what you hear with the data and waveform that produced it.

## Planned journey

Only Chapter 0 exists today. The broad route—not a claim of implemented
features—is:

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
