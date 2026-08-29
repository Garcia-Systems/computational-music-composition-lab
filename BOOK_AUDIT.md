# Full-Book Audit

## Executive summary

The repository contains one Python package, 36 chapter directories (`00`–`35`), five chapter-specific SuperCollider scripts (`22`–`26`), a concise SuperCollider guide, a `unittest` suite, and a Git-ignored generated-output workspace with committed Chapter 35 examples. No Chapter 36 or additional Part was added.

The audit found no broken pitch/frequency formula, duration summation error, live scheduler duration chaining, process-randomized seed derivation, mutable `NoteEvent`, aesthetic scorer, or unsupported authorship percentage. The highest-value weaknesses were editorial and navigational: the root README omitted Part I–VI boundaries and four final commands, chapter endings frequently described the *next* chapter as “unimplemented” rather than motivating it, recurring vocabulary lacked one reference point, and the CLI duplicated its chapter range in an opaque `choices` tuple with no listing or static verification path. These issues were repaired and verified without expanding the curriculum.

## Findings by priority

### Critical issues found

No critical defect remained after executing all 36 default chapter commands and the automated suite. The renderer already rejects invalid durations, frequencies, sample rates, BPM, and negative event starts; computes score duration from the latest end; preserves silence; mixes polyphony with conditional headroom; and clips floating samples safely at PCM conversion.

### High-priority issues found

| Issue | Why it mattered | Fix | Verification |
|---|---|---|---|
| Root navigation did not represent all ten Parts or list Chapters 32–35 commands | A new reader could not see the intended whole-book progression or reliably discover the ending | Rebuilt the front door around setup, architecture, experimental method, ten Parts, all commands, audio, limits, and completion status | Link/structure checks plus `chapters` and `verify-book` |
| Chapter boundaries used historical “not implemented” status language | Individually correct chapters read like an unfinished serial rather than a completed progression | Added an explicit, honest bridge to every chapter and replaced the clearest stale status claims | 36 `Bridge forward` sections; chapter 35 closes rather than inventing a successor |
| Core distinctions were dispersed | Terms such as beat/seconds, pitch/frequency, root/bass, validation/evaluation, and generation/selection could drift in the reader's memory | Added a deliberately concise book-specific glossary and linked it from the README | Terminology search and manual cross-chapter review |
| CLI curriculum registration was hard to inspect and easy to truncate in documentation | A long literal choices tuple obscured whether the book registered exactly 00–35 | Added one ordered title/command registry, `chapters`, `verify-book`, and successful no-argument help | New tests assert exact range, listing, help, missing-file reporting, and current structure |

## Curriculum coherence

| Part | Question | New abstraction | Audible outcome | Why the next Part follows |
|---|---|---|---|---|
| I — Music Becomes Data | How can pitch and time become inspectable? | Immutable beat-based `NoteEvent` | Frequencies, rhythms, rests, overlap | Events need musical organization |
| II — Building Musical Ideas | How do events become directed ideas? | Scale degree, melodic profile, motif, phrase | Controlled pitch and transformation studies | Phrases gain another dimension when pitches sound together |
| III — Harmony | How do simultaneous pitches move and support melody? | Chord, progression, function, voicing, harmonic span | Root-position/voice-led and melody/harmony comparisons | Harmony needs rhythmic and registral roles |
| IV — Rhythm, Bass, Texture | How do layers coordinate? | Groove grid, bass role, texture layer | Layered arrangements | Arranged passages need development and form |
| V — Form and Composition | How do local ideas create larger possibilities? | Passage relationship, section plan, constraint space | Repetition/contrast/form studies and valid candidates | Large spaces need reproducible exploration and description |
| VI — Generative Composition | How can alternatives depend on chance and history without hiding decisions? | Local RNG, first-order transition model, descriptive report | Same-rule/different-seed and memory studies | Symbolic results invite a dedicated sound engine |
| VII — SuperCollider | What changes when synthesis becomes a separate playback layer? | SynthDef, envelope/filter control, bus/send routing | Same-score timbre, articulation, and space comparisons | Prepared files do not support a live control relationship |
| VIII — Python Meets SuperCollider | How do symbolic decisions reach live sound, before or during performance? | OSC schedule, complete-score engine, online region state | Dry-run schedules and optional live performances | Infrastructure can now be tested in contrasting compositional models |
| IX — Style Labs | How does shared infrastructure behave under different organizing logics? | Limited style/process recipe | Blues, rock, classical-style, and minimalist studies | Different recipes expose responsibility and authorship questions |
| X — Capstone | Who decides, and what can the record support? | Decision ledger and provenance audit | One canonical piece and its audit | The curriculum closes with evidence, listening, and revision |

