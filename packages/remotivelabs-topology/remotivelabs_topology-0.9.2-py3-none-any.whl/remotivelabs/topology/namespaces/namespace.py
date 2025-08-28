from __future__ import annotations

from abc import ABC
from typing import Awaitable, Callable, Generic, TypeVar

from typing_extensions import Self

from remotivelabs.broker import BrokerClient, NamespaceName
from remotivelabs.topology.namespaces.filters import Filter

F = TypeVar("F", bound=Filter)
C = TypeVar("C", bound=Callable[..., Awaitable[object]])


class Namespace(ABC, Generic[F, C]):
    """
    See implementations in `namespaces`, e.g.
    `remotivelabs.topology.namespaces.some_ip.SomeIPNamespace` or `remotivelabs.topology.namespaces.can.CanNamespace`.
    """

    def __init__(
        self,
        name: NamespaceName,
        broker_client: BrokerClient,
    ):
        self._namespace = name
        self._broker_client = broker_client
        self._opened = False

    @property
    def name(self) -> NamespaceName:
        return self._namespace

    async def open(self) -> Self:
        """
        Open the namespace and prepare it for use.
        This is an idempotent operation - calling it multiple times has no additional effect.

        Raises:
            ValueError: If the namespace is not configured on RemotiveBroker

        Returns:
            The namespace
        """
        ns = await self._broker_client.get_namespace(self.name)
        if ns is None:
            raise ValueError(f"Namespace '{self.name}' is not configured on RemotiveBroker")
        self._opened = True
        return self

    async def close(self) -> None:
        """
        Close the namespace and clean up resources.
        This is an idempotent operation - calling it multiple times has no additional effect.
        """
        self._opened = False

    async def __aenter__(self) -> Self:
        return await self.open()

    async def __aexit__(self, exc_type, exc_value, traceback) -> None:
        await self.close()
