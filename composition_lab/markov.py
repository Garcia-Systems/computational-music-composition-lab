"""Small, inspectable first-order transition helpers.

Counts—not floating point probabilities—are the learned model.  The functions
are generic over hashable symbolic states, so scale degrees and durations use
exactly the same mechanism.
"""

from __future__ import annotations

from collections.abc import Callable, Hashable, Iterable, Mapping, Sequence
from dataclasses import dataclass
import random
from typing import TypeVar

T = TypeVar("T", bound=Hashable)
TransitionCounts = dict[T, dict[T, int]]


class DeadEndError(ValueError):
    """Raised when a state has no observed successor."""


def transition_pairs(sequence: Sequence[T], *, cyclic: bool = False) -> tuple[tuple[T, T], ...]:
    """Return adjacent pairs, optionally adding the final-to-first pair."""
    pairs = tuple(zip(sequence, sequence[1:]))
    if cyclic and sequence:
        pairs += ((sequence[-1], sequence[0]),)
    return pairs


def build_transition_counts(sequence: Sequence[T], *, cyclic: bool = False) -> TransitionCounts[T]:
    """Count observed adjacent states without inventing terminal transitions."""
    counts: TransitionCounts[T] = {}
    for current, following in transition_pairs(sequence, cyclic=cyclic):
        outgoing = counts.setdefault(current, {})
        outgoing[following] = outgoing.get(following, 0) + 1
    return counts


def build_transition_counts_from_sequences(
    sequences: Iterable[Sequence[T]], *, cyclic: bool = False,
) -> TransitionCounts[T]:
    """Merge internal transitions while preserving sequence boundaries."""
    combined: TransitionCounts[T] = {}
    for sequence in sequences:
        for current, outgoing in build_transition_counts(sequence, cyclic=cyclic).items():
            target = combined.setdefault(current, {})
            for following, count in outgoing.items():
                target[following] = target.get(following, 0) + count
    return combined


def transition_probabilities(
    counts: Mapping[T, Mapping[T, int]],
) -> dict[T, dict[T, float]]:
    """Normalize every outgoing count row for inspection."""
    probabilities: dict[T, dict[T, float]] = {}
    for state, outgoing in counts.items():
        total = sum(outgoing.values())
        if total <= 0 or any(count <= 0 for count in outgoing.values()):
            raise ValueError("transition counts must be positive")
        probabilities[state] = {following: count / total for following, count in outgoing.items()}
    return probabilities


def next_states(counts: Mapping[T, Mapping[T, int]], state: T) -> tuple[tuple[T, int], ...]:
    """Return the visible successor/weight row in deterministic key order."""
    outgoing = counts.get(state)
    if not outgoing:
        raise DeadEndError(f"state {state!r} has no observed successor")
    return tuple((following, outgoing[following]) for following in sorted(outgoing))


def choose_next_state(counts: Mapping[T, Mapping[T, int]], state: T,
                      rng: random.Random) -> T:
    """Choose from observed successors, using their counts directly as weights."""
    options = next_states(counts, state)
    return rng.choices(tuple(value for value, _ in options),
                       weights=tuple(weight for _, weight in options), k=1)[0]


def generate_markov_sequence(
    counts: Mapping[T, Mapping[T, int]], start_state: T, length: int,
    rng: random.Random, *, dead_end: str = "stop",
) -> tuple[T, ...]:
    """Generate ``length`` states; explicitly stop or restart at a dead end."""
    if length < 1:
        raise ValueError("length must be positive")
    if dead_end not in ("stop", "restart"):
        raise ValueError("dead_end must be 'stop' or 'restart'")
    result = [start_state]
    while len(result) < length:
        try:
            result.append(choose_next_state(counts, result[-1], rng))
        except DeadEndError:
            if dead_end == "stop":
                break
            result.append(start_state)
    return tuple(result)


@dataclass(frozen=True)
class ValidMarkovResult:
    candidate: tuple[T, ...] | None
    attempts: int


def generate_valid_markov_candidate(
    counts: Mapping[T, Mapping[T, int]], start_state: T, length: int,
    constraints: Sequence[Callable[[tuple[T, ...]], bool]], rng: random.Random,
    max_attempts: int = 1000,
) -> ValidMarkovResult[T]:
    """Apply Chapter 19-style bounded rejection sampling to Markov candidates."""
    if max_attempts <= 0:
        raise ValueError("max_attempts must be greater than zero")
    for attempt in range(1, max_attempts + 1):
        candidate = generate_markov_sequence(counts, start_state, length, rng)
        if len(candidate) == length and all(rule(candidate) for rule in constraints):
            return ValidMarkovResult(candidate, attempt)
    return ValidMarkovResult(None, max_attempts)
