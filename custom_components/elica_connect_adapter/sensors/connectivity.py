"""Connectivity sensor entity for Elica Connect."""

from __future__ import annotations

from homeassistant.components.sensor import SensorDeviceClass

from ..coordinator import ElicaConnectCoordinator
from .base import ElicaDiagnosticSensor


class ConnectivitySensor(ElicaDiagnosticSensor):
    """Elica connectivity sensor."""

    def __init__(self, coordinator: ElicaConnectCoordinator, device_id: str) -> None:
        super().__init__(
            coordinator,
            device_id,
            name="Connectivity",
            icon="mdi:wifi",
            translation_key="connectivity",
            device_class=SensorDeviceClass.ENUM,
        )
        self._attr_options = ["connected", "disconnected"]

    @property
    def native_value(self) -> str:
        return "connected" if self.device.state.connected else "disconnected"

    @property
    def extra_state_attributes(self) -> dict[str, Any]:
        return {
            "time_zone": self.device.metadata.get("timeZone"),
        }
