from __future__ import annotations

import asyncio
from contextlib import AsyncExitStack

from remotivelabs.broker import BrokerClient
from remotivelabs.topology.behavioral_model import BehavioralModel
from remotivelabs.topology.namespaces import filters
from remotivelabs.topology.namespaces.generic import GenericNamespace, RestbusConfig


class ECUMock:
    def __init__(self, namespaces: dict[str, list[str]], broker_url: str, delay_multiplier: float):
        self._namespaces = namespaces
        self._broker_url = broker_url
        self._delay_multiplier = delay_multiplier

    async def run(self):
        async with BrokerClient(self._broker_url) as broker_client:
            models: list[BehavioralModel] = [
                BehavioralModel(
                    ecu,
                    namespaces=[
                        GenericNamespace(
                            name=namespace,
                            broker_client=broker_client,
                            restbus_configs=[RestbusConfig([filters.SenderFilter(ecu_name=ecu)])],
                        )
                        for namespace in namespace_list
                    ],
                    broker_client=broker_client,
                )
                for ecu, namespace_list in self._namespaces.items()
            ]

            async with AsyncExitStack() as stack:
                for model in models:
                    await stack.enter_async_context(model)
                await asyncio.gather(*(model.run_forever() for model in models))
