// Chapter 23's small instrument library. Evaluate after the server boots.
// Every SynthDef shares freq, amp, gate, and pan and the same fixed ASR shape.
(
SynthDef(\simpleSine, { |freq = 440, amp = 0.1, gate = 1, pan = 0|
    var env = EnvGen.kr(Env.asr(0.01, 1, 0.08), gate, doneAction: 2);
    Out.ar(0, Pan2.ar(SinOsc.ar(freq) * amp * env, pan));
}).add;

SynthDef(\simpleSaw, { |freq = 440, amp = 0.1, gate = 1, pan = 0|
    var env = EnvGen.kr(Env.asr(0.01, 1, 0.08), gate, doneAction: 2);
    Out.ar(0, Pan2.ar(Saw.ar(freq) * amp * env, pan));
}).add;

SynthDef(\simplePulse, { |freq = 440, amp = 0.1, gate = 1, pan = 0, width = 0.5|
    var env = EnvGen.kr(Env.asr(0.01, 1, 0.08), gate, doneAction: 2);
    Out.ar(0, Pan2.ar(Pulse.ar(freq, width.clip(0.1, 0.9)) * amp * env, pan));
}).add;

SynthDef(\twoPartial, { |freq = 440, amp = 0.1, gate = 1, pan = 0,
        partialRatio = 2, partialMix = 0.25|
    var env = EnvGen.kr(Env.asr(0.01, 1, 0.08), gate, doneAction: 2);
    var mix = partialMix.clip(0, 0.5);
    // 0.67 supplies simple headroom; mix crossfades rather than adding full voices.
    var signal = XFade2.ar(SinOsc.ar(freq), SinOsc.ar(freq * partialRatio), (mix * 2) - 1) * 0.67;
    Out.ar(0, Pan2.ar(signal * amp * env, pan));
}).add;

SynthDef(\detunedSaw, { |freq = 440, amp = 0.1, gate = 1, pan = 0, detune = 2|
    var env = EnvGen.kr(Env.asr(0.01, 1, 0.08), gate, doneAction: 2);
    var offset = detune.clip(0, 8);
    // Two oscillators represent one note. Average before applying amp.
    var signal = (Saw.ar(freq) + Saw.ar(freq + offset)) * 0.5;
    Out.ar(0, Pan2.ar(signal * amp * env, pan));
}).add;
)
