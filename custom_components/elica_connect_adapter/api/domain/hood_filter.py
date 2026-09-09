"""Hood filter."""

from dataclasses import dataclass


@dataclass
class HoodFilter:
    """Representation of a hood filter."""

    id: int | None = None
    type: str | None = None
    status: str | None = None
    efficiency: int | None = None
    saturation_alert: bool | None = None
    installation_date: str | None = None
    last_reset: str | None = None
    model: str | None = None
