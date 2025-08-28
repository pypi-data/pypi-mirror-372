from __future__ import annotations

import asyncio
import logging

from remotivelabs.topology.cli.mock.args import ECUMockArgs
from remotivelabs.topology.ecu_mock import ECUMock

_log = logging.getLogger(__name__)


async def main(args: ECUMockArgs):
    _log.info(" > Starting ECUMock(s):\n%s", "\n".join(f"   {ecu}: {', '.join(ns)}" for ecu, ns in args.namespaces.items()))
    ecu = ECUMock(namespaces=args.namespaces, broker_url=args.broker_url, delay_multiplier=args.delay_multiplier)
    await ecu.run()


if __name__ == "__main__":
    ecu_args = ECUMockArgs.parse()
    logging.basicConfig(level=ecu_args.loglevel, format="%(asctime)s.%(msecs)03d [%(levelname)s] %(message)s", datefmt="%H:%M:%S")
    asyncio.run(main(ecu_args))
