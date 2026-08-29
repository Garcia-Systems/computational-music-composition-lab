# Chapter 35 — What Did the Computer Actually Compose?

## 1. The final question

This final chapter creates no music. It audits Chapter 34's canonical **Converging Paths** from its deterministic builder and asks narrower, observable questions: who chose a pitch, who selected a candidate, what was transformed, and what merely followed from a rule?

## 2. The piece we are auditing

The evidence is the Chapter 34 brief, seven-section score (Intro, A, A', B, Development, A return, Coda), candidate pools, decision ledger, provenance, harmony, playback map, and OSC schedule. Run:

```bash
python -m composition_lab chapter-35
```

Missing output files are harmless because the same pure Chapter 34 builder reconstructs the evidence.

## 3. Generated versus transformed versus derived

- **Generated**: an algorithm chooses among multiple musically possible symbolic outcomes.
- **Transformed**: an existing source changes by an explicit operation.
- **Derived**: a result follows mechanically from a selected representation or rule.
- **Selected**: an actor chooses among alternatives already present.
- **Revised**: an actor deliberately edits a selected result.
- **Arranged**: existing material is distributed across layers, registers, entrances, and textures.
- **Synthesized**: an engine makes the audio signal.
- **Performed**: events are executed through time.

Thus `generated ≠ selected`, and candidate existence does not mean score inclusion.

## 4. The decision ledger

The human authored the brief, C-major framework, form, motif, harmony, constraints, texture, playback, selections, revision, and stopping point. The algorithm generated B proposals and executed transformations. Derived code instantiated many events. Counts of these records do not measure creative importance.

## 5. Section-by-section audit

| Section | Evidence-based classification |
|---|---|
| Intro | Human motif fragment; derived bass |
| A | Human motif; derived accompaniment |
| A' | Algorithm-transformed motif; human selection |
| B | Algorithm-generated pitches/rhythms; human selection and one-event revision |
| Development | Deterministic transformations of the human motif |
| A return | Human-directed return and register transformation |
| Coda | Human-directed closure using an augmented fragment |

## 6. Candidate generation and rejection

A' retains three deterministic transformation candidates. B retains six valid seeded constrained-random-walk candidates. Rejected alternatives document exploration but do not enter the final score. A seed reproduces a path through an algorithm; it does not explain the rules that made that path possible.

## 7. Human selection

The algorithm proposed exact candidate content; recorded human authority selected `a-prime-candidate-02` and `b-candidate-04`. Selection does not erase algorithmic contribution, while algorithmic proposal does not grant final authority over survival.

## 8. Human revision

`revision-b-01` changes the selected B candidate's last event to begin at local beat 22 and last two beats. The JSON preserves the exact before/after diff. One event changed; the phrase was not wholly rewritten.

## 9. Developmental provenance

```text
motif-a [human]
├── A' rhythmic variation [algorithm transformation; human selected]
├── development fragment → sequence → diminution + inversion
├── A return [octave transposition]
└── coda [fragmentation + augmentation]
```

The computer transformed this material; it did not invent its motif source.

## 10. Arrangement

The human chose layer entrances, density, registers, roots-and-fifths bass, and the pulse/backbeat recipe. Code placed bass and groove events mechanically. Chapter 34 does not perform a voice-leading search: authored degrees index fixed chord voicings, so exact chord pitches are derived rather than algorithmically selected among inversions.

## 11. Sound and performance

| COMPOSITION | PLAYBACK / SOUND |
|---|---|
| pitch, rhythm, harmony, form, motif, bass, texture | instrument, oscillator, envelope, filter, pan, reverb, OSC transport |

The Python renderer did not compose notes; it turned finalized events into samples. SuperCollider generates audio-rate samples. OSC carries instructions, not the waveform or score authorship.

```text
COMPOSITION → PERFORMANCE → SOUND
AUTHORSHIP / PROVENANCE = who or what made decisions at each stage
```

## 12. Counterfactuals

A stored alternate B candidate changes only B. Removing the revision restores the selected candidate's raw state. Changing playback pan leaves every symbolic event identical. These analytical comparisons never overwrite Chapter 34.

## 13. What we can honestly claim

The algorithm materially chose B candidate pitches and rhythms and executed motif transformations. The human designed the possibility space, authored substantial source and structural material, selected proposals, revised B, arranged the result, and declared it finished. The result is not accurately summarized as entirely human-written or autonomously computer-composed.

## 14. What we still cannot measure

Provenance is only as complete as its records; informal reasons may be absent. This representation omits embodied gesture, microtiming, cultural meaning, and listener experience. No metric here establishes beauty, originality, emotion, meaning, or artistic success. Structural metrics can describe the piece, and provenance can explain its construction, but neither replaces listening.

## 15. The end of the laboratory

| Chapters | Main question |
|---|---|
| 0–3 | How does music become data? |
| 4–17 | How can structure be represented and transformed? |
| 18–21 | How can algorithms generate and describe possibilities? |
| 22–25 | How do symbolic events become sound? |
| 26–28 | How can compositions be performed computationally? |
| 29–32 | How do these tools behave in compositional models? |
| 33 | Who decides what? |
| 34 | Can the system create one complete piece? |
| 35 | What did the computer actually compose? |

```text
                     HUMAN
                       │
             intention / selection
                       ▼
              COMPOSITION RULES
                       ▼
                 ALGORITHM
         ┌─────────────┼─────────────┐
         ▼             ▼             ▼
     generation   transformation   derivation
         └─────────────┼─────────────┘
                       ▼
                SYMBOLIC SCORE
                       │ human revision
                       ▼
                  FINAL SCORE
                       ▼
                  PERFORMANCE
                       ▼
                     SOUND
                       ▼
                   LISTENING
                       └────→ revision / new intention
```

The computer did not simply compose everything, nor did the human merely operate a tool. The finished work arose through inspectable intentions, constraints, proposals, transformations, selections, revisions, and performances—the laboratory lets those relationships remain visible.

## Bridge forward

The curriculum ends here. Its final result is not an authorship percentage but a repeatable practice: preserve intentions and decisions, inspect the data, listen to the sound, and revise with honest limits.
