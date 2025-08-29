from __future__ import annotations

import argparse
import logging
import os
from argparse import ArgumentParser
from collections import defaultdict
from dataclasses import dataclass


def _parse_namespace_pair(pair: str) -> tuple[str, list[str]]:
    if "=" not in pair:
        raise argparse.ArgumentTypeError(f"Invalid format: '{pair}', expected NAMESPACE=ECU1,ECU2")
    namespace, ecu_str = pair.split("=", 1)
    if not namespace or not ecu_str:
        raise argparse.ArgumentTypeError(f"Empty namespace or ECU list in: '{pair}'")
    ecus = [e.strip() for e in ecu_str.split(",") if e.strip()]
    if not ecus:
        raise argparse.ArgumentTypeError(f"No valid ECUs in: '{pair}'")
    return namespace, ecus


@dataclass
class ECUMockArgs:
    """Command line argument parser.

    Attributes:
        namespaces: Dict where keys are ECU names and value is a list of namespaces.
        broker_url: URL of the broker.
        delay_multiplier: Multiply all delays with this value.
        loglevel: Logging level.
    """

    namespaces: dict[str, list[str]]
    broker_url: str
    delay_multiplier: float
    loglevel: str

    @staticmethod
    def parse() -> ECUMockArgs:
        parser = ArgumentParser(prog="ECUMock")
        parser.add_argument(
            "-n",
            "--namespaces",
            type=_parse_namespace_pair,
            action="append",
            required=True,
            metavar="NAMESPACE=ECU1,ECU2",
            help="Repeatable NAMESPACE=ECU1,ECU2 pairs (ECUs comma-separated)",
        )
        parser.add_argument(
            "-u",
            "--url",
            type=str,
            default=os.environ.get("REMOTIVE_BROKER_URL", "http://http://127.0.0.1:50051"),
            metavar="REMOTIVE_BROKER_URL",
        )
        parser.add_argument("-d", "--delay-multiplier", type=float, default=1.0)
        parser.add_argument(
            "-l",
            "--loglevel",
            default=logging.getLevelName(logging.INFO),
            choices=[
                logging.getLevelName(logging.CRITICAL),
                logging.getLevelName(logging.FATAL),
                logging.getLevelName(logging.ERROR),
                logging.getLevelName(logging.WARNING),
                logging.getLevelName(logging.INFO),
                logging.getLevelName(logging.DEBUG),
            ],
            type=str,
            metavar="LEVEL",
        )

        args = parser.parse_args()

        ns_dict: dict[str, list[str]] = defaultdict(list)
        for namespace, ecus in args.namespaces:
            for ecu in ecus:
                ns_dict[ecu].append(namespace)
        return ECUMockArgs(namespaces=ns_dict, broker_url=args.url, delay_multiplier=args.delay_multiplier, loglevel=args.loglevel)
