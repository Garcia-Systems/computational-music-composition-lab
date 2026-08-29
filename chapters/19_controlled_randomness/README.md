# Chapter 19 — Controlled Randomness

> If many valid musical possibilities exist, how can randomness help us explore
> them while preserving reproducibility and compositional control?

```bash
python -m composition_lab chapter-19
```

Chapter 18 asks which candidates satisfy explicit rules. This chapter keeps that
valid set and changes only the selection strategy:

```text
VALID POSSIBILITY SPACE → RANDOM CHOICE → SEED → BOUNDED RANDOMNESS
→ WEIGHTED CHOICE → RANDOM WALK → CONSTRAINT-AWARE RANDOM GENERATION
```

The constraint system decides what is allowed. Randomness decides which allowed
possibility to explore. It does not decide which possibility is good.

## Seeds are experimental parameters

Every experiment creates a local `random.Random(seed)`. Python's generator is
pseudo-random: given the same algorithm, state, and seed, it repeats the same
sequence. The same seed therefore reproduces event tuples; seed 10, 20, or 30
can be changed while key, scale, rhythm, harmony, tempo, and constraints remain
fixed. The examples never seed implicitly from the clock.

The capstone expands one documented master seed into independent melody, rhythm,
bass, motif, and texture seeds. Adding a draw to the rhythm stream cannot silently
move the melody stream. Its manifest and every musical choice are printed.

## Selection, weights, and rules

`random_valid_candidate` selects uniformly only after Chapter 18 has enumerated
and filtered the small candidate space. An empty valid set raises the explicit
error `no valid candidates available`; it never regenerates behind the reader's
back. The CLI samples 100 times to make behavior visible without rendering 100
files. A small sample is not expected to contain equal counts.

Weighted selection uses the table C:4, D:1, E:2, F:1, G:3, A:1, B:1. These are
experimental choices, not optimal musical values. A weight changes likelihood;
a hard rule forbids or requires. Thus “C is more likely than D” differs from
“the final note must be C.” Empty tables, unequal lengths, negative weights, and
all-zero weights are rejected.

Rhythm is chosen from Chapter 18's already-valid four-beat candidates, so total
duration cannot drift. Separate pitch and rhythm streams permit changing only
one dimension. Motif choices are bounded to original, transpose +5, and
retrograde. Velocity is bounded to base 80 plus -5 through +5 and clamped to the
event range. This is bounded velocity variation, not realistic humanization.

## Proposal and rejection

Enumeration gives complete knowledge of a small space, then random selection
samples it. Rejection sampling instead proposes a candidate, checks every rule,
and repeats after a failure. The helper reports accepted candidate and attempts,
and returns an explicit failure after `max_attempts`. It cannot loop forever.
Tighter rules may increase rejected proposals, while enumeration itself can
become expensive. Neither method is universally preferable.

## Local movement

Independent random notes select every scale pitch afresh. A scale-degree random
walk selects movement relative to its current degree. At degrees 1–8 it considers
only steps that remain in that range—there is no wrapping or after-the-fact
clamping. A weighted version favors ±1 over ±2 without forbidding leaps. Upward
and downward weight tables alter probability but do not guarantee contours. The
CLI prints start, legal steps, degrees, and pitch names so the walk is reconstructible.

## Constraint-safe surface variation

Random motif transposition stays in an explicit set. Bass uses a 4:1 root/fifth
preference for later events, but the first bass event of every harmonic span is
always its root. A groove mutation remains inside one four-beat cycle. Texture
choices remain sustained, block, or broken while form stays fixed as A A' B A.
Randomness never bypasses `NoteEvent` or melody validation.

## Capstone and replay

The capstone fixes C major, A A' B A form, harmonic spans, tempo, and Chapter 18
melodic constraints. It varies a legal melody index, legal rhythm index, bounded
motif transformation, root/fifth bass continuation, and texture. Master seed
2026 renders the primary study and 2027 the alternate. Rebuilding 2026 produces
equal pitch, rhythm, bass, transformation, decision, and complete event tuples.
The seed inspector prints derived seeds, decisions, and constraint status.

```text
FORM        deterministic
HARMONY     deterministic
CONSTRAINTS deterministic
RANDOMNESS  explores local choices
```

## Controlled-randomness recipe

1. Fix context and what must not change.
2. Name dimensions that may vary.
3. Define valid choices and optional weights.
4. Set and print a seed.
5. Generate, validate, and log decisions.
6. Listen.
7. Change one parameter or seed and compare.

## Reader experiments

- Try seeds 1, 2, 3, 100, and 2026; then remove a seed and explain lost replay.
- Raise or lower tonic weight; weight steps more heavily; add repeated step 0.
- Narrow transpositions or compare mutation probabilities 0.10, 0.50, and 0.90.
- Tighten Chapter 18 constraints and inspect rejection attempts.
- Keep melody seed fixed and change rhythm seed.
- Generate several seeds and choose manually: what did you hear that the random
  generator did not understand?

A 25% variation probability does not mean exactly one of four repetitions will
change. Use deterministic structure when an exact formal pattern is required.

## Deliberate boundary

Uniform and weighted choice, seeded pseudo-randomness, bounded variation,
rejection sampling, and random walks are compositional mechanisms—not theories
of creativity. Algorithmic composition can also involve stochastic processes,
noise, cellular automata, chaos, grammars, evolutionary systems, or learned
models, but none is implemented here. There are no learned probabilities,
transition tables, Markov chains, machine learning, “AI composer,” SuperCollider,
OSC, or Chapter 20 musical memory.

## Bridge forward

Seeded choices can vary, but each choice still need not depend on musical history. Chapter 20 derives first-order transition memory from supplied sequences.
