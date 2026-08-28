# Chapter 27 — The Composition Engine

A complete piece previously meant manually coordinating tempo, key, form, chords, melody, bass, groove, instruments, and output. The missing capability was not music theory but **coordination**. This chapter supplies one small, explicit pipeline rather than a universal song schema.

```text
COMPOSITION ENGINE = constructs musical events
SUPERCOLLIDER      = turns playback instructions into sound
```

The engine contains no oscillator, filter, effect, envelope, or `SynthDef`. The human remains the composer: the recipe contains human decisions about form, constraints, harmony, transformations, texture, and instrumentation. Automation handles representation, rule-bounded generation, transformation, placement, assembly, validation, export, and scheduling—not taste, meaning, emotional intention, or aesthetic judgment.

## The narrow recipe

1. Choose tempo and a MIDI tonic in major.
2. Build the fixed 8 + 8 + 8 + 8 beat `A | A' | B | A` timeline.
3. Assign `I–IV–V–I`, `I–IV–V–I`, `vi–IV–ii–V`, and `I–IV–V–I`.
4. Generate eight A notes with a local seeded random walk constrained to the scale, range, and maximum leap.
5. Make A' by moving the exact A pitches up an octave. The apostrophe is only a label; the recipe explicitly requests this transformation.
6. Generate B with a separate, derived random stream and a descending bias while retaining the key, range, and leap guard.
7. Copy A literally at beat 24.
8. Derive roots-and-fifths bass attacks from harmonic degrees with Chapter 14's function.
9. Use Chapter 11 voice leading and sustained Chapter 15 layer events for accompaniment.
10. Activate Chapter 13's deterministic groove only in A' and B.
11. Assemble immutable `MusicalLayer` values.
12. Validate objective invariants.
13. Inspect Chapter 21 descriptions without choosing a “best” melody.
14. Send the one completed `CompositionResult` to JSON, reference WAV, or OSC adapters.

A transparent engine that supports one understandable composition recipe is more useful here than a generic engine whose behavior is hidden behind configuration.

## Data and dependency direction

`CompositionSpec` is immutable intent: title, beat tempo, tonic, supported mode, explicit section recipes, seed, and small melody constraints. Generated notes never enter it. `CompositionResult` is the immutable outcome: the original spec, section coordinates, timed harmonic spans, named `MusicalLayer` values, and pedagogical trace. Layers stay separate until an adapter needs a sorted event stream.

```text
FORM
 |
 +----> HARMONY ------> BASS
 |          |
 |          +---------> ACCOMPANIMENT
 +----> MELODY
 +----> TEXTURE PLAN --> GROOVE ENTRANCES / LAYER ACTIVATION
```

```text
Scale / Key
    |
    v
Harmony ---------> Bass
    |
    v
Melody Context
Motif / Phrase ----> Melody
Form -------------> Section Placement
Groove -----------> Rhythm Layer
All Layers
    v
CompositionResult
    +----> Evaluation
    +----> JSON
    +----> Python WAV
    +----> OSC
```

Bass depends on harmony; harmony does not depend on bass. OSC depends on events; events do not depend on OSC. The pure `compose(spec)` function performs no file, audio, network, SuperCollider, sleep, or clock operation. Playback maps can change instrument and pan without changing notes or seed.

## One score, multiple boundaries

```bash
python -m composition_lab chapter-27
python -m composition_lab chapter-27 --seed 2026 --bpm 108 --tonic 60
python -m composition_lab chapter-27 --live
```

The default command prints its spec, trace, form/harmony/layer reports, provenance, and Chapter 21 melody profile; writes stable composition and manifest JSON; renders a dependency-light sine reference WAV; and writes an inspectable OSC schedule without sending it. `--live` first makes that same complete result, then sends its already-built schedule to the Chapter 26 receiver. Schedule times stay in Python; `/note` arguments remain unchanged.

The reference WAV verifies pitch and timing. SuperCollider remains the richer sound engine. Outputs share symbolic structure, not timbre, envelopes, effects, or exact audio samples. Effects remain receiver-side.

Try C/F/G tonics; seeds 10/20/30; or playback at 90/108/140 BPM. Compare Chapter 21 profiles without ranking them. Remove a layer from the existing result rather than regenerating. Replace only A' transformation, B register, the B harmony, or the maximum leap and describe the objective difference.

## Whole-book convergence

Chapters 1–3 supply pitch, time, and `NoteEvent`; 4–5 supply key and melodic description; 6–7 motifs and phrases; 8–12 harmony and voice leading; 13 groove; 14 bass; 15 layers; 16–17 development and form; 18 constraints; 19 seeded randomness; 20 memory/Markov alternatives; 21 descriptive evaluation; 22–25 rendering and sound-design boundaries; 26 OSC; and 27 integration. Existing modules remain the theory framework—the chapter orchestrates rather than rewrites them.

## Boundary with Chapter 28

Chapter 27 is strictly **specification → complete composition → perform**. It never creates new musical events during playback. Online decisions, lookahead, incremental generation, live variation, and performance state belong to Chapter 28 and are deliberately not implemented here.
