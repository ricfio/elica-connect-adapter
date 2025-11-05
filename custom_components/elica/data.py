"""Container for the integration's runtime state."""

from dataclasses import dataclass

from .connect.domain import Device


@dataclass
class IntegrationData:
    """Container for the integration's runtime state."""

    devices: dict[str, Device]
