"""MQTT connectivity sensor entity for Elica Connect."""

from __future__ import annotations

from typing import Any

from homeassistant.components.sensor import SensorDeviceClass

from ..api.core.constants import MQTT_HOST
from ..coordinator import ElicaConnectCoordinator
from .base import ElicaDiagnosticSensor


class MqttConnectivitySensor(ElicaDiagnosticSensor):
    """Elica MQTT connectivity sensor."""

    def __init__(self, coordinator: ElicaConnectCoordinator, device_id: str) -> None:
        super().__init__(
            coordinator,
            device_id,
            icon="mdi:connection",
            translation_key="mqtt_connectivity",
            device_class=SensorDeviceClass.ENUM,
        )
        self._attr_unique_id = f"elica_{device_id}_{self.translation_key}"
        self._attr_options = ["connected", "disconnected"]

    @property
    def native_value(self) -> str:
        return (
            "connected"
            if self.coordinator.data.get("mqtt_stats", {}).get("connected", False)
            else "disconnected"
        )

    @property
    def extra_state_attributes(self) -> dict[str, Any]:
        stats = self.coordinator.data.get("mqtt_stats", {})
        return {
            "broker_url": MQTT_HOST,
            "client_id": "eiot-app",
            "last_connection": stats.get("last_connection"),
            "last_disconnection": stats.get("last_disconnection"),
        }
