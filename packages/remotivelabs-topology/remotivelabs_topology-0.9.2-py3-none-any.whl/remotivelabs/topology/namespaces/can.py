from __future__ import annotations

from typing_extensions import Self

from remotivelabs.topology.namespaces.generic import GenericNamespace, Restbus, RestbusConfig

__all__ = ["CanNamespace", "Restbus", "RestbusConfig"]


class CanNamespace(GenericNamespace):
    """
    Used to represent a CAN (Controller Area Network) namespace in a simulation or
    testing environment.

    It inherits all behavior from `GenericNamespace` without modification, but serves
    as a semantic identifier for CAN-specific configurations or extensions.
    """

    async def open(self) -> Self:
        """
        Opens the CAN namespace and validates that the namespace is of the correct type.
        This is an idempotent operation - calling it multiple times has no additional effect.

        Returns:
            The namespace

        Raises:
            ValueError: If the namespace is not of type 'can', 'canfd', or 'udp'.
        """
        if self._opened:
            return self

        ns = await self._broker_client.get_namespace(self.name)
        if ns is None or ns.type not in ["can", "canfd", "udp"]:
            raise ValueError(f"Namespace '{self.name}' is missing or not of type 'can', 'canfd' or 'udp'")

        return await super().open()
