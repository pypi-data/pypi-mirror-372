from __future__ import annotations

import asyncio
import logging
from dataclasses import dataclass
from typing import Any, AsyncIterator, Awaitable, Callable, Generator

from remotivelabs.broker import BrokerClient, NamespaceName, Signal, WriteSignal
from remotivelabs.topology.comm.transport import InvalidStateError
from remotivelabs.topology.control.transport.message import TransportMessage
from remotivelabs.topology.control.transport.message import dumps as transport_dumps
from remotivelabs.topology.control.transport.message import loads as transport_loads

_logger = logging.getLogger(__name__)


@dataclass
class ControlNamespaceNotFoundError(Exception):
    """Raised when a control namespace is not found on the broker."""

    namespace: NamespaceName
    broker: str

    def __str__(self) -> str:
        return f"Control message namespace '{self.namespace}' not found on broker '{self.broker}'"


@dataclass
class InvalidControlNamespaceError(Exception):
    """Raised when a given control namespace is not of type 'virtual'."""

    namespace: NamespaceName

    def __str__(self) -> str:
        return f"Control message namespace '{self.namespace}' is not of type 'virtual'"


class RemotiveBrokerTransport:
    """
    Internal helper to handle RemotiveBroker transport layer functionality like publish and subscribe.
    """

    name: str
    namespace: NamespaceName
    _client: BrokerClient
    _handle_message: Callable[[TransportMessage], Awaitable[None]]

    def __init__(self, name: str, namespace: NamespaceName, handler: Callable[[TransportMessage], Awaitable[None]], client: BrokerClient):
        self.name = name
        self.namespace = namespace
        self._client = client
        self._handle_message = handler

        self._task: asyncio.Task | None = None
        self._ready_event = asyncio.Event()

    @property
    def is_started(self) -> bool:
        return self._task is not None and not self._task.done()

    def __await__(self) -> Generator[Any, Any, Any]:
        if not self.is_started:
            raise InvalidStateError("Transport is not started")
        assert self._task is not None  # assert to make mypy happy
        return self._task.__await__()

    async def start(self) -> None:
        """Start the transport. This method is idempotent, so it's safe to call multiple times."""
        if self.is_started:
            return

        await self._assert_is_virtual_interface()
        self._task = asyncio.create_task(self._run())
        await self._ready_event.wait()
        _logger.debug(f"{self.name} transport started")

    async def stop(self) -> None:
        """Stop the transport. This method is idempotent, so it's safe to call multiple times."""
        try:
            if self._task:
                self._task.cancel()
        finally:
            self._ready_event.clear()
            self._task = None
            _logger.debug(f"{self.name} transport stopped")

    async def _assert_is_virtual_interface(self) -> None:
        """Check if the namespace exists and is virtual"""
        namespace = await self._client.get_namespace(self.namespace)
        if namespace is None:
            raise ControlNamespaceNotFoundError(namespace=self.namespace, broker=self._client.client_id)
        if not namespace.is_virtual():
            raise InvalidControlNamespaceError(namespace=self.namespace)

    async def publish_message(self, msg: TransportMessage, target_ecu: str) -> None:
        """Publish a message to the target ECU"""
        await self._client.publish((self.namespace, [WriteSignal(name=target_ecu, value=transport_dumps(msg))]))

    async def _subscribe_to_messages(self) -> AsyncIterator[bytes]:
        signals_stream: AsyncIterator[list[Signal]] = await self._client.subscribe((self.namespace, [self.name]), initial_empty=True)
        self._ready_event.set()

        async for signals in signals_stream:
            data = signals[0].value
            assert isinstance(data, bytes)
            yield data

    async def _run(self) -> None:
        try:
            async for raw_msg in self._subscribe_to_messages():
                msg = transport_loads(raw_msg)
                await self._handle_message(msg)
        except Exception:
            _logger.exception(f"{self.name} transport task failed")
            raise
