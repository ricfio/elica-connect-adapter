"""Capability sensor entities for Elica Connect."""

from __future__ import annotations

import logging

from homeassistant.components.sensor import SensorDeviceClass, SensorStateClass
from homeassistant.helpers.entity import EntityCategory

from ..api.domain.capabilities import Capability
from ..coordinator import ElicaConnectCoordinator
from .base import ElicaSensor
from .definitions import CAPABILITY_SENSORS, CapabilitySensorDefinition

_LOGGER = logging.getLogger(__name__)


class CapabilitySensor(ElicaSensor):
    """Elica capability sensor."""

    def __init__(
        self,
        coordinator: ElicaConnectCoordinator,
        device_id: str,
        key: str,
        name: str | None = None,
        icon: str | None = None,
        device_class: SensorDeviceClass | None = None,
        state_class: SensorStateClass | None = None,
        native_unit: str | None = None,
        entity_category: EntityCategory | None = None,
        translation_key: str | None = None,
    ) -> None:
        super().__init__(
            coordinator=coordinator,
            device_id=device_id,
            name=name or "",
            icon=icon,
            device_class=device_class,
            state_class=state_class,
            native_unit=native_unit,
            entity_category=entity_category,
            translation_key=translation_key,
        )
        self._key = key

    @property
    def native_value(self) -> int | float | None:
        device = self.coordinator.get_device(self.device_id)
        val = device.data_model.get(self._key)
        if val is not None and self._key == Capability.FILTER_SATURATION:
            try:
                return max(0, min(100, 100 - int(val)))
            except (TypeError, ValueError):
                return val
        return val

    @property
    def extra_state_attributes(self) -> dict:
        device = self.coordinator.get_device(self.device_id)
        capability_value = device.data_model.get(self._key) if device else None

        attrs = {
            "capability_id": self._key,
            "capability_value": capability_value,
        }
        if device and self._key == Capability.FILTER_SATURATION:
            if capability_value is not None:
                try:
                    saturation = max(0, min(100, int(capability_value)))
                    efficiency = max(0, min(100, 100 - saturation))
                    attrs.update(
                        {
                            "saturation": saturation,
                            "efficiency": efficiency,
                            "min_value": 0,
                            "max_value": 100,
                            "scale": "100-0 (decreasing)",
                        }
                    )
                except (TypeError, ValueError):
                    pass
            if device.filters:
                filter_data = device.filters[0]
                attrs.update(
                    {
                        "filter_id": filter_data.id,
                        "filter_type": filter_data.type,
                        "filter_status": filter_data.status,
                        "saturation_alert": filter_data.saturation_alert,
                        "installation_date": filter_data.installation_date,
                        "last_reset": filter_data.last_reset,
                        "filter_model": filter_data.model,
                    }
                )
        return attrs


class UnknownCapabilitySensor(CapabilitySensor):
    """Elica unknown capability sensor."""

    def __init__(
        self,
        coordinator: ElicaConnectCoordinator,
        device_id: str,
        key: str,
    ) -> None:
        super().__init__(
            coordinator=coordinator,
            device_id=device_id,
            key=key,
            name=f"Capability {key}",
            icon="mdi:circle",
        )
