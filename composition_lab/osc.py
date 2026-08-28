"""Small localhost OSC protocol and drift-aware Chapter 26 scheduler."""

from __future__ import annotations

from collections.abc import Callable, Mapping, Sequence
from dataclasses import dataclass
import time
from typing import Protocol

from .events import NoteEvent
from .pitch import pitch_to_frequency
from .rhythm import beats_to_seconds
from .chapter22 import velocity_to_amplitude

OSC_HOST = "127.0.0.1"
OSC_PORT = 57121
PING_ADDRESS = "/ping"
NOTE_ADDRESS = "/note"
PANIC_ADDRESS = "/panic"
SUPPORTED_INSTRUMENTS = frozenset(("sine", "saw", "pulse", "articulated_saw"))


class MessageTransport(Protocol):
    def send_message(self, address: str, arguments: Sequence[object]) -> None: ...


@dataclass(frozen=True)
class PlaybackChoice:
    instrument: str
    pan: float = 0.0

    def __post_init__(self) -> None:
        if self.instrument not in SUPPORTED_INSTRUMENTS:
            raise ValueError(f"unsupported instrument: {self.instrument}")
        if isinstance(self.pan, bool) or not isinstance(self.pan, (int, float)) or not -1 <= self.pan <= 1:
            raise ValueError("pan must be between -1 and 1")


@dataclass(frozen=True)
class OscMessage:
    address: str
    arguments: tuple[object, ...]


@dataclass(frozen=True)
class OscOnsetGroup:
    beat: float
    at_seconds: float
    messages: tuple[OscMessage, ...]


def validate_destination(host: str, port: int) -> None:
    if host != OSC_HOST:
        raise ValueError("Chapter 26 is localhost-only; host must be 127.0.0.1")
    if isinstance(port, bool) or not isinstance(port, int) or not 1 <= port <= 65535:
        raise ValueError("port must be an integer between 1 and 65535")


def note_event_to_osc_payload(event: NoteEvent, *, bpm: float, instrument: str,
                              pan: float = 0.0) -> tuple[object, ...]:
    """Convert an event without mutating it; argument order is the protocol contract."""
    choice = PlaybackChoice(instrument, pan)
    if bpm <= 0:
        raise ValueError("bpm must be greater than zero")
    frequency = pitch_to_frequency(event.pitch)
    amplitude = velocity_to_amplitude(event.velocity)
    duration = beats_to_seconds(event.duration, bpm)
    if frequency <= 0 or duration <= 0:
        raise ValueError("frequency and duration_seconds must be greater than zero")
    return (frequency, amplitude, duration, choice.instrument, float(choice.pan))


def build_osc_schedule(events: Sequence[NoteEvent], layers: Sequence[str], *, bpm: float,
                       playback_by_layer: Mapping[str, PlaybackChoice]) -> tuple[OscOnsetGroup, ...]:
    """Build immutable onset groups, preserving input order within equal starts."""
    if bpm <= 0:
        raise ValueError("bpm must be greater than zero")
    if len(events) != len(layers):
        raise ValueError("events and layers must have equal lengths")
    indexed = sorted(enumerate(zip(events, layers, strict=True)), key=lambda item: (item[1][0].start, item[0]))
    groups: list[OscOnsetGroup] = []
    for _, (event, layer) in indexed:
        if layer not in playback_by_layer:
            raise ValueError(f"missing playback configuration for layer: {layer}")
        choice = playback_by_layer[layer]
        message = OscMessage(NOTE_ADDRESS, note_event_to_osc_payload(
            event, bpm=bpm, instrument=choice.instrument, pan=choice.pan))
        if groups and groups[-1].beat == event.start:
            previous = groups[-1]
            groups[-1] = OscOnsetGroup(previous.beat, previous.at_seconds,
                                       previous.messages + (message,))
        else:
            groups.append(OscOnsetGroup(float(event.start), float(event.start) * 60.0 / bpm, (message,)))
    return tuple(groups)


class OscNoteClient:
    """Protocol facade; a supplied transport makes it usable without networking."""
    def __init__(self, host: str = OSC_HOST, port: int = OSC_PORT,
                 *, transport: MessageTransport | None = None) -> None:
        validate_destination(host, port)
        if transport is None:
            try:
                from pythonosc.udp_client import SimpleUDPClient
            except ImportError as error:
                raise RuntimeError("live mode requires the 'python-osc' package") from error
            transport = SimpleUDPClient(host, port)
        self.transport = transport

    def ping(self) -> None:
        self.transport.send_message(PING_ADDRESS, [])

    def note(self, arguments: Sequence[object]) -> None:
        self.transport.send_message(NOTE_ADDRESS, list(arguments))

    def panic(self) -> None:
        self.transport.send_message(PANIC_ADDRESS, [])


def execute_osc_schedule(schedule: Sequence[OscOnsetGroup], client: OscNoteClient, *,
                         clock: Callable[[], float] = time.monotonic,
                         sleep: Callable[[float], None] = time.sleep,
                         verbose: bool = False) -> None:
    """Send against absolute monotonic targets; late groups are sent immediately."""
    started = clock()
    for group in schedule:
        remaining = started + group.at_seconds - clock()
        if remaining > 0:
            sleep(remaining)
        actual = clock() - started
        if verbose:
            print(f"beat={group.beat:.2f} target={group.at_seconds:.3f}s actual={actual:.3f}s "
                  f"lateness={max(0.0, actual-group.at_seconds):.3f}s events={len(group.messages)}")
        for message in group.messages:
            client.note(message.arguments)
