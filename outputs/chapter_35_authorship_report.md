# Chapter 35 Authorship Report: Converging Paths

## Composition
This audits the canonical Chapter 34 score and creates no new composition.

## Audit basis
The Chapter 34 pure builder reconstructs the brief, manifest data, candidates, ledger, provenance, score, playback, and OSC evidence.

## Human-authored decisions
The human authored the goal, form, C-major framework, motif, constraints, harmony, arrangement, selections, revision, and stopping point.

## Algorithm-generated material
The seeded constrained random walk preserved 6 valid B candidates and chose their exact pitches and rhythms inside a human-designed possibility space.

## Algorithmic transformations
A', Development, return, and coda use explicit transformations of motif-a. Transformation is not generation of the source.

## Derived material
Fixed chord pitches, bass/groove placement, section positioning, frequency/time conversion, velocity mapping, and OSC payloads follow selected representations or rules.

## Human selections
The recorded choices are `a-prime-candidate-02` and `b-candidate-04`. Generation is not selection; generated is not used.

## Human revisions
`revision-b-01` changes exactly 1 event; this is not a complete human rewrite.
- Event 26: `{'pitch': 60, 'start': 22.5, 'duration': 1.5, 'velocity': 88}` → `{'pitch': 60, 'start': 22, 'duration': 2, 'velocity': 88}`; properties: start, duration.

## Rejected alternatives
A': a-prime-candidate-01, a-prime-candidate-03. B: b-candidate-01, b-candidate-02, b-candidate-03, b-candidate-05, b-candidate-06. They evidence exploration, not score inclusion.

## Section-by-section audit
- **intro** — 8 beats; `motif-a-fragment`; human-authored motif fragment + mechanically-derived bass; layers: melody, bass.
- **a** — 24 beats; `motif-a`; human-authored theme + mechanically-derived accompaniment; layers: melody, harmony, bass.
- **a_prime** — 24 beats; `a-prime-candidate-02`; algorithm-transformed motif + human selection + derived accompaniment; layers: melody, harmony, bass, groove.
- **b** — 24 beats; `b-candidate-04`; algorithm-generated melody + human selection + human revision; layers: melody, harmony.
- **development** — 32 beats; `motif-a-development`; algorithm-transformed units from the human-authored motif; layers: melody, harmony, bass, groove.
- **a_return** — 24 beats; `motif-a-return`; human-directed return + algorithm-transformed register + derived arrangement; layers: melody, harmony, bass, groove.
- **coda** — 16 beats; `motif-a-augmented-fragment`; human-directed closure + algorithm-transformed augmented fragment; layers: melody, harmony, bass.

## Arrangement decisions
The human chose layer entrances/exits, density, register, bass strategy, and groove recipe; code instantiated events.

## Contribution ledger
| Component | Source | Action | Final authority |
|---|---|---|---|
| Form | brief / ledger | human-authored | human |
| A motif | motif-a | human-authored | human |
| A' variation | motif-a | algorithm-transformed | algorithm proposed; human selected |
| B candidates | seeded constrained random walk | algorithm-generated exact pitches and rhythms | algorithm proposed |
| B selection | b-candidate-04 | human-selected | human |
| B revision | revision-b-01 | human-revised | human |
| Development | motif-a | algorithm-transformed | human-designed process |
| Harmony / voicing | harmonic plan + chord table | human-authored plan; mechanically-derived pitches | human |
| Bass | roots_and_fifths | human strategy; mechanically-derived placement | human |
| Groove | quarter pulse/backbeat | human recipe; mechanically-derived placement | human |
| Arrangement | texture plan | human-arranged | human |
| Playback | playback map | human-selected / performed | human configuration |
| Audio rendering | final NoteEvents | synthesized / machine-rendered | finalized score |

## Playback / synthesis
Python renders finalized events into samples. SuperCollider generates audio-rate samples. OSC carries instructions, not waveforms. None thereby chooses the symbolic form.

COMPOSITION → PERFORMANCE → SOUND

AUTHORSHIP / PROVENANCE asks who or what made each stage's decisions.

## Lineages
### Transformation
```text
motif-a [human]
├── a-prime-candidate-02 [rhythmic transformation; human selected]
├── motif-a-development [fragmentation, sequence, diminution + inversion]
├── motif-a-return [octave transposition]
└── motif-a-augmented-fragment [fragmentation + augmentation]
```
### Generation
```text
B constrained-random-walk generator
├── b-candidate-01 [rejected]
├── b-candidate-02 [rejected]
├── b-candidate-03 [rejected]
├── b-candidate-04 [human selected → revision-b-01]
├── b-candidate-05 [rejected]
└── b-candidate-06 [rejected]
```
### Sound
```text
final NoteEvents
↓ playback configuration
↓ OSC messages / Python renderer
↓ SuperCollider SynthDefs
↓ audio samples
```

## Counterfactual comparisons
- Alternate B `b-candidate-01` changes only `b`.
- No revision restores the selected raw candidate: True.
- Alternate playback leaves symbolic data unchanged: True.

## Defensible claims
- The human authored the brief, form, tonal framework, source motif, constraints, harmonic and arrangement plans, selections, revision, and stopping decision.
- The algorithm generated the exact pitch and rhythm sequences in the B candidate pool; the selected candidate became B's basis.
- The algorithm executed deterministic motif transformations, distinct from authoring their source motif.
- The human selected one A' transformation and one B candidate, then revised the selected B ending.
- Bass, groove, chord pitches, placement, frequency conversion, and OSC payloads largely follow chosen rules mechanically.
- Rendering and SuperCollider synthesis create audio signals; OSC transports instructions; none chose the form.
- The evidence supports neither an entirely human-written score nor an autonomously computer-composed piece.

## Limitations
- Provenance only captures recorded decisions; informal reasons and preferences can be absent.
- The model covers pitch, time, duration, velocity, layers, harmony, and playback metadata—not embodied gesture, microtiming, cultural meaning, or listener experience.
- No structural metric establishes beauty, originality, emotional power, meaning, or artistic success; neither metrics nor provenance replaces listening.

Decision counts describe records, not creative importance or an authorship percentage.
