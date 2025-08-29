from __future__ import annotations

import asyncio
from typing import AsyncIterator, Awaitable, Callable, Sequence, Union, overload

from typing_extensions import Self

import remotivelabs.topology.namespaces._conv.some_ip_converter as conv
from remotivelabs.broker import BrokerClient, Frame, FrameSubscription, NamespaceName
from remotivelabs.topology.namespaces import input_handlers
from remotivelabs.topology.namespaces.filters import SomeIPEventFilter, SomeIPRequestFilter
from remotivelabs.topology.namespaces.namespace import Namespace
from remotivelabs.topology.namespaces.some_ip.event import SomeIPEvent
from remotivelabs.topology.namespaces.some_ip.request import RequestType, SomeIPRequest, SomeIPRequestNoReturn, SomeIPRequestReturn
from remotivelabs.topology.namespaces.some_ip.response import SomeIPError, SomeIPResponse
from remotivelabs.topology.namespaces.some_ip.types import ServiceName


class SomeIPNamespace(
    Namespace[
        Union[SomeIPRequestFilter, SomeIPEventFilter],
        Union[Callable[[SomeIPRequest], Awaitable[Union[SomeIPResponse, SomeIPError, None]]], Callable[[SomeIPEvent], Awaitable[None]]],
    ]
):
    """
    SomeIP provides a client-side interface for sending SOME/IP requests and handling responses
    within a specific namespace using a broker client.

    The client maintains a session ID counter and ensures that the namespace is of type 'someip'
    before issuing requests. To validate and activate the namespace, this class must be used
    as an async context manager.
    """

    def __init__(self, name: NamespaceName, broker_client: BrokerClient, client_id: int, decode_named_values: bool = False):
        """
        Initialize the SomeIP namespace client

        Args:
            name: The namespace name to operate in.
            broker_client: The client used to communicate with the broker.
            client_id: The SOME/IP client ID used for requests.
            decode_named_values: True will decode named values to str.

        Note:
            Use together with a `BehavioralModel` or start the instance using a context manager:
            ```python
            async with SomeIPNamespace(...) as namespace:
                ...
            ```
        """
        super().__init__(name=name, broker_client=broker_client)
        self._client_id = client_id
        self._session_id = _SessionIdCounter()
        self._decode_named_values = decode_named_values

    async def open(self) -> Self:
        """
        Opens the SOME/IP namespace and validates that the namespace is of the correct type.
        This is an idempotent operation - calling it multiple times has no additional effect.

        Returns:
            The namespace

        Raises:
            ValueError: If the namespace is not of type 'someip'.
        """
        if self._opened:
            return self

        ns = await self._broker_client.get_namespace(self.name)
        if ns is None or ns.type != "someip":
            raise ValueError(f"Namespace '{self.name}' is missing or not of type 'someip'")

        self._opened = True
        return await super().open()

    @overload
    async def request(self, req: SomeIPRequestReturn) -> asyncio.Task[SomeIPResponse | SomeIPError]: ...

    @overload
    async def request(self, req: SomeIPRequestNoReturn) -> asyncio.Task[None]: ...

    @overload
    async def request(self, req: SomeIPRequest) -> asyncio.Task[SomeIPResponse | SomeIPError | None]: ...

    async def request(self, req: SomeIPRequest) -> asyncio.Task[SomeIPResponse | SomeIPError | None]:
        """
        Send a SOME/IP request and return an asyncio Task that resolves to the response or error.

        Args:
            req: A SomeIPRequest instance specifying service, method, type, and parameters.

        Returns:
            asyncio.Task that resolves to SomeIPResponse, SomeIPError, or None if no return is expected.

        Raises:
            ValueError: If a response is expected but the response frame is missing.
        """
        response_frame = await self._broker_client.get_frame_info(
            name=f"{req.service_instance_name}.Response.{req.name}", namespace=self.name
        )

        if req.message_type == RequestType.REQUEST:
            if response_frame is None:
                raise ValueError(f"Expected a response frame for request, but got None for {req.service_instance_name}.Response.{req.name}")

            sub = await self._broker_client.subscribe_frames(
                (self._namespace, [FrameSubscription(name=response_frame.name)]),
                initial_empty=True,
                decode_named_values=self._decode_named_values,
            )
        else:
            sub = None

        req_session_id = self._session_id.get_next()
        await self._broker_client.publish((self.name, conv.some_ip_request_to_signals(req, self._client_id, req_session_id)))

        async def response_task(
            sub: AsyncIterator[Frame] | None,
        ) -> SomeIPResponse | SomeIPError | None:
            if sub is None or response_frame is None:
                return None

            async for frame in sub:
                response, meta = conv.frame_to_some_ip_response(frame, response_frame.signals)
                if meta.client_id == self._client_id and meta.session_id == req_session_id:
                    return response
            return None

        return asyncio.create_task(response_task(sub))

    async def notify(self, event: SomeIPEvent) -> None:
        """
        Emit a SOME/IP event

        Args:
            event: The SOME/IP event
        """
        await self._broker_client.publish((self.name, conv.some_ip_event_to_signals(event)))

    async def subscribe(
        self,
        *events: tuple[str, ServiceName],
        on_change: bool = False,
    ) -> AsyncIterator[SomeIPEvent]:
        """
        Subscribes to a stream of SOME/IP events.

        Args:
            *events: One or more tuples, each containing event name and service name of events to subscribe to.
            on_change: If True, only yield updates when signal values change.

        Returns:
            An asynchronous iterator with SomeIPEvent.
        """
        stream = await self._broker_client.subscribe_frames(
            (self.name, [FrameSubscription(name=f"{service}.Event.{name}") for name, service in events]),
            on_change=on_change,
            decode_named_values=self._decode_named_values,
        )

        async def async_generator() -> AsyncIterator[SomeIPEvent]:
            async for frame in stream:
                yield conv.frame_to_some_ip_event(frame)

        return async_generator()

    @overload
    def create_input_handler(
        self,
        filters: Sequence[SomeIPRequestFilter],
        callback: Callable[[SomeIPRequest], Awaitable[SomeIPResponse | SomeIPError | None]],
    ) -> tuple[NamespaceName, input_handlers.InputHandler]: ...

    @overload
    def create_input_handler(
        self,
        filters: Sequence[SomeIPEventFilter],
        callback: Callable[[SomeIPEvent], Awaitable[None]],
    ) -> tuple[NamespaceName, input_handlers.InputHandler]: ...

    @overload
    def create_input_handler(
        self,
        filters: Sequence[SomeIPRequestFilter | SomeIPEventFilter],
        callback: Union[
            Callable[[SomeIPRequest], Awaitable[SomeIPResponse | SomeIPError | None]], Callable[[SomeIPEvent], Awaitable[None]]
        ],
    ) -> tuple[NamespaceName, input_handlers.InputHandler]: ...

    def create_input_handler(
        self,
        filters: Sequence[SomeIPRequestFilter | SomeIPEventFilter],
        callback: Union[
            Callable[[SomeIPRequest], Awaitable[SomeIPResponse | SomeIPError | None]], Callable[[SomeIPEvent], Awaitable[None]]
        ],
    ) -> tuple[NamespaceName, input_handlers.InputHandler]:
        """
        Creates a list of input handlers for the given namespace to be used with a `BehavioralModel`.

        Each handler defines a filter and a corresponding async callback for processing matching requests/events.

        Args:
            - filters: A sequence of SomeIPRequestFilter or SomeIPEventFilter objects to select relevant requests or events
            - callback: An async callback function that receives and processes a request or event.
        """

        if all(isinstance(f, SomeIPRequestFilter) for f in filters):
            return (
                self.name,
                input_handlers.SomeIPRequestHandler(filters=filters, cb=callback, decode_named_values=self._decode_named_values),  # type: ignore[arg-type]
            )
        return (self.name, input_handlers.SomeIPEventHandler(filters=filters, cb=callback, decode_named_values=self._decode_named_values))  # type: ignore[arg-type]


class _SessionIdCounter:
    def __init__(self, start=1):
        if not 1 <= start <= 65535:
            raise ValueError("Initial value must be between 1 and 65535.")
        self._value = start

    def get_next(self):
        current_value = self._value
        self._value = (self._value + 1) & 0xFFFF  # Wrap around at 16 bits
        if self._value == 0:
            self._value = 1
        return current_value
