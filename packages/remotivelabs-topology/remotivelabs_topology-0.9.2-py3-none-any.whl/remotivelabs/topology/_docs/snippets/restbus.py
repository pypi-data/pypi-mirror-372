import asyncio

from remotivelabs.broker import BrokerClient, RestbusSignalConfig
from remotivelabs.topology.behavioral_model import BehavioralModel
from remotivelabs.topology.namespaces import filters
from remotivelabs.topology.namespaces.can import CanNamespace, RestbusConfig


async def main():
    async with BrokerClient(url="http://127.0.0.1:50051") as broker_client:
        driver_can_0 = CanNamespace(
            "HazardLightControlUnit-DriverCan0",
            broker_client,
            restbus_configs=[RestbusConfig([filters.SenderFilter(ecu_name="HazardLightControlUnit")])],
        )

        async with BehavioralModel(
            "HazardLightControlUnit",
            namespaces=[driver_can_0],
            broker_client=broker_client,
        ) as bm:
            # Simulate pressing the hazard light button
            await driver_can_0.restbus.update_signals(RestbusSignalConfig.set(name="HazardLightButton.HazardLightButton", value=1))
            await bm.run_forever()


if __name__ == "__main__":
    asyncio.run(main())
