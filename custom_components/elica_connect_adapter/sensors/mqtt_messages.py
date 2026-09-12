"""MQTT messages sensor entity for Elica Connect."""

from __future__ import annotations

from typing import Any

from homeassistant.components.sensor import SensorStateClass

from ..coordinator import ElicaConnectCoordinator
from .base import ElicaDiagnosticSensor


class MqttMessagesSensor(ElicaDiagnosticSensor):
    """Elica MQTT messages sensor."""

    def __init__(self, coordinator: ElicaConnectCoordinator, device_id: str) -> None:
        super().__init__(
            coordinator,
            device_id,
            name="MQTT Messages",
            icon="mdi:message-badge",
            state_class=SensorStateClass.TOTAL_INCREASING,
            translation_key="mqtt_messages",
        )
        self._attr_unique_id = f"elica_{device_id}_{self.translation_key}"

    @property
    def native_value(self) -> int:
        return self.coordinator.data.get("mqtt_stats", {}).get("total_messages", 0)

    @property
    def extra_state_attributes(self) -> dict[str, Any]:
        stats = self.coordinator.data.get("mqtt_stats", {})
        return {
            "last_timestamp": stats.get("last_message_timestamp"),
            "last_payload": stats.get("last_message_payload"),
        }
