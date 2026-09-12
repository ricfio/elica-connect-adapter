"""Sensor definitions for Elica Connect capabilities."""

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING, Final

from homeassistant.components.sensor import SensorDeviceClass, SensorStateClass
from homeassistant.const import PERCENTAGE
from homeassistant.helpers.entity import EntityCategory

from ..api.domain.capabilities import Capability

if TYPE_CHECKING:
    from ..coordinator import ElicaConnectCoordinator
    from .capability import CapabilitySensor


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

    def create_sensor(
        self,
        coordinator: ElicaConnectCoordinator,
        device_id: str,
        key: str,
    ) -> CapabilitySensor:
        """Create a CapabilitySensor instance from this definition."""
        from .capability import CapabilitySensor

        return CapabilitySensor(
            coordinator=coordinator,
            device_id=device_id,
            key=key,
            name=self.name,
            icon=self.icon,
            device_class=self.device_class,
            state_class=self.state_class,
            native_unit=self.native_unit,
            entity_category=self.entity_category,
            translation_key=self.translation_key,
        )


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
    Capability.FAN_SHUTOFF_TIMER: CapabilitySensorDefinition(
        name="Fan Shut-off Timer",
        icon="mdi:timer-sand",
        device_class=SensorDeviceClass.DURATION,
        state_class=SensorStateClass.MEASUREMENT,
        native_unit="min",
        translation_key="fan_shutoff_timer",
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
