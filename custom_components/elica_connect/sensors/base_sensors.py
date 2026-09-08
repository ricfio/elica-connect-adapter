"""Support for Elica sensors."""

from __future__ import annotations

from homeassistant.components.sensor import (
    SensorDeviceClass,
    SensorEntity,
    SensorStateClass,
)
from homeassistant.helpers.entity import EntityCategory
from homeassistant.util import slugify

# from .capability_sensor import CAPABILITY_SENSORS, CapabilitySensor
from ..coordinator import ElicaConnectCoordinator
from ..entity import ElicaDeviceEntity


class BaseSensor(ElicaDeviceEntity, SensorEntity):
    """Representation of Elica Base sensors."""

    def __init__(
        self,
        coordinator: ElicaConnectCoordinator,
        device_id: str,
        name: str,
        icon: str | None = None,
        device_class: SensorDeviceClass | None = None,
        state_class: SensorStateClass | None = None,
        native_unit: str | None = None,
        entity_category: EntityCategory | None = None,
    ) -> None:
        """Initialize the sensor."""
        super().__init__(coordinator, device_id)
        self._attr_name = name
        self._attr_unique_id = slugify(f"{self.device.cuid}_{name}")
        self._attr_icon = icon
        self._attr_device_class = device_class
        self._attr_state_class = state_class
        self._attr_native_unit_of_measurement = native_unit
        self._attr_entity_category = entity_category

    # @property
    # def available(self) -> bool:
    #     """Indica se il device è disponibile."""
    #     return self.device is not None


class ElicaDiagnosticSensor(BaseSensor):
    """Representation of Elica Diagnostic sensors."""

    def __init__(
        self,
        coordinator: ElicaConnectCoordinator,
        device_id: str,
        name: str,
        icon: str | None = None,
        device_class: SensorDeviceClass | None = None,
        state_class: SensorStateClass | None = None,
        native_unit: str | None = None,
    ) -> None:
        """Initialize the diagnostic sensor."""
        super().__init__(
            coordinator,
            device_id,
            name=name,
            icon=icon,
            device_class=device_class,
            state_class=state_class,
            native_unit=native_unit,
            entity_category=EntityCategory.DIAGNOSTIC,
        )
