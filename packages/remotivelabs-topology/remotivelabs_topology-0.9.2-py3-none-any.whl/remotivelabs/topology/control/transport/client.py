from __future__ import annotations

import asyncio
import logging
from typing import Any

from typing_extensions import Self

from remotivelabs.broker import BrokerClient, NamespaceName
from remotivelabs.topology.comm.transport import InvalidStateError
from remotivelabs.topology.comm.transport import TransportClient as TransportClientApi
from remotivelabs.topology.control.transport.message import TransportMessage, TransportMessageType
from remotivelabs.topology.control.transport.rb_transport import RemotiveBrokerTransport

_logger = logging.getLogger(__name__)


class TransportClient(TransportClientApi):
    """
    Transport client implementation using a transport layer.

    TODO: It should be possible to make TransportClient independent of transport type.
    TODO: Make BrokerClient namespace specific, and remove the need for the namespace parameter.
    """

    name: str
    namespace: NamespaceName

    _transport: RemotiveBrokerTransport
    _pending_requests: dict[str, asyncio.Future]

    def __init__(self, client: BrokerClient, namespace: NamespaceName = "virt") -> None:
        self.name = client.client_id
        self.namespace = namespace
        self._transport = RemotiveBrokerTransport(name=self.name, namespace=namespace, handler=self._handle_message, client=client)

        self._pending_requests = {}
        _logger.debug(f"TransportClient {self.name} created")

    async def __aenter__(self) -> Self:
        await self._transport.start()
        return self

    async def __aexit__(self, exc_type: type[BaseException] | None, exc_val: BaseException | None, exc_tb: Any) -> None:
        await self._transport.stop()

    async def send(self, data: bytes, target_ecu: str, timeout: float = 10.0) -> bytes:
        """
        Send request and wait for response.

        Args:
            data: The data to send.
            target_ecu: The target ECU.
            timeout: The timeout for the request in seconds. Defaults to 10 seconds.

        Returns:
            The response data.

        Raises:
            InvalidStateError: If the transport is not started.
        """
        if not self._transport.is_started:
            raise InvalidStateError("TransportClient transport must be started before sending requests")

        request = TransportMessage(
            type=TransportMessageType.REQUEST,
            payload=data,
            source=self.name,
        )

        response_fut: asyncio.Future = asyncio.Future()
        if request.id in self._pending_requests:
            _logger.error(f"message id {request.id} already in use")
            raise ValueError(f"message id already in use: {request.id}")
        self._pending_requests[request.id] = response_fut

        _logger.debug(f"sending request {request.id} to {target_ecu}")
        await self._transport.publish_message(msg=request, target_ecu=target_ecu)

        try:
            await asyncio.wait_for(response_fut, timeout=timeout)
        except asyncio.TimeoutError as err:
            _logger.warning(f"no response for {request.id} received within {timeout} seconds")
            raise err
        finally:
            del self._pending_requests[request.id]

        res = response_fut.result()
        assert isinstance(res, bytes)
        return res

    async def _handle_message(self, msg: TransportMessage) -> None:
        """Handle received messages."""
        if msg.type != TransportMessageType.RESPONSE:
            _logger.warning(f"unexpected message type: {msg.type}")
            return

        if msg.id not in self._pending_requests:
            _logger.warning(f"unexpected message id: {msg.id}")
            return

        _logger.debug(f"received response {msg.id} from {msg.source}")
        self._pending_requests[msg.id].set_result(msg.payload)
