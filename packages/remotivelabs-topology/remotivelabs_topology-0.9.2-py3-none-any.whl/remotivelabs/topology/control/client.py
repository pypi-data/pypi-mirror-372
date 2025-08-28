from __future__ import annotations

import asyncio
import logging

from typing_extensions import Self

from remotivelabs.broker import BrokerClient
from remotivelabs.topology.comm.format import MessageFormat
from remotivelabs.topology.comm.transport import TransportClient as TransportClientApi
from remotivelabs.topology.control import request, response
from remotivelabs.topology.control.request import ControlRequest
from remotivelabs.topology.control.response import ControlResponse
from remotivelabs.topology.control.transport.client import TransportClient

control_request_fmt: MessageFormat[ControlRequest] = request
control_response_fmt: MessageFormat[ControlResponse] = response

_logger = logging.getLogger(__name__)


class ControlClient:
    """
    Client for sending control messages in a Remotive topology.

    A ControlClient is used to send abstract or synthetic control messages that do not exist
    in a real vehicle but are useful to manipulate or initialize models into a specific state.
    """

    def __init__(self, client: BrokerClient) -> None:
        """
        Control message client.

        Args:
            client: BrokerClient instance.

        Note:
            Start the instance using a context manager:
            ```python
            async with ControlClient(...) as client:
                ...
            ```
        """
        self._transport: TransportClientApi = TransportClient(client=client)

    async def __aenter__(self) -> Self:
        await self._transport.__aenter__()
        return self

    async def __aexit__(self, exc_type, exc_value, traceback) -> None:
        await self._transport.__aexit__(exc_type, exc_value, traceback)

    async def send(self, target_ecu: str, request: ControlRequest, timeout: float = 10.0, retries: int = 0) -> ControlResponse:
        """
        Send a control request to the target ECU, retrying on timeout.

        Args:
            target_ecu: The name of the target ECU.
            request: The control message request.
            timeout: Timeout per attempt in seconds.
            retries: Number of retries on timeout. Defaults to 0.

        Returns:
            Control response.
        """

        data = control_request_fmt.dumps(request)
        for attempt in range(retries + 1):
            try:
                _logger.debug(f"attempt {attempt + 1}: sending request {request}")
                ret = await asyncio.wait_for(self._transport.send(data=data, target_ecu=target_ecu, timeout=timeout), timeout=timeout)
                response = control_response_fmt.loads(ret)
                _logger.debug(f"received response {response}")
                return response
            except asyncio.TimeoutError:
                continue

        raise asyncio.TimeoutError(f"Timeout sending {request} to '{target_ecu}'")
