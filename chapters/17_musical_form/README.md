# Chapter 17 — Musical Form

> How can repetition, contrast, and return be organized into larger musical structures?

```text
PASSAGE → SECTION → SECTION RELATIONSHIPS → FORM → LARGE-SCALE MUSICAL SHAPE
```

Run `python -m composition_lab chapter-17` to print the inspectors and render every study.

## Sections and plans

A `Section` is the smallest useful new abstraction: a display label, an optional
descriptive role, and an immutable tuple of `NoteEvent` content. Construction
locally normalizes the earliest onset to beat zero. Its duration is the timeline
span from earliest onset to latest end, not summed note duration; overlapping
melody, chords, bass, and groove therefore do not falsely lengthen it.

A plan such as `("A", "B", "A")` is deliberately plain data. `assemble_form()`
validates its labels, looks each one up in a section dictionary, shifts fresh
events to a cursor, and reports label/start/end/duration placements. Repeated A
occurrences read the same immutable source. Optional non-negative gaps model
silence without inventing silence events. Apostrophes have no parser semantics:
`A'` content is stored explicitly. A template alone is not music:

```text
FORM PLAN + SECTIONS → MUSICAL TIMELINE
```

Content means actual events; role means A, B, verse, chorus, or another useful
context label. No label automatically composes “chorus behavior.” Identity may
involve melody, harmony, groove, texture, duration, register, or position, but
remains compositional and perceptual rather than something this program detects.

## Formal listening studies

- **Binary, A B:** two eight-beat principal sections. B retains a motivic link
  while changing register, rhythm, harmonic direction, bass, and texture. Real
  historical binary forms can include internal repeats, tonal relationships,
  and return-like behavior; two unrelated blocks are not a universal account.
- **Repeated and varied binary:** `A A B B` literally approximates section
  repeats without repeat-sign parsing; `A A' B B'` lets variation coexist with
  repetition. How do repeats change the scale and memory of the form?
- **Ternary:** `A B A` presents identity, contrast, and literal return. `A B A'`
  changes texture while preserving core material. How much can change while the
  last section still functions as a return?
- **AABA:** `A A B A` establishes, reinforces, contrasts, and returns. The
  companion `A A' B A''` changes texture and endings, and prints a timeline.
- **Verse/chorus:** the study uses a thinner/lower verse and thicker/higher,
  more active chorus. Those are choices for this experiment, never requirements.
  A second verse changes its bass layer and a final chorus adds texture. Musical
  role is why verse/chorus is not merely synonymous with abstract A/B.
- **Through-composed:** `A B C D` proceeds through distinct short sections,
  without implying an absence of motif-level recurrence. An `A B A` versus
  `A B C` comparison isolates return from new successive material.

Binary and ternary comparisons share the same A and B. Further controlled files
compare immediate/one-beat-gap transitions; 8+8+8 and 8+12+8 proportions; and
texture-marked/uniform-texture plans. Silence needs no special event. Objective
proportions describe time, not formal balance or quality, and symmetry is not
presented as preferable.

## Simplified twelve-bar blues

One four-beat triad per bar realizes this transparent C-based outline:

```text
I  I  I  I
IV IV I  I
V  IV I  I
```

The 48-beat cycle adds a straight eighth-note pitched groove proxy, root/fifth
bass, and diatonic motif. A 96-beat two-chorus study keeps the harmonic form and
changes one melodic surface detail in chorus two. This triadic approximation is
about hearing the recurring harmonic unit; it does not claim the stylistic or
harmonic richness of blues and introduces neither swing nor walking-bass systems.

## Capstone and hierarchy

The capstone is `A A' B A''`, proportioned 8+8+16+8 beats. It combines melody,
harmony/accompaniment, bass, groove, register, and texture so boundaries remain
audible. The inspector prints its 40-beat map, relations, proportions, and chosen
active-layer counts:

```text
0        8        16                32       40
|--- A ---|--- A' ---|------ B ------|--- A'' ---|
```

This completes a conceptual—not inheritance-based—hierarchy: note events form
motifs; motifs form phrases; phrases form passages; passages form sections; and
sections form a complete plan.

## Reader laboratory

1. Turn binary `A B` into ternary by appending A.
2. Vary the return to make `A B A'`.
3. Shorten only B; then lengthen only B and compare pacing.
4. Repeat both binary sections as `A A B B`.
5. Reuse A and B to make AABA.
6. Change only texture between verse and chorus while retaining related harmony.
7. Repeat the blues form twice and vary only second-cycle melody.
8. Replace a return with new C material.
9. Remove every texture difference. Are formal boundaries still obvious?
10. Add a one-beat gap. How does silence affect the boundary?

## Deliberate restraint

These are simplified executable models, not universal analytical rules: A need
not be eight bars, choruses need not be louder, and ternary is not declared more
complete than binary. Rounded binary, compound ternary, strophic, rondo, sonata,
variation, developmental, hybrid forms, and ambiguous boundaries are acknowledged
but not implemented. There is no symbolic-form parser, audio section detector,
random form generation, probabilistic ordering, constraint solving, or candidate
search. Chapter 18 takes up that bounded candidate-search question.

## Bridge forward

A form plan arranges authored material; it does not explore alternatives under rules. Chapter 18 defines bounded possibility spaces with inspectable constraints.
