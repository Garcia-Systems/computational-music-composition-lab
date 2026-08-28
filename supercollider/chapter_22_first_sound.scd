// Chapter 22 — From Notes to Sound
// Evaluate each parenthesized section separately in the SuperCollider IDE.

// 1. Boot the default scsynth audio server. Wait for "server ready".
s.boot;

// 2. Experiment 1: a direct graph (pedagogical, not our reusable architecture).
// SinOsc is a sine oscillator; 440 is Hz; 0.1 is conservative amplitude.
x = { SinOsc.ar(440, 0, 0.1) }.play;
x.free; // Stop this direct oscillator before continuing.

// Try 220 or 880 Hz. Separately try amplitudes 0.03, 0.1, and 0.2.

// 3. Experiment 2: reusable instrument blueprint. This is also available in
// synthdefs/simple_sine.scd. Frequency comes from Python's conversion.
(
SynthDef(\simpleSine, {
    |freq = 440, amp = 0.1, gate = 1, pan = 0|
    var envelope = EnvGen.kr(Env.asr(0.01, 1, 0.08), gate, doneAction: 2);
    var signal = SinOsc.ar(freq, 0, amp) * envelope;
    Out.ar(0, Pan2.ar(signal, pan));
}).add;
)

// A SynthDef is the blueprint; a Synth is one running server instance.
x = Synth(\simpleSine, [\freq, 440, \amp, 0.1]);
x.set(\gate, 0); // release, then doneAction 2 frees the server node

// 4. Experiment 3: C4, E4, G4 as independent simultaneous Synths.
// Multiple voices can sum, so each is deliberately quiet.
(
~chord = [261.625565, 329.627557, 391.995436].collect({ |frequency|
    Synth(\simpleSine, [\freq, frequency, \amp, 0.05]);
});
)
~chord.do({ |voice| voice.set(\gate, 0) });

// 5. Experiment 4: a manually mirrored short sequence at 120 BPM.
// Duration and wait values below are beats because the Routine uses TempoClock.
(
~clock = TempoClock.new(120 / 60);
Routine({
    [261.625565, 329.627557, 391.995436, 523.251131].do({ |frequency|
        var voice = Synth(\simpleSine, [\freq, frequency, \amp, 0.08]);
        ~clock.sched(1, { voice.set(\gate, 0); nil });
        1.wait;
    });
}).play(~clock);
)

// 6. Experiments 5 and 8: load Python's JSON and preserve absolute starts.
// Evaluate from the repository root, or change ~projectRoot explicitly.
// JSON is part of the standard class library; no Quark is required.
(
~projectRoot = PathName(thisProcess.nowExecutingPath).pathOnly.dirname;
~playExport = { |relativePath|
    var events = JSON.parse(File.readAllString(~projectRoot +/+ relativePath));
    var tempoBpm = 120;
    var clock = TempoClock.new(tempoBpm / 60);
    var grouped = events.sortBy(\start).groupBy({ |event| event[\start] });
    var onsets = grouped.keys.asArray.sort;

    ("playing " ++ events.size ++ " events from " ++ relativePath).postln;
    Routine({
        var previousOnset = 0.0;
        onsets.do({ |onset|
            (onset - previousOnset).wait; // delta between absolute beat onsets
            grouped[onset].do({ |event|
                var amp = (event[\velocity] / 127) * 0.15;
                var voice = Synth(\simpleSine, [
                    \freq, event[\frequency], \amp, amp, \gate, 1, \pan, 0
                ]);
                // Each release is independent; duration is beats on this clock.
                clock.sched(event[\duration], { voice.set(\gate, 0); nil });
            });
            previousOnset = onset;
        });
    }).play(clock);
};
)

~playExport.("outputs/chapter_22_events.json");       // melody plus chord
~playExport.("outputs/chapter_22_capstone_events.json"); // melody/harmony/bass

// Optional recording: s.record; evaluate playback; then s.stopRecording.
// 7. Cleanup / emergency stop.
s.freeAll;
CmdPeriod.run;

// Experiments: change tempoBpm to 90 or 150; overlap two start values; use
// Python-generated C-Eb-G frequencies; adjust ASR attack/release slightly.
// Ask what changed: composition, scheduling, amplitude shape, or synthesis?
