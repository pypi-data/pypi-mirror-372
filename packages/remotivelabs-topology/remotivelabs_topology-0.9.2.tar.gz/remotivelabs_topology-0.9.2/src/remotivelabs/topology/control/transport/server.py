from __future__ import annotations

import logging
from typing import Any

from typing_extensions import Self

from remotivelabs.broker import BrokerClient, NamespaceName
from remotivelabs.topology.comm.transport import TransportHandler
from remotivelabs.topology.comm.transport import TransportServer as TransportServerApi
from remotivelabs.topology.control.transport.message import TransportMessage, TransportMessageType
from remotivelabs.topology.control.transport.rb_transport import RemotiveBrokerTransport

_logger = logging.getLogger(__name__)


class TransportServer(TransportServerApi):
    """
    Transport server implementation using a transport layer.

    TODO: It should be possible to make TransportServer independent of transport type.
    TODO: Make BrokerClient namespace specific, and remove the need for the namespace parameter.
    """

    name: str
    namespace: NamespaceName

    _transport: RemotiveBrokerTransport
    _request_handler: TransportHandler

    def __init__(
        self,
        name: str,
        client: BrokerClient,
        request_handler: TransportHandler,
        namespace: NamespaceName = "virt",
    ) -> None:
        self.name = name
        self._namespace = namespace
        self._transport = RemotiveBrokerTransport(name=name, namespace=namespace, handler=self._handle_message, client=client)

        self._request_handler = request_handler
        _logger.debug(f"TransportServer {self.name} created")

    async def __aenter__(self) -> Self:
        await self._transport.start()
        return self

    async def __aexit__(self, exc_type: type[BaseException] | None, exc_val: BaseException | None, exc_tb: Any) -> None:
        await self._transport.stop()

    def set_handler(self, handler: TransportHandler) -> None:
        self._request_handler = handler

    async def serve_forever(self) -> None:
        """
        Serve requests indefinitely.

        This method blocks until cancelled. Cancellation causes the server to be closed.
        Only one serve_forever task can exist per Server object.

        Note: This method is not needed to properly run the server. It is provided for convenience, as a way to wait until the server is
        closed by some other means (e.g. ctrl-c).

        Raises:
            InvalidStateError: If the server hasn't been started via the context manager.
        """
        # Wait until the transport is cancelled/closed
        await self._transport

    async def _handle_message(self, msg: TransportMessage) -> None:
        if msg.type != TransportMessageType.REQUEST:
            _logger.warning(f"received unexpected message type: {msg.type}")
            return

        if self._request_handler is None:
            _logger.warning("handler not set, ignoring message")
            return

        try:
            _logger.debug(f"handling request {msg.id} from {msg.source}")
            response_payload = await self._request_handler(msg.payload)

            response = TransportMessage(
                type=TransportMessageType.RESPONSE,
                id=msg.id,
                source=self.name,
                payload=response_payload,
            )
            _logger.debug(f"sending response {response.id} to {msg.source}")
            await self._transport.publish_message(msg=response, target_ecu=msg.source)
        except Exception as e:
            _logger.exception(f"error handling request: {e}")
