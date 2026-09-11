"""Base sensor entities for Elica Connect."""

from __future__ import annotations

from homeassistant.components.sensor import (
    SensorDeviceClass,
    SensorEntity,
    SensorStateClass,
)
from homeassistant.helpers.entity import EntityCategory
from homeassistant.util import slugify

from ..coordinator import ElicaConnectCoordinator
from ..entity import ElicaDeviceEntity


class ElicaSensor(ElicaDeviceEntity, SensorEntity):
    """Base class for Elica sensors."""

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
        translation_key: str | None = None,
    ) -> None:
        super().__init__(coordinator, device_id)
        if translation_key:
            self._attr_translation_key = translation_key
        else:
            self._attr_name = name
        self._attr_unique_id = slugify(f"{self.device.cuid}_{name}")
        self._attr_icon = icon
        self._attr_device_class = device_class
        self._attr_state_class = state_class
        self._attr_native_unit_of_measurement = native_unit
        self._attr_entity_category = entity_category


class ElicaDiagnosticSensor(ElicaSensor):
    """Base class for Elica diagnostic sensor."""

    def __init__(
        self,
        coordinator: ElicaConnectCoordinator,
        device_id: str,
        name: str,
        icon: str | None = None,
        device_class: SensorDeviceClass | None = None,
        state_class: SensorStateClass | None = None,
        native_unit: str | None = None,
        translation_key: str | None = None,
    ) -> None:
        super().__init__(
            coordinator,
            device_id,
            name=name,
            icon=icon,
            device_class=device_class,
            state_class=state_class,
            native_unit=native_unit,
            entity_category=EntityCategory.DIAGNOSTIC,
            translation_key=translation_key,
        )
