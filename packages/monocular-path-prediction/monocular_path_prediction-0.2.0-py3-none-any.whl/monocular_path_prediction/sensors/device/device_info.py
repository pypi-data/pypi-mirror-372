"""Device info."""

from dataclasses import dataclass


@dataclass(frozen=True)
class DeviceInfo:
    """Represent a device choice with an index and a name."""

    index: int
    name: str
