# Chapter 11 — Voice Leading and Efficient Motion

> If the chord progression stays the same, how can the individual notes move more smoothly from one chord to the next?

```text
CHORD PROGRESSION → VOICING → VOICE → VOICE LEADING
                                  ↓
                       COMMON TONES + SMALL MOTIONS
```

Run the audible laboratory:

```bash
python -m composition_lab chapter-11
```

Chapter 9's root-position `I → IV → V → I` makes every root easy to see, but it also makes all three positions jump. Is every jump necessary merely because the root changed? A progression determines the available chord tones; it does not uniquely determine their octaves. Harmonic identity and voice-leading behavior are separate layers.

## Harmony, voicing, and a computational voice

`C4 E4 G4`, `E4 G4 C5`, and `G3 C4 E4` all contain C-major pitch classes. Their bass and register differ; a four-note form could also differ in spacing and doubling. This chapter deliberately limits itself to close-position, three-note triads and inversions.

A **voice** here is one ordered line obtained by tracking one sorted note position through successive voicings. Thus `(60,64,67)`, `(60,65,69)`, `(59,62,67)` become low `(60,60,59)`, middle `(64,65,62)`, and high `(67,69,67)`. This is an inspectable simplification: real voice identity may cross or continue more subtly than sorted low/middle/high positions imply.

`voice_movements` reports signed semitones. From `(60,64,67)` to `(60,65,69)` it reports `(0,+1,+2)`; total absolute motion is 3 and maximum individual motion is 2. Total and maximum reveal different structures—a modest total might still conceal one conspicuous leap. **Lower motion means less displacement in this model, not automatically better music.**

## Common tones are two different claims

C major and A minor share pitch classes C and E. `common_pitch_classes` ignores octave. By contrast, `stationary_common_tones` requires the same absolute MIDI pitch to remain in the same sorted voice position. G4 and G5 share pitch class G but are not stationary. A composer may preserve a common tone where register permits, but is not obliged to do so.

With several lines we can lightly describe similar motion (both signs alike), contrary motion (opposite signs), and oblique motion (one zero). These are descriptions only; the chapter imposes no counterpoint rules.

## A small visible search

For every next root-position triad, the candidate generator:

1. uses Chapter 8's root, first, and second inversion;
2. shifts each whole close-position voicing by -12, 0, or +12 semitones;
3. retains candidates in C3–C6 (MIDI 48–84);
4. scores fixed positions by total absolute movement;
5. breaks ties by maximum individual motion, lower summed register, then the pitch tuple.

For C major to F major, root position moves `(+5,+5,+5)` for 15 semitones. The nearby second inversion `C4 F4 A4` moves `(0,+1,+2)` for 3. The CLI prints every retained candidate rather than hiding the decision.

At progression level, the procedure holds a chosen first voicing and greedily chooses the nearest candidate for each following chord. It is a **greedy local optimization, not a globally optimal solution**: a locally cheapest position can constrain what happens later. Global search is intentionally deferred. A five-semitone maximum-motion budget is available as a diagnostic constraint, not an optimizer law.

## Main experiments

1. **One transition:** root-position I–IV versus the nearest F-major inversion.
2. **I–IV–V–I:** root positions total 42 semitones (`15, 6, 21`); the greedy path totals 12 (`3, 6, 3`).
3. **Individual voices:** hear low, middle, and high lines alone, and inspect them with Chapter 5 intervals, range, average interval size, and maximum leap.
4. **Common tones:** `I–vi–IV–V` lets shared pitch classes become stationary where the selected register permits.
5. **I–V–vi–IV:** the same algorithm is tested away from the primary cadence.
6. **Intentional leap:** identical I–IV harmony rejects minimum motion to create a clear registral/root-bass gesture. Smoothness is a tool, not a law; bass direction, climax, contrast, texture, expansion, and register may justify wider movement.
7. **Phrase accompaniment:** Chapter 10's melody remains unchanged over root-position and voice-led harmony. This is a texture comparison, not melody/chord-tone classification.

The smooth primary path is:

```text
I     C4 E4 G4
IV    C4 F4 A4
V     D4 G4 B4
I     E4 G4 C5
```

Its voices are `C4 C4 D4 E4`, `E4 F4 G4 G4`, and `G4 A4 B4 C5`. Meanwhile harmonic roots are `C F G C`, but sounding bass is `C C D E`. Root motion describes chord identity; bass motion describes the lowest audible line. Function remains `T → P → D → T`, independently describing what the harmonies do while voice leading describes how pitches travel.

## Reader experiments

A. Force every chord into root position.  
B. Choose one first inversion manually and hear its downstream effect.  
C. Hold a shared absolute pitch where possible.  
D. Start I in first inversion; does the greedy path change?  
E. Tighten the allowable register.  
F. Widen it by an octave.  
G. Reject the cheapest candidate for a designed gesture.  
H. Render only the middle voice; does it sound like a plausible melody?

## Deliberate limits

This is a small deterministic search under a simplified model: diatonic major-key triads, three fixed sorted voices, inversions, whole-voicing octave shifts, a finite range, and greedy choice. Real practice may use four or more voices, crossings, doublings, omissions, independent lines, tendency tones, spacing and instrumental ranges, stylistic counterpoint, registral design, and global planning.

No seventh chords, SATB rules, species counterpoint, forbidden-parallel system, modulation, SuperCollider, or OSC is introduced. Most importantly, the unchanged phrase melody is **not** classified against its chords: chord tones, non-chord tones, dissonance types, and melody/harmony alignment belong to Chapter 12 rather than this voice-leading model.

## Bridge forward

Smoother chord voices still leave the melody unanalyzed. Chapter 12 aligns each melodic event with half-open harmonic spans to describe chord-tone and non-chord-tone relationships.
