"""Capability sensor entities for Elica Connect."""

from __future__ import annotations

import logging
from dataclasses import dataclass
from typing import Final

from homeassistant.components.sensor import SensorDeviceClass, SensorStateClass
from homeassistant.const import PERCENTAGE
from homeassistant.helpers.entity import EntityCategory

from ..api.domain.capabilities import Capability
from ..coordinator import ElicaConnectCoordinator
from .base import ElicaSensor

_LOGGER = logging.getLogger(__name__)


@dataclass
class CapabilitySensorDefinition:
    """Definition of a device capability sensor."""

    name: str
    icon: str
    device_class: SensorDeviceClass | None = None
    state_class: SensorStateClass | None = None
    native_unit: str | None = None
    entity_category: EntityCategory | None = None
    translation_key: str | None = None


# Mapping of known dataModel values to sensor definitions
CAPABILITY_SENSORS: Final = {
    # Light brightness (skipped because integrated into light entity)
    Capability.LIGHT_BRIGHTNESS: CapabilitySensorDefinition(
        name="Light Brightness",
        icon="mdi:brightness-percent",
        state_class=SensorStateClass.MEASUREMENT,
        native_unit=PERCENTAGE,
        translation_key="light_brightness",
    ),
    # Fan mode (skipped because integrated into fan entity)
    Capability.FAN_MODE: CapabilitySensorDefinition(
        name="Fan Mode",
        icon="mdi:fan",
        state_class=SensorStateClass.MEASUREMENT,
        translation_key="fan_mode",
    ),
    # Fan speed (skipped because integrated into fan entity)
    Capability.FAN_SPEED: CapabilitySensorDefinition(
        name="Fan Speed",
        icon="mdi:fan-speed-1",
        state_class=SensorStateClass.MEASUREMENT,
        translation_key="fan_speed",
    ),
    Capability.FAN_BOOST: CapabilitySensorDefinition(
        name="Boost Timer",
        icon="mdi:timer-sand",
        device_class=SensorDeviceClass.DURATION,
        state_class=SensorStateClass.MEASUREMENT,
        native_unit="min",
        translation_key="fan_boost_timer",
    ),
    Capability.FILTER_SATURATION: CapabilitySensorDefinition(
        name="Grease Filter Efficiency",
        icon="mdi:air-filter",
        state_class=SensorStateClass.MEASUREMENT,
        native_unit=PERCENTAGE,
        entity_category=EntityCategory.DIAGNOSTIC,
        translation_key="grease_filter_efficiency",
    ),
}


class CapabilitySensor(ElicaSensor):
    """Elica capability sensor."""

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
        translation_key: str | None = None,
    ) -> None:
        super().__init__(
            coordinator=coordinator,
            device_id=device_id,
            name=name,
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
        attrs = {
            "capability_id": self._key,
        }
        device = self.coordinator.get_device(self.device_id)
        if device and self._key == Capability.FILTER_SATURATION:
            raw_val = device.data_model.get(self._key)
            if raw_val is not None:
                try:
                    saturation = max(0, min(100, int(raw_val)))
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
