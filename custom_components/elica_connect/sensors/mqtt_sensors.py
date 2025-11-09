"""MQTT diagnostic sensors for Elica Connect."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
import logging
from typing import Final

from homeassistant.components.sensor import SensorDeviceClass, SensorStateClass
from homeassistant.helpers.entity import EntityCategory

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
MQTT_LAST_MESSAGE = "mqtt_last_message"
MQTT_MESSAGES_RECEIVED = "mqtt_messages_received"
MQTT_CONNECTION_STATUS = "mqtt_connection"
MQTT_LAST_DISCONNECT = "mqtt_last_disconnect"

# MQTT sensor definitions
MQTT_SENSORS: Final = {
    MQTT_LAST_MESSAGE: MqttSensorDefinition(
        name="MQTT Last Message",
        icon="mdi:message-clock",
        device_class=SensorDeviceClass.TIMESTAMP,
    ),
    MQTT_MESSAGES_RECEIVED: MqttSensorDefinition(
        name="MQTT Messages Received",
        icon="mdi:message-badge",
        state_class=SensorStateClass.TOTAL_INCREASING,
    ),
    MQTT_CONNECTION_STATUS: MqttSensorDefinition(
        name="MQTT Connection",
        icon="mdi:connection",
    ),
    MQTT_LAST_DISCONNECT: MqttSensorDefinition(
        name="MQTT Last Disconnect",
        icon="mdi:connection-off",
        device_class=SensorDeviceClass.TIMESTAMP,
    ),
}


class MqttDiagnosticSensor(ElicaDiagnosticSensor):
    """Representation of an MQTT diagnostic sensor."""

    def __init__(
        self,
        coordinator: ElicaConnectCoordinator,
        device_id: str,
        key: str,
        name: str,
        icon: str | None = None,
        device_class: SensorDeviceClass | None = None,
        state_class: SensorStateClass | None = None,
        native_unit: str | None = None,
    ) -> None:
        """Initialize the sensor."""
        super().__init__(
            coordinator=coordinator,
            device_id=device_id,
            # key=key,
            name=name,
            icon=icon,
            # device_class=device_class,
            state_class=state_class,
            native_unit=native_unit,
            # entity_category=EntityCategory.DIAGNOSTIC,
        )
        self._key = key
        self._attr_unique_id = (
            f"elica_{device_id}_mqtt_{key}"  # Override base unique_id
        )

    @property
    def native_value(self) -> datetime | int | float | str | None:
        """Return the sensor value."""
        from datetime import datetime
        import zoneinfo

        mqtt_stats = self.coordinator.data.get("mqtt_stats", {})

        if self._key == MQTT_LAST_MESSAGE:
            timestamp = mqtt_stats.get("last_message")
            if timestamp:
                # Parse ISO string and add timezone
                try:
                    dt = datetime.fromisoformat(timestamp)
                    if dt.tzinfo is None:
                        # Add local timezone if not present
                        dt = dt.replace(tzinfo=zoneinfo.ZoneInfo("UTC"))
                    return dt
                except ValueError:
                    _LOGGER.warning("Invalid timestamp format: %s", timestamp)
                    return None
            return None

        if self._key == MQTT_MESSAGES_RECEIVED:
            return mqtt_stats.get("messages_received", 0)

        if self._key == MQTT_CONNECTION_STATUS:
            return "connected" if mqtt_stats.get("connected", False) else "disconnected"

        if self._key == MQTT_LAST_DISCONNECT:
            timestamp = mqtt_stats.get("last_disconnect")
            if timestamp:
                try:
                    dt = datetime.fromisoformat(timestamp)
                    if dt.tzinfo is None:
                        dt = dt.replace(tzinfo=zoneinfo.ZoneInfo("UTC"))
                    return dt
                except ValueError:
                    _LOGGER.warning("Invalid timestamp format: %s", timestamp)
                    return None
            return None
        return None
