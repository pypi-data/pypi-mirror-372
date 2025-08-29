from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Awaitable, Callable, Protocol

from typing_extensions import Self


@dataclass
class InvalidStateError(Exception):
    """
    Raised when an operation is attempted on a transport object that is not initialized/started.
    """


TransportHandler = Callable[[bytes], Awaitable[bytes]]
"""
Handler for server-side transport message handling.
"""


class TransportClient(Protocol):
    async def __aenter__(self) -> Self:
        """Add async setup for the client here. Should be idempotent."""
        return self

    async def __aexit__(self, exc_type: type[BaseException] | None, exc_value: BaseException | None, traceback: Any) -> None:
        """Add async teardown for the client here. Should be idempotent."""
        pass

    async def send(self, data: bytes, target_ecu: str, timeout: float = 10.0) -> bytes:
        """
        Send data to the target ECU, and wait for a response.

        Args:
            data: The data to send.
            target_ecu: The target ECU.
            timeout: The timeout for the request in seconds. Defaults to 10 seconds.

        Returns:
            The response from the target ECU.

        Raises:
            InvalidStateError: If the client is not connected.
        """


class TransportServer(Protocol):
    async def __aenter__(self) -> Self:
        """Add async setup for the server here. Should be idempotent."""
        return self

    async def __aexit__(self, exc_type: type[BaseException] | None, exc_value: BaseException | None, traceback: Any) -> None:
        """Add async teardown for the server here. Should be idempotent."""

    def set_handler(self, handler: TransportHandler) -> None:
        """
        Set handler to be used for incoming requests. May be called multiple times, each time replacing the previous handler.

        Args:
            handler: The handler to be used for incoming requests.
        """

    async def serve_forever(self) -> None:
        """
        Serve requests indefinitely.

        Cancellation of serve_forever task causes the server to be closed. This method can be called if the server is already accepting
        connections. Only one serve_forever task can exist per one Server object.
        """
