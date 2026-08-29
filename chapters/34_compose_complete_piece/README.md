# Chapter 34 — Compose a Complete Piece

> Can we use the entire laboratory—from musical representation through
> generation, selection, arrangement, synthesis, and performance—to create one
> complete original composition with a transparent record of how it was made?

## Composition brief

**Converging Paths** is an original, stylistically neutral instrumental piece
with a clear opening identity, contrasting middle, recognizable return,
gradual textural growth, generated and transformed material, and a deliberately
designed ending. At 96 BPM its 152 beats last 95 seconds.

The form is `INTRO — A — A' — B — DEVELOPMENT — A'' — CODA`, lasting
`8 + 24 + 24 + 24 + 32 + 24 + 16` beats in C major and 4/4. This plan and the
delegation plan exist before candidate generation.

## From idea to performance

The human authors the brief, form, motif, harmony, strategies, recorded
selections, revision, playback map, and stopping decision. The algorithm
proposes three A' transformations and six seeded constrained-random-walk B
melodies, mechanically derives development, harmony voices, bass and groove,
analyzes events, serializes the score, renders audio, and schedules OSC.
Default execution does **not** listen: `a-prime-candidate-02` and
`b-candidate-04` are recorded human selections. The selected B is explicitly
revised by lengthening its final tonic. Rejected candidates remain inspectable.

```bash
python -m composition_lab chapter-34
python -m composition_lab chapter-34 --candidates
# Performs the identical finalized score; requires the Chapter 26 receiver:
python -m composition_lab chapter-34 --live
```

The canonical JSON preserves sections, layers, material IDs, decisions, and
provenance. Flattening is only a rendering operation. Instrument, pan, and
effect choices are separate playback metadata and cannot feed back into note
generation. Identical brief, seed, selections, and revision produce identical
symbolic JSON.

To compose another version, edit the source motif, section durations, recorded
candidate IDs, tempo, bass strategy, or texture plan in `chapter34.py`, then
rerun. Change one variable at a time and retain the main artifacts when making
the retrospective experiments: unrevised B, alternate A', alternate B, or a
flat texture.

## Human listening worksheet

- Which B candidate would you choose?
- Would you revise the selected candidate differently?
- Does A'' feel sufficiently related to A?
- Which developmental transformation is easiest to hear?
- Does the coda feel like an ending?
- Which layer would you remove?
- Would you choose different playback sounds?

These are prompts for listening, not assertions in automated tests. A complete
composition is not one clever algorithm: it coordinates form, pitch, rhythm,
harmony, motif, generation, selection, revision, bass, texture, sound, and
performance. Chapter 35 audits what authorship claims
this record supports.

## Bridge forward

The canonical piece exists and must not be recomposed to explain itself. Chapter 35 reads its stored provenance and decision records to audit what can—and cannot—be claimed.
