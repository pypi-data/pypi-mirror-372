import logging

from remotivelabs.topology.behavioral_model.behavioral_model import (
    BehavioralModel,
    PingRequest,
    RebootRequest,
)

# Disable library logging by default
_logger = logging.getLogger("remotivelabs.topology")
_logger.addHandler(logging.NullHandler())

__all__ = [
    "BehavioralModel",
    "PingRequest",
    "RebootRequest",
]
