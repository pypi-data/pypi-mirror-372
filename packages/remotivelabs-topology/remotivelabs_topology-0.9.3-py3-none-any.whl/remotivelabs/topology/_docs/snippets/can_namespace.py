import asyncio

from remotivelabs.broker import BrokerClient
from remotivelabs.topology.namespaces import filters
from remotivelabs.topology.namespaces.can import CanNamespace, RestbusConfig


async def main():
    async with (
        BrokerClient(url="http://127.0.0.1:50051") as broker_client,
        CanNamespace(
            "HazardLightControlUnit-DriverCan0",
            broker_client,
            restbus_configs=[RestbusConfig([filters.SenderFilter(ecu_name="HazardLightControlUnit")])],
        ),
    ):
        await asyncio.Event().wait()


if __name__ == "__main__":
    asyncio.run(main())
