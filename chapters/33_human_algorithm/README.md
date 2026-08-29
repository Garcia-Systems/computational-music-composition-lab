# Chapter 33 — Human + Algorithm

> If the computer can generate, transform, evaluate, arrange, synthesize, and
> perform musical material, which decisions should remain with the human
> composer and which should be delegated to the algorithm?

Part X stops asking what the computer *can* do and asks how those capabilities
should be used in a compositional process:

```text
INTENTION → CONSTRAINT → GENERATION → LISTENING → SELECTION → REVISION → REPEAT
```

This is a generative loop, not an optimization loop. There is no aggregate
fitness, quality metric, or automatic “best” candidate. **VALID ≠ PREFERRED.**

## Four kinds of decision

| Category | Meaning | Examples |
|---|---|---|
| `human` | Deliberate authored choice | goal, key, form, constraints, finishing |
| `algorithm` | Choice inside human-authored boundaries | random walk, rhythm vocabulary |
| `human_selected_algorithm_candidate` | Algorithm proposes; a recorded human choice accepts | B phrase, A' transformation |
| `derived` | Mechanical transformation | bass instantiation, placement, frequency/OSC conversion |

Decision provenance records where an observable design choice came from, what
alternatives existed, which constraints governed it, and whether acceptance was
automatic or human. It is program-level provenance—not hidden reasoning.

## Authored brief and delegation

The 32-beat C-major **A B A'** study starts with a human-authored A motif. Its
brief translates “moderate rhythmic activity” into the explicit rule “1–2
attacks per beat”; the computer does not understand the vague phrase. Four
stable B candidates share range, duration, harmony, ending, and maximum-leap
constraints. SHA-256 derives each `candidate-01` … `candidate-04` seed from the
master seed. Chapter 21-style range, interval, repetition, density, and harmonic
alignment measurements describe them but never select one.

The default recipe records `candidate-03` as a stand-in for a human selection
made during the authored experiment. It does **not** infer preference. Rejected
valid candidates remain in the candidate artifact. A direct authored edit
changes the approach to the final tonic. Then “make the ending less active” is
explicitly translated into fewer attacks and longer durations; the algorithm
proposes three endings, and a second recorded human selection accepts one.

The bass strategy, groove recipe, arrangement plan, and playback map are human
choices. Instantiating events, placing sections, converting MIDI pitch to
frequency, converting beats to seconds, and constructing OSC payloads are
derived operations. Playback occurs only after the symbolic score is finalized.

Delegation is granular: it can occur at the note, motif, phrase, section, form,
arrangement, or sound level. The main study's matrix makes that allocation
concrete:

| Decision | Human | Algorithm | Derived |
|---|:---:|:---:|:---:|
| Key, form, harmony | ✓ | | |
| A motif | ✓ | | |
| B phrase proposals | constraints | ✓ | |
| B and A' acceptance | ✓ | proposes | |
| Bass | strategy | | events |
| Groove | recipe | | events |
| Instrumentation | ✓ | | |
| OSC conversion | | | ✓ |

A controlled 4-bar exercise can expose the same distinction three ways:
Version H specifies every note; Version A lets the algorithm choose notes inside
human constraints; Version M retains algorithmic proposals and records a human
selection. The chapter compares only counts of provenance categories—not the
quality or creativity of the results. On the broader delegation spectrum, a
human-heavy score specifies form, harmony, melody, bass, and groove; a mixed
score delegates melody proposals, bass derivation, and variation; an
algorithm-heavy score chooses form, harmony, and melody only from finite
human-authored vocabularies. The last case is bounded system output, not
autonomous art. Autonomy is not binary.

```text
Composition Brief
├── Form and harmony [human]
├── A motif [human]
├── B candidates [algorithm]
│   └── candidate-03 [human-selected] → factual revision [human]
├── A' transformations [algorithm]
│   └── register variation [human-selected]
└── Bass, groove placement, OSC schedule [derived]
```

## Run and inspect

```bash
python -m composition_lab chapter-33
```

The non-interactive command writes the brief, all candidates, ledger, manifest,
symbolic study, reference WAVs, and an offline OSC schedule under `outputs/`.
To perform the already-finalized score against the Chapter 26 receiver, add
`--live`; no compositional choice occurs during playback.

Reader exercise: generate and listen to every candidate, change only the
recorded selected ID, rerun, and confirm the candidate pool is unchanged. Then
change only the seed or only the maximum leap and inspect how the available
alternatives change. Choosing possibility-space rules and choosing a generator
are compositional acts; a seed has meaning only inside that design.

## Human annotation worksheet

```text
Candidate selected:
Why?

Revision requested:
What changed structurally?

What did the algorithm decide?
What did the human decide?
Would you delegate more or less next time?
```

Annotations remain separate from measured facts. Counts in the ledger are
provenance counts, never creativity percentages: one structural choice may be
more consequential than many mechanical operations, and no weighting is
invented. Constraints are not taste, metrics are not taste, provenance is not
aesthetics, and randomness alone is not intention. Even perfect provenance
cannot quantify creative importance, artistic intent, meaning, or emotion.

Chapter 33 introduces no autonomous-composer abstraction and does not implement
Chapter 34's complete-piece capstone.
