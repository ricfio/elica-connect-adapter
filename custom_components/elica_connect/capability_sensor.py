"""Capability sensors for Elica Connect devices."""
from __future__ import annotations

from dataclasses import dataclass
import logging
from typing import Final

try:
    # HA 2023.8 and newer
    from homeassistant.components.sensor import (
        SensorDeviceClass,
        SensorStateClass,
    )
except ImportError:
    # Older HA versions fallback
    from homeassistant.components.sensor import (
        DEVICE_CLASS_TIMESTAMP,
        SensorStateClass,
    )
    
    class SensorDeviceClass:
        """Mock for older HA versions."""
        TIMESTAMP = DEVICE_CLASS_TIMESTAMP


try:
    # Newer HA versions 
    from homeassistant.const import PERCENTAGE
except ImportError:
    # Use local constant
    PERCENTAGE = "%"

try:
    from homeassistant.helpers.entity import EntityCategory
except ImportError:
    from enum import Enum
    class EntityCategory(str, Enum):
        """Mock for older HA versions."""
        DIAGNOSTIC = "diagnostic"

from .base_sensor import BaseSensor
from .coordinator import ElicaConnectCoordinator

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
        entity_category=EntityCategory.DIAGNOSTIC,
    ),
    "110": CapabilitySensorDefinition(
        name="Fan Speed",
        icon="mdi:fan-speed-1",
        state_class=SensorStateClass.MEASUREMENT,
    ),
}


class CapabilitySensor(BaseSensor):
    """Representation of an Elica capability sensor."""

    def __init__(
        self,
        coordinator: ElicaConnectCoordinator,
        device_id: str,
        key: str | int,
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
            key=str(key),  # Convert to string for consistency
            name=name,
            icon=icon,
            device_class=device_class,
            state_class=state_class,
            native_unit=native_unit,
            entity_category=entity_category,
        )

    @property
    def native_value(self) -> int | float | None:
        """Return the sensor value."""
        device = self.coordinator.get_device(self._device_id)
        if not hasattr(device, "dataModel"):
            return None
        return device.dataModel.get(self._key)

    @property
    def extra_state_attributes(self) -> dict:
        """Return additional state attributes."""
        return {
            "last_update": self.coordinator.last_update_success.isoformat()
            if self.coordinator.last_update_success
            else None,
            "capability_id": self._key,
        }