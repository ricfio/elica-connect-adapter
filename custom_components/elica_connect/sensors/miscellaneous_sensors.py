"""Support for Elica sensors."""

from __future__ import annotations

from homeassistant.components.sensor import SensorDeviceClass, SensorStateClass

from ..coordinator import ElicaConnectCoordinator
from .base_sensors import ElicaDiagnosticSensor


class CapabilitySensor(ElicaDiagnosticSensor):
    """Device Capability Sensor."""

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
            name=name,
            icon="mdi:bank",
        )


class ConnectivityStateSensor(ElicaDiagnosticSensor):
    """Cloud Connectivity Sensor."""

    def __init__(self, coordinator: ElicaConnectCoordinator, device_id: str) -> None:
        """Initialize the sensor."""
        super().__init__(
            coordinator,
            device_id,
            name="Connectivity state",
            icon="mdi:wifi",
        )

    @property
    def native_value(self) -> str:
        """Return the sensor value."""
        return "Connected" if self.device.state.connected else "Disconnected"


class MqttConnectionSensor(ElicaDiagnosticSensor):
    """MQTT Connection Sensor."""

    def __init__(self, coordinator: ElicaConnectCoordinator, device_id: str) -> None:
        """Initialize the sensor."""
        super().__init__(
            coordinator,
            device_id,
            name="MQTT Connection",
            icon="mdi:connection",
        )

    @property
    def native_value(self) -> str:
        """Return the sensor value."""
        return "Connected" if self.device.state.connected else "Disconnected"
