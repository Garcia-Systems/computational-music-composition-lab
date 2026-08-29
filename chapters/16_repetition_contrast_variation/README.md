# Chapter 16 — Repetition, Contrast, and Variation

> How can a composer repeat enough material to create identity while changing enough material to create direction?

```text
IDEA → REPETITION → VARIATION → CONTRAST → RETURN → DEVELOPMENT
```

Run `python -m composition_lab chapter-16` to render the listening laboratory.

## Identity through time

Literal `A + A` establishes recognition, memory, expectation, and reinforcement;
exact repetition is not inherently boring. Musical identity can persist because
motif, contour, rhythm, harmony, groove, texture, or register remains stable.
`A'` is not a data type: it is a useful label for “A, changed in some way.”

The immutable `Passage` is deliberately small: a name and an event tuple.
`passage_duration()` measures latest end minus earliest onset. Placement first
normalizes material to zero; `place_after()`, `append_passages()`, and
`repeat_passage()` return new events and never edit their sources. This is passage
assembly, not a section hierarchy or form engine. Code reuse avoids duplicate
implementation; musical repetition deliberately repeats audible material to
shape listening.

## Controlled variation laboratory

The chapter changes one variable at a time: pitch with timing fixed; rhythm with
pitch order fixed; register by an octave; texture by adding broken chords and
groove; IV to diatonic ii under the same melody; root bass to melodic bass; and
one added groove offbeat. Variation need not be carried by melody. The event
comparison reports only event count, span, pitch, onset, duration, and velocity
equalities. The variation inventory prints declared changes in pitch, rhythm,
harmony, bass, groove, texture, and register. Neither pretends to measure quality
or recognizability.

The ending variation retains A's opening, while A'' combines a changed ending
with fuller texture. `A A A A'` establishes and then alters expectation; placing
the identical A' early versus late asks whether timing affects noticeability.

## Contrast, continuity, and return

B is composed rather than randomized: it uses more leaps, eighth-note activity,
higher register, a changed diatonic harmonic path, melodic bass, and thicker
texture. Yet its G–A–B–D opening transposes A's C–D–E–G motif, demonstrating
motivic continuity beneath contrast. Other comparisons retain or change texture,
harmony, rhythm, and groove so conclusions remain open.

`A–B–A` makes an identical return audible after contrast. `A–B–A'` returns with
changed arrangement. Context can change the experience of unchanged events, but
the program does not calculate that perception. These are repetition/contrast/
return studies; they are **not** labeled as named musical forms.

The 32-beat capstone is `A → A' → B → A''`: original thin material, rhythm
variation, deliberate contrast, and a fuller return with a changed ending.

## Reader laboratory

1. Change only A's final note.
2. Change only rhythm while retaining pitch order.
3. Change only texture while retaining melody and harmony.
4. Transpose one fragment with Chapter 6's tools.
5. Change several dimensions to compose a strong B.
6. Preserve A's motif or groove inside B.
7. Assemble a literal A–B–A return.
8. Return differently with A–B–A'.
9. Repeat A four times and change only repetition four.
10. Make A' deliberately large. At what point does it begin to feel more like B?

## Deliberate boundary

Development can also include thematic transformation, fragmentation, motivic
saturation, sequence, augmentation/diminution, reharmonization, counterpoint,
orchestration, and developmental harmony. This chapter acknowledges rather than
systematizes those traditions. It implements no randomness, universal similarity
score, named form, section model, or generalized form engine. Chapter 17 remains
unimplemented and will ask how these relationships become larger named structures.

## Bridge forward

Relationships among passages suggest larger boundaries but do not name or schedule them. Chapter 17 makes section plans and form explicit.
