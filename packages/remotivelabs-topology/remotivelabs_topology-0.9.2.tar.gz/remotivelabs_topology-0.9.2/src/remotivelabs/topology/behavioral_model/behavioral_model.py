from __future__ import annotations

import asyncio
import logging
from collections import defaultdict
from dataclasses import dataclass
from typing import AsyncIterator

from typing_extensions import Self

from remotivelabs.broker import BrokerClient, Frame, NamespaceName
from remotivelabs.topology.control.handler import Handler, Router
from remotivelabs.topology.control.request import ControlRequest
from remotivelabs.topology.control.response import ControlResponse
from remotivelabs.topology.control.server import ControlServer
from remotivelabs.topology.namespaces.generic import GenericNamespace
from remotivelabs.topology.namespaces.input_handlers import InputHandler
from remotivelabs.topology.namespaces.namespace import Namespace
from remotivelabs.topology.version import __version__

_logger = logging.getLogger(__name__)


@dataclass
class PingRequest(ControlRequest):
    """
    Control request to check if the `BehavioralModel` is alive and responsive.

    Use `remotivelabs.topology.control.ControlClient` to send control requests.
    """

    type: str = "ping_v1"


@dataclass
class RebootRequest(ControlRequest):
    """
    Control request to reset all namespace restbus to default values.

    Use `remotivelabs.topology.control.ControlClient` to send control requests.
    """

    type: str = "reboot_v1"


class BehavioralModel:
    """
    A BehavioralModel is used to emulate some behavior instead of a real ECU.

    It manages lifecycle operations for namespaces (e.g., `CanNamespace`, `SomeIPNamespace`), handles inputs,
    routes control requests, and provides a unified interface for testing setups.
    """

    _control_router: Router

    _broker_client: BrokerClient
    _control_server: ControlServer
    _control_server_task: asyncio.Task | None
    _sub_task: asyncio.Task | None
    _namespaces: dict[NamespaceName, Namespace]
    _input_handlers: dict[NamespaceName, list[InputHandler]]

    def __init__(
        self,
        name: str,
        broker_client: BrokerClient,
        namespaces: list[Namespace] | None = None,
        input_handlers: list[tuple[NamespaceName, InputHandler]] | None = None,
        control_handlers: list[tuple[str, Handler]] | None = None,
    ):
        """
        Initialize the BehavioralModel instance.

        Args:
            name: Identifier for the ECU stub instance, then name which receives control messages.
            broker_client: The client used for communication with the broker.
            namespaces: list of Namespace instances (`CanNamespace`, `SomeIPNamespace`, etc.).
            input_handlers: Optional list of (namespace, handler list) pairs to receive
                                            callbacks on inputs.
                                            It is advised to create these using the namespace's
                                            `create_input_handler` method.
            control_handlers: Optional list of (command, handler) pairs for routing control messages.

        Note:
            Start the instance using a context manager:
                ```python
                async with BehavioralModel(...) as bm:
                    ...
                    await bm.run_forever()
                ```
            Or use the start/stop methods directly:
                ```python
                bm = BehavioralModel(...)
                await bm.start()
                # ...
                await bm.stop()
                ```
        """
        self._name = name
        self._broker_client = broker_client
        self._namespaces = {ns.name: ns for ns in namespaces or []}
        self._input_handlers: dict[NamespaceName, list[InputHandler]] = defaultdict(list)
        for k, v in input_handlers or []:
            self._input_handlers[k].append(v)

        router = Router(
            fallback_handler=Router(
                [
                    (str(PingRequest.type), self._ping_v1),
                    (str(RebootRequest.type), self._reboot_v1),
                ]
            )
        )
        router.add_routes(control_handlers or [])
        self._control_server = ControlServer(name=name, broker_client=broker_client, handler=router)
        self._control_server_task = None
        self._sub_task = None

        _logger.info(f"BehavioralModel {self._name} using broker at {broker_client.url}")

    async def start(self) -> None:
        """
        Start the behavioral model, open all namespaces, and initialize input handlers.
        This is an idempotent operation - calling it multiple times has no additional effect.
        """
        if self._sub_task is not None:
            return

        ready_event = asyncio.Event()
        self._control_server_task = asyncio.create_task(self._control_server.serve_forever(ready_event))

        await ready_event.wait()
        for namespace in self._namespaces.values():
            await namespace.open()

        sub = await self._subscribe_with_handler()
        self._sub_task = asyncio.create_task(self._run_loop(sub))
        await self._broker_client.restbus.start(*(ns.name for ns in self._namespaces.values() if isinstance(ns, GenericNamespace)))
        _logger.debug(f"BehavioralModel '{self._name}' opened using: {__version__}")

    async def stop(self) -> None:
        """
        Stop the behavioral model, close all namespaces, and clean up resources.
        This is an idempotent operation - calling it multiple times has no additional effect.
        """
        if self._sub_task is None:
            return

        self._sub_task.cancel()
        for namespace in self._namespaces.values():
            await namespace.close()

        if self._control_server_task is not None:
            self._control_server_task.cancel()

        self._sub_task = None
        self._control_server_task = None
        _logger.debug(f"BehavioralModel '{self._name}' closed")

    async def __aenter__(self) -> Self:
        await self.start()
        return self

    async def __aexit__(self, exc_type, exc_value, traceback) -> None:
        await self.stop()

    async def run_forever(self) -> None:
        """Run the BehavioralModel indefinitely, processing inputs and control requests."""
        if self._sub_task is None or self._control_server_task is None:
            raise RuntimeError("BehavioralModel must be started before calling run_forever")

        _logger.debug(f"BehavioralModel '{self._name}' running")
        await asyncio.gather(self._sub_task, self._control_server_task)

    async def _run_loop(self, sub: AsyncIterator[Frame] | None) -> None:
        if sub is None:
            return

        async for frame in sub:
            handlers = self._input_handlers[frame.namespace]
            for handler in handlers:
                if (resp := await handler.handle(frame)) is not None:
                    await self._broker_client.publish(resp)

    async def _subscribe_with_handler(self) -> AsyncIterator[Frame] | None:
        for namespace_name, handlers in self._input_handlers.items():
            frames = await self._broker_client.list_frame_infos(namespace_name)
            for handler in handlers:
                for frame_info in frames:
                    handler.add(frame_info)
                if len(handler.subscriptions()) == 0:
                    raise ValueError(f"Input handler {handler} did not yield any subscriptions on namespace '{namespace_name}'")

        subs = []
        for namespace_name, handlers in self._input_handlers.items():
            for handler in handlers:
                subs.append((namespace_name, handler.subscriptions()))

        if not subs:
            return None

        return await self._broker_client.subscribe_frames(
            *subs,
            on_change=False,
            initial_empty=True,
        )

    # Control request handlers
    async def _ping_v1(self, request: ControlRequest) -> ControlResponse:  # noqa: ARG002
        return ControlResponse(status="ok", data=None)

    async def _reboot_v1(self, request: ControlRequest) -> ControlResponse:  # noqa: ARG002
        for namespace in self._namespaces.values():
            if isinstance(namespace, GenericNamespace):
                await namespace.restbus.reset()
        return ControlResponse(status="ok", data=None)
