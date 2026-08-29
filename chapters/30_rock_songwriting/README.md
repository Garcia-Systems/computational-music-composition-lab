# Chapter 30 — Rock and Songwriting

> How can riffs, chord loops, groove, sectional contrast, repetition, and
> arrangement be combined into the computational skeleton of a rock song?

Rock is not a formula. Rock grew through blues, rhythm and blues, country,
gospel, and rock and roll before diversifying into many distinct histories and
practices. This compact instrumental style lab therefore examines selected
compositional devices; it does not classify a genre or measure authenticity.

The chapter starts with one original, syncopated, one-bar E-centred motif. Its
role as a **riff** comes from context: it repeats prominently, joins a groove,
accompanies other material, and identifies sections. General motif, harmony,
groove, bass, texture, form, synthesis, and OSC tools remain the engine; the
rock module supplies only a recipe.

```text
RIFF → GROOVE → CHORD LOOP → SECTION
     → VERSE / CHORUS CONTRAST → ARRANGEMENT → SONG FORM
```

Run the offline-first study with:

```bash
python -m composition_lab chapter-30
```

This writes deterministic symbolic, manifest, WAV, and OSC-schedule artifacts.
`--live` optionally sends the already-composed song through the Chapter 26 OSC
infrastructure. No SuperCollider instance is needed for normal execution or tests.

The form is Intro–Verse–Chorus–Verse–Chorus–Bridge–Final Chorus–Outro. Every
section is four bars so the 32-bar reference remains a laboratory-scale study.
Verse 2 changes one riff ending, choruses return the same instrumental hook,
the bridge repeats a riff fragment, and verse pickups demonstrate a transition.

## Reader experiments

- Change only every fourth riff ending; then move one attack by half a beat.
- Compare full triads with root/fifth power-chord voicings.
- Switch bass among riff doubling, chord roots, and independent motion.
- Remove the backbeat without changing riff or harmony.
- Change only chorus register, texture, or harmony in separate trials.
- Remove the bridge; compare timelines rather than judging either version.
- Render flat and sectional arrangements, sine and richer playback maps,
  several tempos, or a whole-song transposition while preserving the symbols.

## What This Model Does Not Capture

The event abstraction cannot represent human ensemble interaction, guitar string
and pick choices, palm muting, feedback, bends, slides, vibrato, amplifier and
speaker behavior, drum articulation and microtiming, vocal delivery, lyrics,
studio production, performer identity, historical subgenres, or cultural context.
It can count repetition and layers; it cannot know whether music is catchy,
exciting, authentic, or “rocks.” Punk, metal, progressive, indie, hard,
psychedelic, and alternative rock, jam bands, and other traditions may organize
shared devices very differently. Chapter 31's classical-style development is
deliberately not implemented here.

## Bridge forward

Riff-centered repetition is one way to create identity. Chapter 31 changes the question to how a compact motif can be transformed, harmonically redirected, and returned in a limited classical-style development study.
