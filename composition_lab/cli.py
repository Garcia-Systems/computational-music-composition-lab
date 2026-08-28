"""Command-line experiments for the executable textbook."""

from __future__ import annotations

import argparse
from pathlib import Path
from typing import Sequence

from .waveform import SAMPLE_RATE, render_notes, write_wav

CHAPTER_00_NOTES = (
    ("C4", 261.63, 0.40),
    ("E4", 329.63, 0.40),
    ("G4", 392.00, 0.40),
    ("C5", 523.25, 0.60),
)
CHAPTER_00_FILENAME = "chapter_00_first_composition.wav"


def run_chapter_00(output_directory: Path = Path("outputs")) -> Path:
    """Render Chapter 0's fixed four-note composition and return its path."""
    composition = ((frequency, duration) for _, frequency, duration in CHAPTER_00_NOTES)
    output_path = output_directory / CHAPTER_00_FILENAME
    return write_wav(output_path, render_notes(composition))


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Run Computational Music Composition Lab experiments.")
    parser.add_argument("chapter", choices=("chapter-00",), help="experiment to run")
    parser.add_argument(
        "--output-directory",
        type=Path,
        default=Path("outputs"),
        help="directory for generated files (default: outputs)",
    )
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    output_path = run_chapter_00(args.output_directory)
    note_names = " → ".join(name for name, _, _ in CHAPTER_00_NOTES)
    print(
        "Chapter 0 — The Composition Laboratory\n\n"
        f"Composition:\n{note_names}\n\n"
        f"Rendering:\nsample rate: {SAMPLE_RATE} Hz\nwaveform: sine\n\n"
        f"Created:\n{output_path}\n\n"
        "Experiment complete.\nListen to the WAV file before continuing."
    )
    return 0
