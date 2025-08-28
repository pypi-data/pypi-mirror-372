from __future__ import annotations

from abc import ABC, abstractmethod
from collections import defaultdict
from dataclasses import dataclass, field
from typing import Awaitable, Callable, Protocol, Sequence, Union, cast

import remotivelabs.topology.namespaces._conv.some_ip_converter as conv
from remotivelabs.broker import Frame, FrameInfo, FrameSubscription, NamespaceName, WriteSignal
from remotivelabs.topology.namespaces.filters import (
    AllFramesFilter,
    Filter,
    FrameFilter,
    ReceiverFilter,
    SenderFilter,
    SignalFilter,
    SomeIPEventFilter,
    SomeIPRequestFilter,
)
from remotivelabs.topology.namespaces.some_ip import RequestType, SomeIPError, SomeIPEvent, SomeIPRequest, SomeIPResponse

__doc__ = """
Handlers for filtered processing of inputs in RemotiveTopology.

This module defines handlers for processing inputs, such as frames, that match specific filters. Handlers include:

- `FrameHandler`: For general frame handling using signal or frame filters.
- `SomeIPRequestHandler`: For handling SOME/IP request frames and responding.
- `SomeIPEventHandler`: For handling SOME/IP event frames.
"""


@dataclass(frozen=True)
class _SubscriptionMetadata:
    named_values: dict[int, str] = field(default_factory=dict)


class InputHandler(Protocol):
    """"""

    def add(self, *frame_infos: FrameInfo) -> None: ...
    def subscriptions(self) -> list[FrameSubscription]: ...
    async def handle(self, frame: Frame) -> tuple[NamespaceName, list[WriteSignal]] | None: ...


class _BaseHandler(ABC, InputHandler):
    def __init__(
        self,
        filters: Sequence[Filter],
        cb: Callable[..., Awaitable[object]] | None = None,
        decode_named_values: bool = False,
    ):
        self._include_filters: list[Filter] = [f for f in filters if f.include]
        self._exclude_filters: list[Filter] = [f for f in filters if not f.include]
        self._subscriptions: list[FrameSubscription] = []
        self._cb = cb
        self._routes: dict[str, dict[str, _SubscriptionMetadata]] = defaultdict(dict)
        self._decode_named_values = decode_named_values

    def __str__(self) -> str:
        includes = ", ".join(str(f) for f in self._include_filters) if self._include_filters else "None"
        excludes = ", ".join(str(f) for f in self._exclude_filters) if self._exclude_filters else "None"
        return f"Includes: {includes}, Excludes: {excludes}"

    def add(self, *frame_infos: FrameInfo):
        for frame_info in frame_infos:
            frame_sub = any(f.filter_frames(frame_info) for f in self._include_filters) and not any(
                f.filter_frames(frame_info) for f in self._exclude_filters
            )

            signals: dict[str, _SubscriptionMetadata] = defaultdict()
            for si in frame_info.signals.values():
                if any(f.filter_signals(si, frame_info) for f in self._include_filters) and not any(
                    f.filter_signals(si, frame_info) for f in self._exclude_filters
                ):
                    signals[si.name] = _SubscriptionMetadata(named_values=si.named_values)

            if frame_sub or signals:
                self._routes[frame_info.name] = signals

    def subscriptions(self) -> list[FrameSubscription]:
        return [FrameSubscription(name=frame_name, signals=list(signals.keys())) for frame_name, signals in self._routes.items()]

    async def handle(self, frame: Frame) -> tuple[NamespaceName, list[WriteSignal]] | None:
        sub = self._routes.get(frame.name)
        if sub is None:
            return None

        if self._decode_named_values:
            signals = {name: sub[name].named_values.get(cast(int, value), value) for name, value in frame.signals.items() if name in sub}
        else:
            signals = {name: value for name, value in frame.signals.items() if name in sub}

        return await self(Frame(timestamp=frame.timestamp, name=frame.name, namespace=frame.namespace, signals=signals, value=frame.value))

    @abstractmethod
    async def __call__(self, frame: Frame) -> tuple[NamespaceName, list[WriteSignal]] | None: ...


class FrameHandler(_BaseHandler):
    """
    Handler for Frames.

    This class wraps a callback that and passes objects matching provided filters.
    It should be passed to an `BehavioralModel` for automatic subscription and dispatch.

    Args:
        filters: A sequence of filters used to match relevant frames.
        cb: Async callback invoked with a Frame when matched.
        decode_named_values: True will decode named values to str.
    """

    _cb: Callable[[Frame], Awaitable[None]] | None

    def __init__(
        self,
        filters: Sequence[Union[SenderFilter, ReceiverFilter, FrameFilter, AllFramesFilter, SignalFilter]],
        cb: Callable[[Frame], Awaitable[None]] | None = None,
        decode_named_values: bool = False,
    ):
        super().__init__(filters=filters, cb=cb, decode_named_values=decode_named_values)

    async def __call__(self, frame: Frame) -> None:
        if self._cb:
            await self._cb(frame)


class SomeIPRequestHandler(_BaseHandler):
    """
    Handler for SOME/IP requests.

    This class wraps a callback that and passes objects matching provided filters.
    It should be passed to an `BehavioralModel` for automatic subscription and dispatch.

    Args:
        filters: A sequence of SomeIPRequestFilter used to match incoming request frames.
        cb: Async callback that receives a SomeIPRequest and returns a response or None.
        decode_named_values: True will decode named values to str.
    """

    _cb: Callable[[SomeIPRequest], Awaitable[SomeIPResponse | SomeIPError | None]] | None

    def __init__(
        self,
        filters: Sequence[SomeIPRequestFilter],
        cb: Callable[[SomeIPRequest], Awaitable[SomeIPResponse | SomeIPError | None]] | None = None,
        decode_named_values: bool = False,
    ):
        super().__init__(filters=filters, cb=cb, decode_named_values=decode_named_values)

    async def __call__(self, frame: Frame):
        if self._cb:
            request, meta = conv.frame_to_some_ip_request(frame)
            response = await self._cb(request)
            if response is not None and request.message_type == RequestType.REQUEST:
                return (
                    frame.namespace,
                    conv.some_ip_response_to_signals(response, request.service_instance_name, request.name, meta),
                )
        return None


class SomeIPEventHandler(_BaseHandler):
    """
    Handler for SOME/IP events.

    This class wraps a callback that and passes objects matching provided filters.
    It should be passed to an `BehavioralModel` for automatic subscription and dispatch.

    Args:
        filters: A sequence of SomeIPEventFilter used to match event frames.
        cb: Async callback invoked with a SomeIPEvent.
        decode_named_values: True will decode named values to str.
    """

    _cb: Callable[[SomeIPEvent], Awaitable[None]] | None

    def __init__(
        self,
        filters: Sequence[SomeIPEventFilter],
        cb: Callable[[SomeIPEvent], Awaitable[None]] | None = None,
        decode_named_values: bool = False,
    ):
        super().__init__(filters=filters, cb=cb, decode_named_values=decode_named_values)

    async def __call__(self, frame: Frame) -> None:
        if self._cb:
            event = conv.frame_to_some_ip_event(frame)
            await self._cb(event)
