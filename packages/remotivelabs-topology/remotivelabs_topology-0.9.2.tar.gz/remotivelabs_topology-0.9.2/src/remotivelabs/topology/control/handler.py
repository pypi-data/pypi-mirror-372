from __future__ import annotations

from dataclasses import dataclass
from typing import Protocol, runtime_checkable

from remotivelabs.topology.control.request import ControlRequest
from remotivelabs.topology.control.response import ControlResponse


@dataclass
class RouteAlreadyExistsError(Exception):
    """Exception raised when a route is already present in the router."""

    type: str

    def __str__(self) -> str:
        return f"Route for type '{self.type}' already exists in the router"


@runtime_checkable
class Handler(Protocol):
    """
    A callable protocol for handling control messages asynchronously.

    Implementations must define an async __call__ method that takes a
    ControlRequest and returns a ControlResponse.
    """

    async def __call__(self, request: ControlRequest) -> ControlResponse:
        pass


class Router(Handler):
    """
    A router that can be used to route control messages to different handlers.
    """

    _routes: dict[str, Handler] = {}
    _fallback_handler: Handler | None = None

    def __init__(self, handlers: list[tuple[str, Handler]] | None = None, fallback_handler: Handler | None = None):
        self._routes = {} if handlers is None else dict(handlers)
        self._fallback_handler = fallback_handler

    async def __call__(self, request: ControlRequest) -> ControlResponse:
        handler = self._routes.get(request.type)
        if handler:
            return await handler(request)
        if self._fallback_handler:
            return await self._fallback_handler(request)
        return ControlResponse(status="invalid_request", data=f"No handler found for request type: {request.type}")

    def add_route(self, type: str, handler: Handler):
        if type in self._routes:
            raise RouteAlreadyExistsError(type)
        self._routes[type] = handler

    def add_routes(self, handlers: list[tuple[str, Handler]]):
        for type, handler in handlers:
            self.add_route(type, handler)

    def add_fallback_handler(self, handler: Handler):
        self._fallback_handler = handler
