"""MQTT diagnostic sensors for Elica Connect."""

from __future__ import annotations

import logging
from dataclasses import dataclass
from typing import Any, Final

from homeassistant.components.sensor import SensorDeviceClass, SensorStateClass
from homeassistant.helpers.entity import EntityCategory

from ..api.core.constants import MQTT_HOST
from ..coordinator import ElicaConnectCoordinator
from .base_sensors import ElicaDiagnosticSensor

_LOGGER = logging.getLogger(__name__)


@dataclass
class MqttSensorDefinition:
    """Definition for an MQTT diagnostic sensor."""

    name: str
    icon: str
    device_class: SensorDeviceClass | None = None
    state_class: SensorStateClass | None = None
    native_unit: str | None = None
    entity_category: EntityCategory | None = EntityCategory.DIAGNOSTIC


# MQTT Diagnostic sensor keys
MQTT_STATE = "mqtt_state"
MQTT_MESSAGES = "mqtt_messages"

# MQTT sensor definitions
MQTT_SENSORS: Final = {
    MQTT_STATE: MqttSensorDefinition(
        name="MQTT State",
        icon="mdi:connection",
        entity_category=EntityCategory.DIAGNOSTIC,
    ),
    MQTT_MESSAGES: MqttSensorDefinition(
        name="MQTT Messages",
        icon="mdi:message-badge",
        state_class=SensorStateClass.TOTAL_INCREASING,
        entity_category=EntityCategory.DIAGNOSTIC,
    ),
}


class MqttStateSensor(ElicaDiagnosticSensor):
    """Representation of MQTT State sensor."""

    def __init__(self, coordinator: ElicaConnectCoordinator, device_id: str) -> None:
        super().__init__(
            coordinator,
            device_id,
            name="MQTT State",
            icon="mdi:connection",
            translation_key="mqtt_state",
        )
        self._attr_unique_id = f"elica_{device_id}_mqtt_state"

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


class MqttMessagesSensor(ElicaDiagnosticSensor):
    """Representation of MQTT Messages sensor."""

    def __init__(self, coordinator: ElicaConnectCoordinator, device_id: str) -> None:
        super().__init__(
            coordinator,
            device_id,
            name="MQTT Messages",
            icon="mdi:message-badge",
            state_class=SensorStateClass.TOTAL_INCREASING,
            translation_key="mqtt_messages",
        )
        self._attr_unique_id = f"elica_{device_id}_mqtt_messages"

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
