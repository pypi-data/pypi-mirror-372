from __future__ import annotations

import asyncio
import logging

from remotivelabs.broker import BrokerClient
from remotivelabs.topology.comm.format import MessageFormat
from remotivelabs.topology.comm.transport import TransportServer as TransportServerApi
from remotivelabs.topology.control import request, response
from remotivelabs.topology.control.handler import Handler
from remotivelabs.topology.control.request import ControlRequest
from remotivelabs.topology.control.response import ControlResponse
from remotivelabs.topology.control.transport.server import TransportServer

_logger = logging.getLogger(__name__)

control_request_fmt: MessageFormat[ControlRequest] = request
control_response_fmt: MessageFormat[ControlResponse] = response


class ControlServer:
    """
    Control message server.
    """

    def __init__(self, name: str, broker_client: BrokerClient, handler: Handler) -> None:
        """
        Create a control message server.

        Args:
            broker_client: BrokerClient instance.
            handler: Handler instance.
        """
        self._handler = handler
        self._transport: TransportServerApi = TransportServer(name=name, client=broker_client, request_handler=self.transport_handler)

    def set_handler(self, handler: Handler) -> None:
        self._handler = handler

    async def transport_handler(self, payload: bytes) -> bytes:
        request = control_request_fmt.loads(payload)
        _logger.debug(f"received request {request}")
        response = await self._handler(request)
        _logger.debug(f"sending response {response}")
        return control_response_fmt.dumps(response)

    async def serve_forever(self, ready: asyncio.Event | None = None) -> None:
        """
        Serve requests indefinitely.

        This method blocks until cancelled. Cancellation causes the server to be closed.
        """

        async with self._transport as transport:
            if ready is not None:
                ready.set()
            await transport.serve_forever()
