"""Base sensor for Elica Connect devices."""
from __future__ import annotations

from homeassistant.components.sensor import SensorEntity, SensorDeviceClass, SensorStateClass
from homeassistant.helpers.entity import EntityCategory

from .base_entity import BaseEntity
from .coordinator import ElicaConnectCoordinator


class BaseSensor(BaseEntity, SensorEntity):
    """Base sensor class for Elica Connect."""

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
        super().__init__(coordinator, device_id)
        
        self._key = key
        
        # Entity properties
        self._attr_name = name
        self._attr_unique_id = f"elica_{device_id}_sensor_{key}"
        self._attr_icon = icon
        self._attr_device_class = device_class
        self._attr_state_class = state_class
        self._attr_native_unit_of_measurement = native_unit
        self._attr_entity_category = entity_category