## Pedagogical continuity and documentation

Every Chapter N → N+1 transition now identifies an unresolved problem or, at real conceptual pivots, names the change honestly. In particular, Chapter 28 → 29 stops infrastructure work and begins model testing; the style-lab transitions do not imply a ranking of genres; Chapter 32 → 33 moves from mechanisms to responsibility; and Chapter 34 → 35 explicitly audits the stored canonical result rather than recomposing it.

The root README now states prerequisites from `pyproject.toml`, distinguishes dry-run Python from optional SuperCollider, explains buffered PCM and DAC playback without suggesting per-sample speaker calls, locates generated artifacts, and retains the central question, three-layer architecture, provenance layer, listening loop, limitations, and curriculum-complete statement. SuperCollider documentation now maps Chapters 22–26 and states `sclang`/`scsynth`, boot/load/stop order, ADSR sustain-level semantics, reciprocal-Q behavior, pan direction, bounded effects, and OSC's control-only role.

## Code architecture and correctness

The package already separates symbolic representation, transformations, analysis, generation, composition assembly, playback configuration, OSC transport, style recipes, and provenance. Historical duplication in early chapter runners remains **pedagogical repetition**; aggressively routing Chapter 0 through late event abstractions would erase the progression. No generic plugin/discovery framework or `utils.py` dumping ground was introduced.

The code review confirmed frozen shared records and pure transformations; local `random.Random` use; SHA-based stable seed derivation instead of `hash()`; deterministic JSON ordering/records; half-open harmonic spans; monotonic absolute-target OSC scheduling; same-onset grouping; beat-to-second conversion at transport boundaries; and non-live defaults. The transparent CLI still maps each later command directly to `run_chapter_XX`; the registry centralizes only curriculum identity and structural checks.

## Testing and execution

- Structural verification checks exactly one ordered README for every chapter `00`–`35`, required root files, and Chapter 22–26 `.scd` scripts. It performs no rendering, sleeping, networking, or live audio.
- All 36 default chapter commands were executed. Representative artifacts were inspected across early WAV, structured/harmony/form data and sound, generative reports, SuperCollider bridge data, OSC dry-run schedule, style studies, canonical composition, and authorship audit.
- The documented complete `unittest` suite covers musical transformations, timing, deterministic generation, renderer safety, OSC grouping/scheduling, style distinctions, canonical composition, and provenance. CLI structural tests were added as curriculum regression support.

## Known limitations

The Python renderer remains intentionally mono and simple. SuperCollider examples are abstract synthesis studies, not acoustic instrument emulations or production mixing. Theory support is deliberately narrow (12-tone equal temperament, major/natural minor, mostly triadic tonal tools and simple meters). Percussion may use pitched proxies. Style labs cannot encode whole genres, cultural histories, performer interaction, or authenticity. Provenance records decision categories and evidence but cannot quantify creative importance.

## Future work deliberately deferred

Notation export, MIDI file/device workflows, microtonality, deeper counterpoint, orchestration, sample libraries, advanced synthesis, DAW integration, distributed timing, corpus ingestion, and ML systems are possible future experiments—not defects in the completed Chapters 0–35 curriculum. They were not added as scattered TODOs or a new Part.

---

**Executable textbook curriculum: complete**  
**Chapters: 0–35**
