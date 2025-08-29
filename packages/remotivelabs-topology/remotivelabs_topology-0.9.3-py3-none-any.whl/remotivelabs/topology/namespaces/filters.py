from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass
from functools import partial

from remotivelabs.broker.frame import FrameInfo, SignalInfo


@dataclass(frozen=True)
class Filter(ABC):
    @property
    @abstractmethod
    def include(self) -> bool:
        "Whether matching elements should be included or excluded."
        ...

    def filter_frames(self, _: FrameInfo) -> bool:
        "Determine whether a frame matches the filter."
        return False

    def filter_signals(self, _: SignalInfo, __: FrameInfo) -> bool:
        "Determine whether a signal matches the filter."
        return False


@dataclass(frozen=True)
class SignalFilter(Filter):
    """
    Match a single signal.

    Attributes:
        signal_name: Name of the signal to match.
        include: Whether to include or exclude matches.
    """

    signal_name: str
    include: bool = True

    def filter_signals(self, si: SignalInfo, __) -> bool:
        return self.signal_name == si.name


def _someip_match(sep: str, service_instance_name: str | None, method_or_event: str | None, is_signal: bool, name: str) -> bool:
    if sep not in name:
        return False
    service_part, rest = name.split(sep, 1)
    if not rest or (service_instance_name and service_instance_name != service_part):
        return False
    return rest.startswith(f"{method_or_event}.") if is_signal and method_or_event else method_or_event == rest if method_or_event else True


@dataclass(frozen=True)
class AllFramesFilter(Filter):
    """
    Match all frames.

    Attributes:
        include: Whether to include or exclude matches.
    """

    include: bool = True

    def filter_frames(self, _: FrameInfo) -> bool:
        return True

    def filter_signals(self, _: SignalInfo, __: FrameInfo) -> bool:
        return True


@dataclass(frozen=True)
class FrameFilter(Filter):
    """
    Match a single frame.

    Attributes:
        frame_name: Name of the frame to match.
        include: Whether to include or exclude matches.
    """

    frame_name: str
    include: bool = True

    def filter_frames(self, fi: FrameInfo) -> bool:
        return self.frame_name == fi.name

    def filter_signals(self, _: SignalInfo, fi: FrameInfo) -> bool:
        return self.frame_name == fi.name


@dataclass(frozen=True)
class ReceiverFilter(Filter):
    """
    Match all frames and signals received by `ecu_name`.

    Attributes:
        ecu_name: Name of the ECU that receives the frames or signals.
        include: Whether to include or exclude matches.
    """

    ecu_name: str
    include: bool = True

    def filter_frames(self, fi: FrameInfo) -> bool:
        receivers = set(fi.receiver)
        receivers.update(r for signal in fi.signals.values() for r in signal.receiver)
        return self.ecu_name in receivers

    def filter_signals(self, si: SignalInfo, __) -> bool:
        return self.ecu_name in si.receiver


@dataclass(frozen=True)
class SenderFilter(Filter):
    """
    Match all frames and signals sent by `ecu_name`.

    Attributes:
        ecu_name: Name of the ECU that sends the frames or signals.
        include: Whether to include or exclude matches.
    """

    ecu_name: str
    include: bool = True

    def filter_frames(self, fi: FrameInfo) -> bool:
        senders = set(fi.sender)
        senders.update(r for signal in fi.signals.values() for r in signal.sender)
        return self.ecu_name in senders

    def filter_signals(self, si: SignalInfo, __) -> bool:
        return self.ecu_name in si.sender


@dataclass(frozen=True)
class SomeIPRequestFilter(Filter):
    """
    Match a SOME/IP request.

    Attributes:
        service_instance_name: Name of the service to match. If omitted, all services are considered.
        method_name: Name of the method to match. If omitted, all methods are considered.
        include: Whether to include or exclude matches.
    """

    service_instance_name: str | None = None
    method_name: str | None = None
    include: bool = True

    def __post_init__(self):
        matcher = partial(_someip_match, ".Request.", self.service_instance_name, self.method_name)
        object.__setattr__(self, "filter_frames", lambda fi: matcher(False, fi.name))
        object.__setattr__(self, "filter_signals", lambda si, __: matcher(True, si.name))


@dataclass(frozen=True)
class SomeIPEventFilter(Filter):
    """
    "Match a SOME/IP event."

    Attributes:
        service_instance_name: Name of the service to match. If omitted, all services are considered.
        event_name: Name of the event to match. If omitted, all events are considered.
        include: Whether to include or exclude matches.
    """

    service_instance_name: str | None = None
    event_name: str | None = None
    include: bool = True

    def __post_init__(self):
        matcher = partial(_someip_match, ".Event.", self.service_instance_name, self.event_name)
        object.__setattr__(self, "filter_frames", lambda fi: matcher(False, fi.name))
        object.__setattr__(self, "filter_signals", lambda si, __: matcher(True, si.name))
