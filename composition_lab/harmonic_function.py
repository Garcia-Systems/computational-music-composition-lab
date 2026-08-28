"""A deliberately narrow major-key functional-harmony vocabulary.

The labels here describe broad pedagogical regions for diatonic triads.  They
are not a style-independent analyzer and do not assign an aesthetic tension
score to a chord.
"""

from __future__ import annotations

from collections.abc import Iterable


_MAJOR_FUNCTIONS = {
    1: "tonic",
    2: "predominant",
    3: "tonic-like",
    4: "predominant",
    5: "dominant",
    6: "tonic-like",
    7: "dominant",
}

_ABBREVIATIONS = {
    "tonic": "T", "tonic-like": "T", "predominant": "P", "dominant": "D",
}


def harmonic_function(degree: int) -> str:
    """Return the broad function of one diatonic triad in an introductory major model."""
    if isinstance(degree, bool) or not isinstance(degree, int):
        raise TypeError("degree must be an integer")
    if not 1 <= degree <= 7:
        raise ValueError("degree must be between 1 and 7")
    return _MAJOR_FUNCTIONS[degree]


def functional_path(degrees: Iterable[int]) -> tuple[str, ...]:
    """Map scale degrees to full functional labels, preserving every chord."""
    return tuple(harmonic_function(degree) for degree in degrees)


def abbreviated_functional_path(degrees: Iterable[int]) -> tuple[str, ...]:
    """Return T/P/D labels after the full vocabulary has been established."""
    return tuple(_ABBREVIATIONS[label] for label in functional_path(degrees))
