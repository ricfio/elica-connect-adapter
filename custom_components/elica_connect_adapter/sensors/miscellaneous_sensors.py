"""Support for Elica sensors."""

from __future__ import annotations

from homeassistant.components.sensor import SensorDeviceClass

from ..coordinator import ElicaConnectCoordinator
from .base_sensors import ElicaDiagnosticSensor


class ConnectivityStateSensor(ElicaDiagnosticSensor):
    """Cloud Connectivity Sensor."""

    def __init__(self, coordinator: ElicaConnectCoordinator, device_id: str) -> None:
        """Initialize the sensor."""
        super().__init__(
            coordinator,
            device_id,
            name="Connectivity state",
            icon="mdi:wifi",
            translation_key="connectivity_state",
            device_class=SensorDeviceClass.ENUM,
        )
        self._attr_options = ["connected", "disconnected"]

    @property
    def native_value(self) -> str:
        """Return the sensor value."""
        return "connected" if self.device.state.connected else "disconnected"
