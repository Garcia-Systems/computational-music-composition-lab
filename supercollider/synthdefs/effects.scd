// Chapter 25 wet-only send/return effects. All buses are stereo.
(
SynthDef(\simpleDelayFx, { |inBus = 0, out = 0, delayTime = 0.25,
    feedback = 0.35, amp = 0.35|
    var input = In.ar(inBus, 2);
    var previous = LocalIn.ar(2);
    var delayed = DelayC.ar(input + (previous * feedback.clip(0, 0.8)), 2,
        delayTime.clip(0.001, 2));
    LocalOut.ar(delayed);
    // No input is added here: this return is processed (wet) audio only.
    Out.ar(out, delayed * amp.clip(0, 0.5));
}).add;

SynthDef(\simpleReverbFx, { |inBus = 0, out = 0, room = 0.5,
    damp = 0.4, amp = 0.3|
    var input = In.ar(inBus, 2);
    // mix=1 makes the return wet-only; source synths provide the dry path.
    var wet = FreeVerb.ar(input, mix: 1.0, room: room.clip(0, 1), damp: damp.clip(0, 1));
    Out.ar(out, wet * amp.clip(0, 0.5));
}).add;
)
