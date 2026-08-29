# Chapter 29 — Blues

> How can the computational tools developed so far be used to model and experiment
> with recognizable blues structures without reducing the style to a rigid formula?

## Method and context

**A musical style is larger than any list of scales, chord progressions, rhythms,
or algorithms.** A computational model can represent selected features. Musical
data alone cannot establish authenticity, historical meaning, cultural identity,
or expressive quality.

Blues developed within African American musical traditions in the United States
and became foundational to jazz, R&B, rock and roll, rock, soul, and funk. This is
a focused computational lab, not a comprehensive history. The familiar twelve-bar
model is useful pedagogy, but blues is not limited to it: performances alter,
extend, compress, substitute, and reinterpret textbook patterns.

The lab therefore does **not** claim `12 bars + blues scale = blues`. It isolates
interacting tendencies—form, I/IV/V relationships, pitch inflection, rhythmic
feel, repetition, call and response, phrase placement, space, bass, and performance
practice—then changes one variable at a time.

## Transparent recipes

The baseline is `I I I I | IV IV I I | V IV I I`, one chord per four-beat bar.
Reader-facing bars are one-indexed; event time stays zero-based in beats, so bar 5
starts at beat 16 and twelve bars occupy 48 beats. A quick-change second chorus and
a V7 in bar 12 as a turnaround are documented variations, not definitive rules.

Chapter 29 narrowly adds dominant sevenths `(0, 4, 7, 10)`. Using I7, IV7, and V7
is not identical to common-practice functional harmony: C7 on I is not simply a
conventional classical tonic. Likewise, Chapter 12's “non-chord tone” remains a
description rather than “wrong note”; Eb against C7 is an intentional, listenable
melody/harmony friction experiment.

The commonly taught minor blues scale `(0, 3, 5, 6, 7, 10, 12)` is a discrete
12-TET approximation. It can encode Eb and E but largely hides the expressive space
between them. Bends, slides, microtonal and variable intonation, vocal inflection,
and guitar articulation cannot be captured fully by integer pitch.

Straight eighths place attacks at `0, 1/2`; the simplified shuffle places them at
`0, 2/3`, imagined as triplet positions `X . X`. Blues can use straight, swung,
shuffled, and other feels. This exact ratio is a controlled model, not a prescription
for performed timing and not mechanical “humanization.”

The capstone uses a generated A and derived A′/B/A″/A‴/B′ phrases, leaving silence
inside each four-bar window. A riff is represented with the existing motif/event
infrastructure. Its bass transposes one root-relative `1-3-5-6-6-5-3-1` recipe.
Human authors specify form, harmony, groove, and relationships; a local RNG seeded
with `2026` supplies bounded note detail. Symbolic JSON precedes WAV or optional OSC.

Run `python -m composition_lab chapter-29`; add `--live` only with the existing
Chapter 26 SuperCollider receiver running.

## What This Model Does Not Capture

This deliberately partial model does not capture microtonal pitch inflection,
human swing variation, vocal phrasing, guitar-specific articulation, tone production,
interaction among musicians, regional and historical styles, lyrical traditions,
improvisational vocabulary, individual performer identity, or cultural and historical
context. It defines no authenticity/style score and performs no genre classification.

## Listening worksheet

- What changes when triads become dominant sevenths?
- What changes between major-scale and minor-blues-scale approximations?
- Where does melody conflict with chord tones, and how does context change labels?
- What changes when straight attacks move to the shuffle grid?
- Where do rests separate call and response, and which material repeats?
- What changes over IV7, when the bass moves, and at the turnaround?

## Bridge forward

The blues lab begins with cyclical form, shuffle, and pitch/harmony friction. Chapter 30 changes model rather than claiming a linear genre progression: riff, backbeat, and sectional songwriting become the organizing devices.
