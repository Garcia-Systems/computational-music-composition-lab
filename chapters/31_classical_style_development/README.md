# Chapter 31 — Classical-Style Development

> How can a small motif be transformed, sequenced, fragmented, reharmonized,
> and distributed across a larger formal argument?

“Classical-style development” here is a limited computational study of
techniques associated with common-practice and related instrumental traditions,
not a definition or authenticity test for classical music as a whole.

The executable lab moves from a four-note original motif through literal and
sequential repetition, fragmentation, rhythmic scaling, inversion, retrograde,
harmonic recontextualization, phrase expansion, development, literal return,
and a derived coda. Every major placement has deterministic provenance.

```bash
python -m composition_lab chapter-31
python -m composition_lab chapter-31 --live  # optional localhost OSC
```

The 64-beat capstone has **Opening**, **Development**, **Return**, and **Coda**
sections. It is called a motivic development study, not a sonata. The generated
JSON, provenance, manifest, OSC schedule, and reference WAV are written to
`outputs/`. Playback mapping changes sound roles without changing score data.

## Reader experiments

- Change sequence distance, fragment size, or inversion axis.
- Compare original, diminished, and augmented rhythm over identical harmony.
- Change harmony while retaining the exact motif and inspect chord-tone labels.
- Repeat a developmental stage, vary return accompaniment, or remove the coda.
- Change layer playback while retaining symbolic notes and provenance.

## What This Model Does Not Capture

The study does not model historical stylistic diversity, ornamentation,
counterpoint in depth, instrument idioms, rubato, articulation nuance, phrase
shaping, advanced harmonic syntax, sonata procedures, orchestration, or human
interpretation. `NoteEvent` also lacks slurs, dynamic curves, phrasing, rubato,
and technique metadata. Chapter 32's gradual/process-specific systems are not
implemented here.
