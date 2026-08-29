import contextlib
import io
import tempfile
import unittest
from pathlib import Path

from composition_lab.cli import CHAPTER_COMMANDS, CHAPTER_TITLES, main, verify_book


class BookCliTests(unittest.TestCase):
    def test_registry_is_exactly_chapters_00_through_35(self):
        self.assertEqual(36, len(CHAPTER_TITLES))
        self.assertEqual(tuple(f"chapter-{n:02d}" for n in range(36)), CHAPTER_COMMANDS)

    def test_chapter_listing_is_discoverable(self):
        output = io.StringIO()
        with contextlib.redirect_stdout(output):
            self.assertEqual(0, main(["chapters"]))
        lines = output.getvalue().splitlines()
        self.assertEqual(36, len(lines))
        self.assertTrue(lines[0].startswith("00  The Composition Laboratory"))
        self.assertIn("chapter-35", lines[-1])

    def test_no_argument_prints_help_successfully(self):
        output = io.StringIO()
        with contextlib.redirect_stdout(output):
            self.assertEqual(0, main([]))
        self.assertIn("verify-book", output.getvalue())

    def test_verifier_reports_missing_structure_without_running_chapters(self):
        with tempfile.TemporaryDirectory() as directory:
            problems = verify_book(Path(directory))
        self.assertTrue(problems)
        self.assertIn("missing required file: README.md", problems)

    def test_repository_structure_verifies(self):
        self.assertEqual((), verify_book())


if __name__ == "__main__":
    unittest.main()
