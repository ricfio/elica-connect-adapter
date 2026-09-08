"""Capability sensors for Elica Connect devices."""

from __future__ import annotations

from dataclasses import dataclass
import logging
from typing import Final

from homeassistant.components.sensor import SensorDeviceClass, SensorStateClass
from homeassistant.const import PERCENTAGE
from homeassistant.helpers.entity import EntityCategory

from ..coordinator import ElicaConnectCoordinator
from .base_sensors import BaseSensor

_LOGGER = logging.getLogger(__name__)


@dataclass
class CapabilitySensorDefinition:
    """Definition for a device capability sensor."""

    name: str
    icon: str
    device_class: SensorDeviceClass | None = None
    state_class: SensorStateClass | None = None
    native_unit: str | None = None
    entity_category: EntityCategory | None = None


# Mapping of known dataModel values to sensor definitions
CAPABILITY_SENSORS: Final = {
    # Main features with known meanings
    "96": CapabilitySensorDefinition(
        name="Light Brightness",
        icon="mdi:brightness-percent",
        state_class=SensorStateClass.MEASUREMENT,
        native_unit=PERCENTAGE,
    ),
    "64": CapabilitySensorDefinition(
        name="Fan Mode",
        icon="mdi:fan",
        state_class=SensorStateClass.MEASUREMENT,
        # entity_category=EntityCategory.DIAGNOSTIC,
        # entity_category=EntityCategory.CONFIG,
    ),
    "110": CapabilitySensorDefinition(
        name="Fan Speed",
        icon="mdi:fan-speed-1",
        state_class=SensorStateClass.MEASUREMENT,
    ),
    "128": CapabilitySensorDefinition(
        name="Grease Filter Efficiency",
        icon="mdi:air-filter",
        state_class=SensorStateClass.MEASUREMENT,
        native_unit=PERCENTAGE,
        entity_category=EntityCategory.DIAGNOSTIC,
    ),
}


class CapabilitySensor(BaseSensor):
    """Representation of an Elica capability sensor."""

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
        entity_category: EntityCategory | None = None,
    ) -> None:
        """Initialize the sensor."""
        super().__init__(
            coordinator=coordinator,
            device_id=device_id,
            name=name,
            icon=icon,
            device_class=device_class,
            state_class=state_class,
            native_unit=native_unit,
            entity_category=entity_category,
        )
        self._key = key

    @property
    def native_value(self) -> int | float | None:
        """Return the sensor value."""
        device = self.coordinator.get_device(self.device_id)
        return device.data_model.get(self._key)

    @property
    def extra_state_attributes(self) -> dict:
        """Return additional state attributes."""
        attrs = {
            "capability_id": self._key,
        }
        device = self.coordinator.get_device(self.device_id)
        if device and self._key == "128" and device.filters:
            filter_data = device.filters[0]
            attrs.update({
                "filter_id": filter_data.id,
                "filter_type": filter_data.type,
                "filter_status": filter_data.status,
                "saturation_alert": filter_data.saturation_alert,
                "installation_date": filter_data.installation_date,
                "last_reset": filter_data.last_reset,
                "filter_model": filter_data.model,
            })
        return attrs
