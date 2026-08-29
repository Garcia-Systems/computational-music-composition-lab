import json

from composition_lab.chapter30 import ARRANGEMENT, FORM, PLAYBACK_RICH, PLAYBACK_SIMPLE, build_rock_song, write_rock_artifacts
from composition_lab.motifs import motif_duration
from composition_lab.osc import build_osc_schedule
from composition_lab.rock import (CHORUS_DEGREES, VERSE_DEGREES, backbeat_bar,
                                  bass_lines, four_repetitions, opening_riff,
                                  power_chord, riff_over_roots, syncopated_riff)


def test_power_chord_and_riff_span():
    assert power_chord(40) == (40, 47, 52)
    assert power_chord(40, False) == (40, 47)
    assert motif_duration(opening_riff()) == 4


def test_repetition_and_controlled_timing_change():
    riff = opening_riff()
    repeated = four_repetitions(riff)
    first_pitch_offsets = tuple(e.start for e in repeated if e.pitch == 40 and e.start % 4 == 0)
    assert first_pitch_offsets == (0, 4, 8, 12)
    syncopated = syncopated_riff(riff)
    assert tuple(e.pitch for e in syncopated) == tuple(e.pitch for e in riff)
    assert syncopated[2].start == riff[2].start + .5
    assert syncopated[5].start == riff[5].start + .5


def test_backbeat_and_bass_strategies_are_objective():
    riff = opening_riff()
    assert tuple(e.start for e in backbeat_bar()["snare"]) == (1, 3)
    lines = bass_lines(riff)
    assert tuple(e.pitch for e in lines["riff-doubling"][:len(riff)]) == tuple(e.pitch - 12 for e in riff)
    assert tuple(e.pitch for e in lines["root-following"]) == (28, 33, 37, 35)
    assert tuple(e.start for e in lines["independent"]) == tuple(range(0, 16, 2))


def test_fixed_and_harmony_adapted_riff_keep_timing_but_change_selected_context():
    riff = opening_riff()
    fixed = riff_over_roots(riff, (0, 5, 9, 7), adapt=False)
    adapted = riff_over_roots(riff, (0, 5, 9, 7), adapt=True)
    assert tuple(e.start for e in fixed) == tuple(e.start for e in adapted)
    assert tuple(e.pitch for e in fixed[:len(riff)]) == tuple(e.pitch for e in adapted[:len(riff)])
    assert adapted[len(riff)].pitch == fixed[len(riff)].pitch + 5


def test_form_reuse_hook_register_arrangement_and_determinism():
    a, b = build_rock_song(), build_rock_song()
    assert a == b
    assert tuple(s.name for s in a.sections) == FORM
    assert all(s.end - s.start == 16 for s in a.sections)
    assert a.hook_locations == ("Chorus 1", "Chorus 2", "Final Chorus")
    assert a.sections[1].harmony == VERSE_DEGREES
    assert a.sections[2].harmony == CHORUS_DEGREES
    assert {s.name: s.active_layers for s in a.sections} == ARRANGEMENT
    assert a.sections[3].riff == "A' ending"


def test_playback_maps_do_not_change_symbols_and_json_is_deterministic(tmp_path):
    study = build_rock_song()
    rich = build_osc_schedule(study.events, study.layers, bpm=study.bpm, playback_by_layer=PLAYBACK_RICH)
    simple = build_osc_schedule(study.events, study.layers, bpm=study.bpm, playback_by_layer=PLAYBACK_SIMPLE)
    assert tuple(g.beat for g in rich) == tuple(g.beat for g in simple)
    paths = write_rock_artifacts(study, tmp_path)
    first = paths[0].read_bytes()
    write_rock_artifacts(study, tmp_path)
    assert paths[0].read_bytes() == first
    assert len(json.loads(paths[0].read_text())) == len(study.events)
