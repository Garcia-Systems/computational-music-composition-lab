// Chapter 22's deliberately small instrument blueprint.
// Frequency is calculated by Python; this definition knows no music theory.
(
SynthDef(\simpleSine, {
    |freq = 440, amp = 0.1, gate = 1, pan = 0|
    var envelope = EnvGen.kr(Env.asr(0.01, 1, 0.08), gate, doneAction: 2);
    var signal = SinOsc.ar(freq, 0, amp) * envelope;
    Out.ar(0, Pan2.ar(signal, pan));
}).add;
)
