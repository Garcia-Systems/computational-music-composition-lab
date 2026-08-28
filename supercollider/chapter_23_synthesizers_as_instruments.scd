// Chapter 23 — Synthesizers as Instruments
// Evaluate numbered blocks in order; stop each comparison before the next.

// 1. Boot, wait for ready, then 2. load definitions relative to this script.
s.boot;
(
~projectRoot = PathName(thisProcess.nowExecutingPath).pathOnly.dirname;
(~projectRoot +/+ "supercollider/synthdefs/basic_instruments.scd").load;
~instrumentDefs = (sine: \simpleSine, saw: \simpleSaw, pulse: \simplePulse,
    two_partial: \twoPartial, detuned_saw: \detunedSaw);
~playNote = { |instrument = \simpleSine, freq = 440, duration = 1, amp = 0.08, extras = #[]|
    var voice = Synth(instrument, [\freq, freq, \amp, amp, \gate, 1, \pan, 0] ++ extras);
    SystemClock.sched(duration, { voice.set(\gate, 0); nil });
};
)

// 3. Direct waveform comparison: same A4 and safe amplitude. Free each first.
x = { SinOsc.ar(440, 0, 0.08) }.play; x.free;
x = { Saw.ar(440, 0.08) }.play; x.free;
x = { Pulse.ar(440, 0.5, 0.08) }.play; x.free;
// Equal amplitude parameters do not guarantee equal perceived loudness.
// This is an approximate listening comparison, not loudness calibration.
~playNote.(\simpleSine); ~playNote.(\simpleSaw); ~playNote.(\simplePulse);

// 4. Pulse width: only width changes (50%, 25%, 10%). No PWM modulation.
Routine({ [0.5, 0.25, 0.1].do({ |width| ~playNote.(\simplePulse, 440, 1, 0.07, [\width, width]); 1.25.wait; }); }).play;

// 5. Harmonic mixture: 440 only, then 440 + an 880-Hz partial.
~playNote.(\twoPartial, 440, 1, 0.08, [\partialRatio, 2, \partialMix, 0]);
~playNote.(\twoPartial, 440, 1, 0.08, [\partialRatio, 2, \partialMix, 0.3]);
// Try ratios 2, 3, 4 and mixes 0.05, 0.20, 0.40 separately.

// 6. Detuning: one saw versus two safely averaged saws at 440 and 442 Hz.
~playNote.(\simpleSaw, 440); ~playNote.(\detunedSaw, 440, 1, 0.08, [\detune, 2]);

// Register: same unfiltered saw preset at A2, A3, A4, A5.
Routine({ [110, 220, 440, 880].do({ |freq| ~playNote.(\simpleSaw, freq, 0.7, 0.06); 0.9.wait; }); }).play;

// 7. Same C-E-G-C melody, no regeneration; change only SynthDef.
(
~melody = [261.625565, 329.627557, 391.995436, 523.251131];
~playMelody = { |definition| Routine({ ~melody.do({ |freq| ~playNote.(definition, freq, 0.8, 0.07); 1.wait; }); }).play; };
)
~playMelody.(\simpleSine); // wait, then repeat with each below
~playMelody.(\simpleSaw);
~playMelody.(\simplePulse);
~playMelody.(\detunedSaw);

// Same three NoteEvents; compare chord spectrum at deliberately lower per-voice gain.
Routine({ [\simpleSine, \simpleSaw, \simplePulse].do({ |def|
    [261.625565, 329.627557, 391.995436].do({ |freq| ~playNote.(def, freq, 1.2, 0.035); }); 1.6.wait;
}); }).play;
// Low register: compare the same C2 event through sine, then saw.
~playNote.(\simpleSine, 65.406391, 1, 0.07); ~playNote.(\simpleSaw, 65.406391, 1, 0.07);

// 8. Capstone dispatch. Unknown metadata warns and falls back predictably to sine.
// The explicit maps mirror the two JSON maps; change ~layerMap, not event notes.
(
~layerMap = (melody: "pulse", harmony: "two_partial", bass: "detuned_saw");
~events = JSON.parse(File.readAllString(~projectRoot +/+ "outputs/chapter_23_capstone_events.json"));
~events.do({ |event|
    var name = ~layerMap[event[\layer].asSymbol] ? "sine";
    var definition = ~instrumentDefs[name.asSymbol];
    if(definition.isNil) { ("Unknown instrument " ++ name ++ "; using sine").warn; definition = \simpleSine; };
    SystemClock.sched(event[\start] * 0.5, {
        ~playNote.(definition, event[\frequency], event[\duration] * 0.5,
            (event[\velocity] / 127) * 0.10); nil;
    });
});
)

// 9. Cleanup / emergency stop.
s.freeAll; CmdPeriod.run;
// Raw saw and pulse are intentionally unfiltered. No noise, modulation, effects,
// OSC, or Chapter 24 articulation is hidden in these examples.
