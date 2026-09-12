"""Support for Elica sensors."""

from __future__ import annotations

import logging

from homeassistant.components.sensor import SensorDeviceClass, SensorStateClass
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .api.domain.capabilities import Capability
from .const import DOMAIN
from .coordinator import ElicaConnectCoordinator
from .sensors.capability import CAPABILITY_SENSORS, CapabilitySensor
from .sensors.connectivity import ConnectivitySensor
from .sensors.info import DeviceInformationSensor
from .sensors.mqtt import MqttMessagesSensor, MqttStateSensor

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(
    hass: HomeAssistant,
    config_entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up Elica sensors."""
    entry_data = hass.data[DOMAIN][config_entry.entry_id]
    coordinator: ElicaConnectCoordinator = entry_data["coordinator"]

    entities = []

    # Add MQTT diagnostic sensors for each device
    for device_id in coordinator.data["devices"]:
        device = coordinator.get_device(device_id)
        entities.append(ConnectivitySensor(coordinator, device_id))
        entities.append(DeviceInformationSensor(coordinator, device_id))

        # Add capability sensors for each device's dataModel values
        for key in device.data_model:
            # if key in (
            #     Capability.LIGHT_BRIGHTNESS,
            #     Capability.FAN_SPEED,
            #     Capability.FAN_MODE,
            #     Capability.FAN_BOOST,
            # ):
            #     continue
            if key in CAPABILITY_SENSORS:
                # Add known capability sensors
                definition = CAPABILITY_SENSORS[key]
                entities.append(
                    CapabilitySensor(
                        coordinator=coordinator,
                        device_id=device_id,
                        key=key,
                        name=definition.name,
                        icon=definition.icon,
                        device_class=definition.device_class,
                        state_class=definition.state_class,
                        native_unit=definition.native_unit,
                        entity_category=definition.entity_category,
                        translation_key=definition.translation_key,
                    )
                )
            else:
                # Add unknown capability sensors
                entities.append(
                    CapabilitySensor(
                        coordinator=coordinator,
                        device_id=device_id,
                        key=key,
                        name=f"Capability {key}",
                        icon="mdi:circle",
                        device_class=None,
                        state_class=None,
                        native_unit=None,
                        entity_category=None,
                    )
                )

        # Add extra capability sensors
        entities.extend(
            [
                CapabilitySensor(
                    coordinator=coordinator,
                    device_id=device_id,
                    key=Capability.FAN_SHUTOFF_TIMER,
                    name="Fan Shut-off Timer",
                    icon="mdi:timer-sand",
                    device_class=SensorDeviceClass.DURATION,
                    state_class=SensorStateClass.MEASUREMENT,
                    native_unit="min",
                    translation_key="fan_shutoff_timer",
                ),
            ]
        )

        # Add MQTT sensors
        entities.extend(
            [
                MqttStateSensor(coordinator, device_id),
                MqttMessagesSensor(coordinator, device_id),
            ]
        )

    async_add_entities(entities)
