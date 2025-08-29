import asyncio

from remotivelabs.broker import BrokerClient, Frame
from remotivelabs.topology.behavioral_model import BehavioralModel
from remotivelabs.topology.namespaces import filters
from remotivelabs.topology.namespaces.can import CanNamespace


async def _on_hazard_button_pressed(frame: Frame) -> None:
    print(f"Hazzard light frame {frame}")


async def main():
    async with BrokerClient(url="http://127.0.0.1:50051") as broker_client:
        driver_can_0 = CanNamespace("BodyCanModule-DriverCan0", broker_client)

        async with BehavioralModel(
            "BodyCanModule",
            namespaces=[driver_can_0],
            broker_client=broker_client,
            input_handlers=[
                driver_can_0.create_input_handler(
                    [filters.FrameFilter("HazardLightButton")],
                    _on_hazard_button_pressed,
                )
            ],
        ) as bm:
            await bm.run_forever()


if __name__ == "__main__":
    asyncio.run(main())
