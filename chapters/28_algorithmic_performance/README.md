# Chapter 28 — Algorithmic Performance

## Central question

What changes when a composition engine generates controlled musical decisions
while a performance is underway instead of completing the score first?

Offline generation creates and inspects a complete score before playback.
Online generation creates only a near-future region, schedules it, updates its
musical memory, and repeats. Neither architecture is inherently preferable: they
answer different compositional and engineering needs. Here, **bounded
improvisation** means that live choices remain inside human-authored scale,
register, leap, rhythm, harmony, texture, form, and duration boundaries. This is
not free improvisation.

```text
PerformancePlan + PerformanceState
→ decide next four-beat GeneratedRegion
→ Chapter 26 /note schedule
→ update musical state
→ repeat until beat 32
```

The immutable `PerformancePlan` holds 108 BPM, 32 total beats, eight-beat
sections, four-beat phrases, four beats of lookahead, seed 2026, tonic, and the
maximum melodic leap. The immutable `PerformanceState` contains only musical
memory: timeline/section/phrase position, last pitch, recent and stored A motifs,
and generation step. It never contains sockets, clocks, threads, or audio.

## Hybrid performance

Form `A | A' | B | A`, harmony, bass, layer entrances, tempo, and texture are
preplanned. Melody notes, a finite rhythm pattern, and bounded motif behavior are
chosen phrase by phrase. A single `random.Random(seed)` stream continues through
all phrases; it is never reseeded. A' transforms stored A material, B requests
new material and a more active rhythm subset, and final A returns stored A
material with bounded placement. The generator is a cheap scale-constrained
random walk rather than exhaustive search.

All placed events use absolute performance beats. Adjacent regions cover
`0–4, 4–8, …, 28–32` without moving the authoritative grid for synthesis release
tails. The same origin is used by live OSC scheduling; SuperCollider still
decides only how `/note` messages sound.

## Lookahead, clocks, and deadlines

Lookahead is future material prepared early. It is not the delay between a
control message and audible sound, and it does not provide hard real-time
guarantees. Simulation uses numeric virtual decision beats and never sleeps.
Live mode uses one monotonic performance origin and converts every absolute beat
to a target time, so a late decision does not start a new phrase clock or shift
the remaining grid.

Synthetic generation costs can model a deadline miss without waiting. A missed
deadline or impossible candidate set selects a deterministic safe region: repeat
the previous valid motif, or use a tonic phrase if none exists. The trace records
the cause and fallback. This illustrates why a slow offline exhaustive search
may be unsuitable for a short live deadline without building a real-time system.

## Reproducibility and records

```bash
python -m composition_lab chapter-28
python -m composition_lab chapter-28 --seed 2026 --lookahead 4
python -m composition_lab chapter-28 --replay
python -m composition_lab chapter-28 --live
```

The default command is an instantaneous, audio-independent simulation. It writes:

- `outputs/chapter_28_decision_trace.json`: factual rhythm, motif, candidate,
  choice, fallback, target-beat, decision-beat, and state-transition records.
- `outputs/chapter_28_performance_events.json`: the complete symbolic event
  history that exists only after generation finishes.
- `outputs/chapter_28_manifest.json`: seed, tempo, duration, lookahead, phrase
  size, form, strategies, and scripted controls.
- `outputs/chapter_28_reference.wav`: an offline rendering of that exact event
  history, not a second generator run.

Seed replay requires the same algorithm and random-call sequence. Trace replay
loads recorded events and is therefore the stronger historical record if code
later changes. The seed helps recreate decisions; the decision trace records
what happened; event history records what music ultimately existed.

`--live` requires the Chapter 26 receiver and a booted SuperCollider server; it
does not launch either. The same generated regions and `/note` payload conversion
are used in simulation and live operation. No concurrency, MIDI, GUI, tempo
ramps, live reharmonization, neural memory, unbounded generation, or style rules
are introduced. Those boundaries keep this chapter focused on state continuity,
deadlines, failure recovery, traceability, and the intentional deferral of some
compositional decisions. Chapter 29 is deliberately not implemented here.
