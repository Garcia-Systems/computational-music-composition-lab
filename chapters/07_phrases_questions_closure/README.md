# Chapter 7 — Phrases, Questions, and Closure

> How do small motifs become larger musical thoughts that feel like beginnings,
> continuations, questions, and endings?

```text
MOTIF → MOTIF DEVELOPMENT → PHRASE → PHRASE FUNCTION → PHRASE PAIR
```

Chapter 6 could arrange original, repeat, transpose, retrograde, augmentation,
and return. Yet several related transformations can still resemble exercises
rather than a musical sentence. Material gains meaning from placement in a
larger temporal arc. We are no longer asking only how material transforms; we
are asking how its arrangement creates direction over time.

A **phrase is a bounded musical thought containing enough internal direction to
feel like a meaningful unit**. It might contain motif, repetition, variation,
continuation, and ending behavior. It need not have one fixed length. Our
controlled studies use manageable four- and eight-measure spans.

## Four experimental roles

The complete sixteen-beat study gives regions explicit, inspectable roles:

```text
beats  0–4    OPENING       C4 D4 E4 G4; one onset per beat
beats  4–8    CONTINUATION  rising two-note fragments; two onsets per beat
beats  8–10   CLIMAX        preparation A4, then C5 at velocity 105
beats 10–16   CLOSING       descent G4 E4 D4 C4; final tonic lasts 3 beats
```

The opening clearly presents Chapter 6's motif before transforming it. Before
music can develop an idea, a listener usually needs an opportunity to hear it.
The continuation extracts `C D`, then uses Chapter 6 transposition to make
rising cells. A **fragment is a smaller recognizable piece extracted from a
motif**. Here fragmentation, reduced pauses, upward register, and increased
velocity accumulate rather than requiring a new development framework.

A climax is a local point of maximum musical emphasis. Highest pitch, velocity,
density, leap, preparation, or duration can contribute; no universal
`find_climax()` can objectively decide it. This study deliberately coordinates
density, register, and velocity at a designed high point, then descends and
slows. Chapter 5's range and motion profile verifies structural changes, but:

> Analysis describes the construction. Listening evaluates the musical effect.

Compare the flat phrase—steady register, pulse, and velocity—with the shaped
version. The motif remains basic source material. Does the shaped version make
a destination clearer? Higher does not always mean more intense; this is a
controlled compositional experiment, not a rule.

## Boundaries and closure

Listeners may infer a boundary from rests, a longer last note, rhythmic
slowdown, movement toward tonic, repetition followed by change, register
change, reduced density, a clear ending onset, or subsequent silence. No one
feature always defines a phrase. Boundary perception can be cumulative.

Closure is not simply “the song stops.” It can be explored as a musical
reduction of forward expectation. The artifacts hold their lead-in constant
and compare degree 1 (C) with degree 2 (D), then a `0.5`-beat tonic with a
`2`-beat tonic. Which sounds complete, suspended, or expectant? Responses are
not prescribed. Pitch and time both matter.

Silence is represented honestly as empty timeline space, never a fake silence
note. `place_after(first, second, gap=1)` puts the second phrase one beat after
the latest event end. Compare that boundary with `gap=0`: can silence make the
end of one thought easier to perceive? Phrase span likewise uses earliest onset
and latest event end—not the sum of durations, which would be wrong for gaps or
overlap.

## Question and answer

An introductory phrase pair calls its question-like phrase the **antecedent**
and its answer-like phrase the **consequent**:

```text
question: C D E G | F E D     (ends on degree 2)
answer:   C D E G | F E C     (ends on degree 1)
```

Opening, rhythm, register, tempo, and most pitches remain identical. How little
must change for one phrase to sound like a response? `A + A` is also rendered
beside `A + A′`. Repetition creates recognition; variation can create response.
The capstone places two related sixteen-beat arcs around two beats of actual
silence: phrase A has question-like forward momentum; phrase B returns with a
long tonic close. It remains melody, rhythm, register, density, duration,
velocity, and timing—not harmonic-function theory.

## Run the laboratory

```bash
python -m composition_lab chapter-07
```

The command prints the motif, four section positions, designed climax, Chapter
5 measurements, ending degrees, and every created WAV. The artifacts isolate
flat/shaped direction, tonic/open pitch, short/long duration, question/answer,
literal/varied pairs, a complete phrase, and the phrase-pair capstone.

## Reader experiments

1. **Remove the climax.** Flatten register and velocity. Does a destination remain?
2. **Move the climax.** Put the highest note very early, then very late.
3. **Change only final degree.** Compare `1, 2, 3, 5, 7`.
4. **Change only final duration.** Compare `.25, .5, 1, 2, 4` beats.
5. **Fragment aggressively.** Progressively shorten cells. When does development
   become agitation or lose identity?
6. **Repeat versus answer.** Compare `A + A` and `A + A′`.
7. **Remove silence.** Set the inter-phrase gap to zero. Is the boundary weaker?
8. **Try asymmetry.** Compare equal phrase spans with a four-plus-six-bar pair;
   symmetry is not inherently better, but it creates different expectations.

## Theoretical and chapter boundary

Opening/continuation/climax/closure is experimental scaffolding, not a universal
law. Phrases behave differently in classical music, blues, jazz, rock, folk,
electronic and non-Western traditions, through-composed works, and highly
repetitive music.

Chapter 8 will ask what happens when different pitches sound together. Chapter
7 deliberately adds no triads, chord roots or qualities, inversions, Roman
numerals, progressions, harmonic function, or voice leading. It also adds no
probability, SuperCollider, or OSC.

## Bridge forward

Phrase direction has so far been melodic. Chapter 8 changes perspective honestly—from pitches through time to pitches sounding together—and introduces vertical structure.
