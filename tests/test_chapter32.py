import json

import pytest

from composition_lab.events import composition_duration
from composition_lab.chapter32 import PLAYBACK, _manifest, write_process_artifacts
from composition_lab.minimalism import (accumulated_layers, additive_patterns,
    build_process_study, phase_offsets, realignment_period, rotate_sequence,
    substitute_pattern_steps, subtractive_patterns)
from composition_lab.osc import PlaybackChoice, build_osc_schedule


def test_rotation_wrap_and_negative_behavior():
    source = (1, 2, 3, 4)
    assert rotate_sequence(source, 1) == (2, 3, 4, 1)
    assert rotate_sequence(source, 4) == source
    assert rotate_sequence(source, -1) == (4, 1, 2, 3)


def test_additive_subtractive_and_substitution_are_exact():
    source = (1, 2, 3, 4)
    assert additive_patterns(source) == ((1,), (1, 2), (1, 2, 3), source)
    assert tuple(map(len, subtractive_patterns(source))) == (4, 3, 2, 1)
    target = (5, 6, 7, 8)
    for count, stage in enumerate(substitute_pattern_steps(source, target)):
        assert sum(a != b for a, b in zip(source, stage, strict=True)) == count


def test_layers_offsets_and_realignment():
    assert accumulated_layers(("A", "bass", "B")) == (("A",), ("A", "bass"), ("A", "bass", "B"))
    assert phase_offsets(5, .25, 1) == (0, .25, .5, .75, 0)
    assert realignment_period(3, 4) == 12


def test_capstone_is_bounded_deterministic_and_trace_matches_states():
    first, second = build_process_study(), build_process_study()
    assert first == second
    assert composition_duration(first.events) == first.total_beats == 64
    assert all(event.start >= 0 for event in first.events)
    assert _manifest(first) == _manifest(second)
    for previous, current in zip(first.trace, first.trace[1:]):
        assert current.previous_state == previous.new_state


def test_playback_mapping_does_not_change_composition():
    study = build_process_study()
    alternate = {layer: PlaybackChoice("saw", .5) for layer in PLAYBACK}
    build_osc_schedule(study.events, study.layers, bpm=study.bpm, playback_by_layer=alternate)
    assert study == build_process_study()


def test_artifacts_are_deterministic(tmp_path):
    study = build_process_study()
    paths = write_process_artifacts(study, tmp_path)
    assert all(path.exists() for path in paths)
    assert json.loads((tmp_path / "chapter_32_manifest.json").read_text())["randomness"] is None
