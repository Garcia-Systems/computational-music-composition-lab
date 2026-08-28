// Chapter 25 — evaluate numbered parenthesized sections one at a time.
// Python writes files; this manual script deliberately does not use OSC.

// 1. Boot server.
(s.waitForBoot({ "Server ready".postln; }); s.boot;)

// 2–3. Load the routing-aware instrument and effect definitions.
(thisProcess.nowExecutingPath.dirname +/+ "synthdefs" +/+ "effects.scd").load;
// Historical SynthDefs stay unchanged.
(
SynthDef(\routedSaw, { |dryOut = 0, delayBus = 0, reverbBus = 0,
    freq = 440, amp = 0.055, gate = 1, pan = 0, delaySend = 0,
    reverbSend = 0, attack = 0.01, release = 0.25, cutoff = 1400|
    var env = EnvGen.kr(Env.adsr(attack, 0.1, 0.7, release), gate, doneAction: 2);
    var mono = RLPF.ar(Saw.ar(freq), cutoff.clip(20, 18000), 0.65) * env * amp;
    var stereo = Pan2.ar(mono, pan.clip(-1, 1));
    Out.ar(dryOut, stereo);                         // dry copy
    Out.ar(delayBus, stereo * delaySend.clip(0, 1)); // send copies
    Out.ar(reverbBus, stereo * reverbSend.clip(0, 1));
}).add;
)

// 4. Dry baseline: center pan and zero sends.
(x = Synth(\routedSaw, [\freq, 261.63, \pan, 0, \delaySend, 0, \reverbSend, 0]);
SystemClock.sched(0.5, { x.set(\gate, 0); nil });)

// 5. Controlled pan: same pitch, envelope, filter, velocity-derived amp and duration.
([-0.8, 0, 0.8].do({ |position, index|
    SystemClock.sched(index * 1.2, {
        var note = Synth(\routedSaw, [\freq, 261.63, \pan, position]);
        SystemClock.sched(0.5, { note.set(\gate, 0); nil }); nil
    });
});)

// 6–10. Allocate stereo buses and enforce sourceGroup -> fxGroup node order.
// In.ar sees writes from source synths earlier in the same server block.
(
~delayBus = Bus.audio(s, 2); ~reverbBus = Bus.audio(s, 2);
~sourceGroup = Group.head(s); ~fxGroup = Group.after(~sourceGroup);
~delayFx = Synth.head(~fxGroup, \simpleDelayFx,
    [\inBus, ~delayBus, \delayTime, 0.25, \feedback, 0, \amp, 0.35]);
~reverbFx = Synth.after(~delayFx, \simpleReverbFx,
    [\inBus, ~reverbBus, \room, 0.5, \damp, 0.4, \amp, 0.3]);
)

// 6. Single DelayC echo: feedback=0. Change delayTime among 0.1, 0.25, 0.5 seconds.
(~delayFx.set(\feedback, 0, \delayTime, 0.25);
x = Synth.head(~sourceGroup, \routedSaw,
    [\delayBus, ~delayBus, \reverbBus, ~reverbBus, \delaySend, 0.3]);)

// 7. Repeating feedback comparison: 0.2, 0.4, 0.6 are conservative.
(~delayFx.set(\delayTime, 0.25, \feedback, 0.4);)

// 8. Dry/wet comparison: keep the note fixed; use delaySend 0, 0.15, then 0.35.
// Send level changes how much enters the wet-only effect, not its internal mix.

// 9. Reverb comparison: keep send fixed and try room 0.25, 0.5, 0.75.
(~reverbFx.set(\room, 0.5, \damp, 0.4);)

// 10–11. Shared bus: melody, harmony, and bass use one persistent reverb Synth.
// At 120 BPM: 0.25, 0.5, and 1 beat equal 0.125, 0.25, and 0.5 seconds.
(
[
    [67, 0.2, 0.15, 0.30], // melody: modest right, delay, reverb
    [60, -0.3, 0.05, 0.38], // harmony: modest left, more shared room
    [36, 0.0, 0.00, 0.10]  // bass: low send is a choice, not a rule
].do({ |row|
    Synth.head(~sourceGroup, \routedSaw, [\freq, row[0].midicps, \pan, row[1],
        \delayBus, ~delayBus, \reverbBus, ~reverbBus,
        \delaySend, row[2], \reverbSend, row[3]]);
});
)

// 12. Cleanup. Effect synths persist until explicitly freed.
(
~sourceGroup.freeAll; ~delayFx.free; ~reverbFx.free;
~sourceGroup.free; ~fxGroup.free; ~delayBus.free; ~reverbBus.free;
// Emergency alternative: s.freeAll;
)
