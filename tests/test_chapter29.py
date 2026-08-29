import json

import pytest

from composition_lab.blues import (BASELINE_DEGREES, MINOR_BLUES, bar_start_beat,
    blues_bass_pitches, ending_variation, generate_blues_phrase,
    shuffle_eighth_onsets, straight_eighth_onsets, twelve_bar_degrees)
from composition_lab.chapter29 import (PLAYBACK_LAYERED, PLAYBACK_SINE, build_blues_study,
    chord_tone_flags, write_blues_artifacts)
from composition_lab.chords import DOMINANT_SEVENTH, dominant_seventh
from composition_lab.osc import build_osc_schedule


def test_dominant_seventh_and_vocabulary():
    assert DOMINANT_SEVENTH == (0, 4, 7, 10)
    assert dominant_seventh(60) == (60, 64, 67, 70)
    assert MINOR_BLUES == (0, 3, 5, 6, 7, 10, 12)


def test_form_duration_and_bar_mapping():
    assert twelve_bar_degrees() == BASELINE_DEGREES
    assert tuple(bar_start_beat(i) for i in range(1, 13)) == tuple(range(0, 48, 4))
    study = build_blues_study()
    assert study.beats == 96 and len(study.degrees) == 24
    assert study.degrees[11] == 5  # turnaround into chorus two


def test_shuffle_grid():
    assert straight_eighth_onsets() == (0, .5)
    assert shuffle_eighth_onsets()[1] == pytest.approx(2 / 3)


def test_phrase_constraints_transform_and_determinism():
    a = generate_blues_phrase(seed=2026)
    assert a == generate_blues_phrase(seed=2026)
    assert max(e.start + e.duration for e in a) <= 8
    assert all((e.pitch - 60) % 12 in set(MINOR_BLUES[:-1]) for e in a)
    varied = ending_variation(a)
    assert varied[:-1] == a[:-1] and varied[-1].pitch == a[-1].pitch + 3
    assert build_blues_study() == build_blues_study()


def test_bass_transposition_and_harmony_context():
    c, f, g = (blues_bass_pitches(root) for root in (36, 41, 43))
    assert tuple(p + 5 for p in c) == f
    assert tuple(p + 7 for p in c) == g
    motif = (60, 63, 65, 67, 70)
    assert chord_tone_flags(motif, dominant_seventh(60)) != chord_tone_flags(motif, dominant_seventh(65))


def test_playback_map_does_not_change_symbolic_composition(tmp_path):
    study = build_blues_study()
    a = build_osc_schedule(study.events, study.layers, bpm=study.bpm, playback_by_layer=PLAYBACK_SINE)
    b = build_osc_schedule(study.events, study.layers, bpm=study.bpm, playback_by_layer=PLAYBACK_LAYERED)
    assert tuple(group.beat for group in a) == tuple(group.beat for group in b)
    paths = write_blues_artifacts(study, tmp_path)
    assert all(path.exists() for path in paths)
    assert json.loads((tmp_path / "chapter_29_manifest.json").read_text())["beats"] == 96
