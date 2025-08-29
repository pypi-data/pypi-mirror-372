from __future__ import annotations

import logging
import os
from argparse import ArgumentParser
from dataclasses import dataclass

from remotivelabs.broker.auth import ApiKeyAuth, AuthMethod, NoAuth


@dataclass(frozen=True)
class BehavioralModelArgs:
    """Command line argument parser.

    Attributes:
        url: URL argument for RemotiveBroker.
        auth: Auth method to use for RemotiveBroker.
        delay_multiplier: Multiply all delays in restbus with this value.
        loglevel: Logging level.
    """

    url: str
    auth: AuthMethod
    delay_multiplier: float
    loglevel: str

    @staticmethod
    def parse() -> BehavioralModelArgs:
        """
        Parse command line arguments.
        """

        parser = ArgumentParser()
        parser.add_argument(
            "-u",
            "--url",
            default=os.environ.get("REMOTIVE_BROKER_URL", "http://127.0.0.1:50051"),
            type=str,
            metavar="URL",
        )
        parser.add_argument(
            "-b",
            "--delay-multiplier",
            default=1.0,
            type=float,
            metavar="DELAY_MULTIPLIER",
        )
        parser.add_argument(
            "-x",
            "--x_api_key",
            default=os.environ.get("REMOTIVE_BROKER_API_KEY", ""),
            type=str,
            metavar="X_API_KEY",
        )
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
        p, _ = parser.parse_known_args()
        return BehavioralModelArgs(
            url=p.url,
            auth=NoAuth() if p.x_api_key == "" else ApiKeyAuth(p.x_api_key),
            delay_multiplier=p.delay_multiplier,
            loglevel=p.loglevel,
        )


if __name__ == "__main__":
    BehavioralModelArgs.parse()
