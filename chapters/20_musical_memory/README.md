# Chapter 20 — Musical Memory

> How can a generative system make future musical choices depend on what has
> happened before?

```bash
python -m composition_lab chapter-20
```

```text
SEQUENCE → STATE → HISTORY → TRANSITION → CONDITIONAL PROBABILITY
→ MUSICAL MEMORY
```

Chapter 19 chose each scale degree independently. Here the current scale degree
is a **state**, adjacent observations are **transitions**, and their integer
counts become selection weights. From `1 2 3 2 1`, the transparent pairs are
`1→2, 2→3, 3→2, 2→1`. For each current state:

```text
P(next | current) = transition count / total outgoing transition count
```

The nested dictionary of integer counts remains canonical; normalized
probabilities are an inspector view. Training is deterministic. Generation
alone consumes a caller-owned `random.Random`, so equal model, seed, start, and
length reproduce an equal tuple without mutating the table.

## First-order memory and dead ends

A first-order model consults only the current state. If state 2 was reached from
1 in one place and 5 elsewhere, its next draw combines all successors of 2; it
has forgotten the earlier state. This is local statistical memory, not phrase,
motif, harmonic, intentional, emotional, or stylistic understanding.

A single observed successor has probability 1.0. Direct selection from an
unseen or terminal state raises `DeadEndError`. Full-sequence generation uses a
named policy: `stop` returns the generated prefix; `restart` inserts the original
start state and continues. Neither silently substitutes uniform randomness.
Linear training does not give the final state an outgoing edge. Optional cyclic
training adds `last → first`, an explicit and useful decision for loops.

## What is represented matters

The main tables contain scale degrees, not absolute pitches. Thus one generated
state tuple is rendered in C and F major without retraining. The same generic
helpers also accept duration states. The first rhythm experiment fixes note
count rather than pretending a Markov chain naturally fits an exact beat span.
Pitch and duration use independent RNG streams: pitch knows no rhythmic context,
and rhythm knows no pitch context.

The listening studies compare source and generated sequences, independent and
transition-conditioned randomness, overall state-frequency and transition
models, seeds 10/20/30, C/F realizations, linear/cyclic training, fixed-pitch
rhythm models, and raw/constrained output. These are controlled descriptions,
not claims that one output is better.

## Boundaries and constraints

Concatenating `(1, 2)` and `(4, 5)` invents `2→4`.
`build_transition_counts_from_sequences` learns `1→2` and `4→5` separately,
preserving phrase boundaries.

Learned probabilities do not guarantee a tonic ending, pitch range, or maximum
leap. The constraint experiment therefore uses Chapter 19's bounded rejection
pattern:

```text
MARKOV GENERATOR → CANDIDATE → EXPLICIT RULES → ACCEPT OR TRY AGAIN
```

Attempts are reported and capped. This is learned probability plus explicit
rules, not harmony-aware learning. A degree model does not know the active chord.

## Capstone

Three short, hand-authored phrases train one boundary-aware cyclic model. Master
seed 2026 generates constrained A, A', and B sections; the final A is a literal
return. Fixed harmony and A A' B A form prevent local randomness from deciding
the entire piece. Seed 2027 changes only exploration. Reports expose each start,
state tuple, attempt count, and validation result.

## Reader experiments

1. Change training while holding seed fixed; then hold training and change seed.
2. Repeat one transition, remove one, and inspect conditional probabilities.
3. Render one degree sequence in C and F.
4. Compare linear and cyclic tables, then STOP and RESTART policies.
5. Add a phrase with boundary-aware training.
6. Train durations separately and keep note count fixed.
7. Tighten maximum leap or ending rules and observe rejection attempts.
8. Compare generated and source phrases: which local motions remain, and which
   larger structures disappear?

## Deliberate boundary

This chapter implements only a first-order discrete Markov model with small
symbolic states. It does not implement second/higher order or variable-order
models, n-grams, hidden or hierarchical states, recurrent networks,
transformers, embeddings, machine-learning dependencies, corpora, MIDI
ingestion, combined pitch/rhythm/harmony states, generalized evaluation,
aesthetic scoring, SuperCollider, OSC, or Chapter 21.

## Bridge forward

A memory model proposes material; it cannot tell us what the result is like or what a listener should prefer. Chapter 21 adds descriptive metrics while reserving judgment for people.
