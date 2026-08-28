# Chapter 10 — Harmonic Function and Tension

> Why do some chords feel stable, some transitional, and others strongly expect what comes next?

Chapter 9 could store and render `I → IV → V → I`, but it did not explain why
its positions behave differently. This chapter adds one deliberately small idea:
**function describes a chord's role in context, not merely its identity**.

```text
CHORD → PROGRESSION → FUNCTION → TENSION → RESOLUTION
```

Run the experiments with:

```bash
python -m composition_lab chapter-10
```

## Three broad regions

For **diatonic triads in a major key**, this introductory model uses:

```text
TONIC          I; vi and sometimes iii are tonic-like   stability / arrival
PREDOMINANT    ii, IV                                   departure / preparation
DOMINANT       V, vii°                                  tension / expectation
```

The caution in “tonic-like” matters. I, vi, and iii do not sound identical and
do not behave identically every time. The helper `harmonic_function(degree)` is
an explicit seven-entry mapping, not a universal analyzer. It validates degrees
1–7. `functional_path((1, 4, 5, 1))` retains the full labels; only after those
are understood does the inspector abbreviate them `T → P → D → T`.

A common functional arc is:

```text
I → IV → V → I
stability → departure → tension → resolution
home → departure → tension → return
```

This is a useful model, not a claim that all tonal music tells a literal
home-and-return story. Listen to `chapter_10_functional_arc.wav`: can you hear a
difference between departure, tension, and return?

## Function is not chord identity

Compare `I–IV–V–I` and `I–ii–V–I`. Key, duration, V, and final I remain fixed;
only the predominant changes. Can different chords serve a similar broad role
while producing different color? Then compare `I–IV–V–I` and
`I–IV–vii°–I`. V and vii° can occupy a dominant region, but they create
expectation differently and are not interchangeable in every context.

The same A-minor triad also appears after I and after V. In `I → vi`, it can
extend a tonic-like region. In `V → vi`, it avoids an anticipated tonic arrival.
The chord remains A minor; its contextual meaning changes. Does it feel different
depending on what comes before it? Isolated sonorities can be compared, but
**function becomes clearer through relationships**.

## Tension and resolution

A chord does not contain one universal numeric amount of tension. Perceived
tension depends on sequence, meter, duration, register, performance, style, and
listener. This project therefore implements no `tension_score(chord)`. Labels
and controlled listening comparisons are more honest than a fake aesthetic
number.

**Resolution occurs when a harmonically expectant event moves toward a more
stable context.** Hear equal-duration G major → C major (`V → I`) in
`chapter_10_V_to_I.wav`. Then use the shared setup `I → IV → V` and branch:

```text
A: → I    tonic resolution
B: → vi   deceptive motion to a diatonic, tonic-like destination
C: stop   unresolved dominant
```

Deceptive motion moves away from the expected tonic without leaving C major.
How does expectation change when arrival is avoided? The three
`chapter_10_resolution_*.wav` files isolate that question; the resolved and
unresolved files frame the same contrast separately.

## Functional rhythm and harmonic rhythm

A region may persist across chords: `I → vi` can prolong tonic-like behavior,
`ii → IV` predominant behavior, and `V → vii°` dominant behavior. This is a
conceptual reading, not an automated region detector. Compare the compact
`I–IV–V–I` with expanded `I–vi–ii–IV–V–vii°–I`. How does spending longer in
regions change pacing?

Duration is not function. The short-dominant and long-dominant versions preserve
I, IV, V, and I while V lasts one or four beats. Does delayed resolution change
expectation? Root-position voicings make the experiment inspectable and their
jumps audible. We deliberately do **not** optimize individual voices; that is
Chapter 11's question.

## Function and phrase

The functional phrase reconnects Chapter 7's shape with harmony:

```text
OPENING       tonic region
CONTINUATION  predominant region
CLIMAX        dominant region
CLOSING       tonic return
```

A short melody and the four equal harmonic regions share one timeline in
`chapter_10_functional_phrase.wav`. The dominant-area melody reaches degree 7
before the closing tonic. This only asks how melodic and harmonic closure can
reinforce one another; it does not perform chord-tone analysis.

## Reader experiments

1. Replace IV with ii while keeping every other variable fixed.
2. Replace V with vii° and compare dominant-region color.
3. Delay tonic by holding V longer.
4. Remove tonic and stop on V.
5. Replace `V → I` with deceptive `V → vi`.
6. Expand tonic with `I → vi → I` before departure.
7. Expand predominant with `ii → IV` before V.
8. Expand dominant with `V → vii° → I`.
9. Keep the functional-phrase melody unchanged while altering harmony beneath it.

## Analytical and historical restraint

Functional labels describe a common tonal relationship model. They do not
automatically determine emotion, quality, beauty, historical style, or listener
response. Tonic–predominant–dominant thinking applies more readily to some
traditions than others. Harmony can instead be modal, blues-based, chromatic,
nonfunctional, pedal-based, static, planed, quartal, rhythmically driven, or
ambiguous.

No seventh-chord survey, secondary dominants, modulation, chromatic harmony,
jazz-functional system, probability, voice-leading optimization, SuperCollider,
or OSC is introduced. Chapter 11 is not implemented.

## Listening artifacts

The command renders the functional arc; IV/ii and V/vii° alternatives; V–I;
resolved, deceptive, and stopped branches; A minor in two contexts; compact and
expanded arcs; short and long dominants; and the melody-plus-harmony functional
phrase. All use deterministic sine rendering and simple root-position triads.
