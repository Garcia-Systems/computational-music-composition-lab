import unittest

from composition_lab.chapter17 import BLUES_DEGREES, blues_section, chapter_17_forms, chapter_17_sections
from composition_lab.events import NoteEvent
from composition_lab.forms import Section, assemble_form, bars_to_beats


class SectionTests(unittest.TestCase):
    def test_section_normalizes_and_uses_timeline_span(self):
        source = (NoteEvent(60, 3, 2), NoteEvent(64, 4, 4))
        section = Section("A", source)
        self.assertEqual(tuple(e.start for e in section.events), (0, 1))
        self.assertEqual(section.duration, 5)
        self.assertEqual(source[0].start, 3)

    def test_plan_validation(self):
        section = Section("A", (NoteEvent(60, 0, 1),))
        with self.assertRaises(ValueError):
            assemble_form((), {"A": section})
        with self.assertRaises(ValueError):
            assemble_form(("B",), {"A": section})
        with self.assertRaises(ValueError):
            assemble_form(("A", "A"), {"A": section}, ())

    def test_assembly_reuses_source_and_reports_placements(self):
        section = Section("A", (NoteEvent(60, 2, 2),))
        assembly = assemble_form(("A", "A"), {"A": section})
        self.assertEqual([(p.label, p.start, p.end) for p in assembly.placements],
                         [("A", 0, 2), ("A", 2, 4)])
        self.assertEqual(section.events[0].start, 0)
        self.assertEqual(assembly.events[0], section.events[0])

    def test_gap_changes_next_start_and_total_span(self):
        section = Section("A", (NoteEvent(60, 0, 2),))
        assembly = assemble_form(("A", "A"), {"A": section}, (1,))
        self.assertEqual(assembly.placements[1].start, 3)
        self.assertEqual(assembly.duration, 5)

    def test_bars_to_beats(self):
        self.assertEqual(bars_to_beats(12), 48)


class Chapter17Tests(unittest.TestCase):
    def setUp(self):
        self.forms = chapter_17_forms()

    def test_named_form_orders_and_durations(self):
        expectations = {
            "binary_form": (("A", "B"), 16),
            "ternary_form": (("A", "B", "A"), 24),
            "AABA": (("A", "A", "B", "A"), 32),
            "verse_chorus": (("Verse", "Chorus", "Verse", "Chorus"), 32),
            "through_composed": (("A", "B", "C", "D"), 32),
        }
        for name, (order, duration) in expectations.items():
            self.assertEqual(tuple(p.label for p in self.forms[name].placements), order)
            self.assertEqual(self.forms[name].duration, duration)

    def test_blues_structure_and_duration(self):
        self.assertEqual(BLUES_DEGREES, ("I", "I", "I", "I", "IV", "IV", "I", "I", "V", "IV", "I", "I"))
        self.assertEqual(blues_section().duration, 48)
        self.assertEqual(self.forms["12_bar_blues"].duration, 48)
        self.assertEqual(self.forms["two_blues_choruses"].duration, 96)

    def test_asymmetry_gap_and_capstone(self):
        self.assertEqual(self.forms["asymmetric_sections"].duration, 28)
        self.assertEqual(self.forms["gap_transition"].duration, 17)
        self.assertEqual(self.forms["form_capstone"].duration, 40)

    def test_expected_artifact_keys(self):
        expected = {"binary_form", "varied_binary", "ternary_form", "varied_ternary", "AABA",
                    "verse_chorus", "12_bar_blues", "through_composed", "symmetric_sections",
                    "asymmetric_sections", "form_capstone"}
        self.assertTrue(expected.issubset(self.forms))


if __name__ == "__main__":
    unittest.main()
