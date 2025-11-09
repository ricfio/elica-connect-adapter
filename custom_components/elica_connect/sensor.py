"""Support for Elica sensors."""

from __future__ import annotations

import logging

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

# from .capability_sensor import CAPABILITY_SENSORS, CapabilitySensor
from .const import DOMAIN
from .coordinator import ElicaConnectCoordinator
from .sensors.miscellaneous_sensors import ConnectivityStateSensor, MqttConnectionSensor
from .sensors.mqtt_sensors import MQTT_SENSORS, MqttDiagnosticSensor

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
        # device = coordinator.get_device(device_id)
        [
            entities.append(sensor)
            for sensor in [
                ConnectivityStateSensor(coordinator, device_id),
                # MqttConnectionSensor(coordinator, device_id),
            ]
        ]

        # [
        #     entities.append(sensor)
        #     for sensor in [
        #         CapabilitySensor(
        #             coordinator,
        #             device_id,
        #             Capability.LIGHT_BRIGHTNESS,
        #             "Light brightness",
        #         ),
        #     ]
        # ]

        # Add capability sensors for each device's dataModel values

        # Add capability sensors for each device's dataModel values
        # if hasattr(device, "capabilities"):
        #     _LOGGER.debug(
        #         "Device %s has capabilities: %s", device_id, device.capabilities
        #     )
        #     for key in device.capabilities:
        #         if str(key) in CAPABILITY_SENSORS:
        #             definition = CAPABILITY_SENSORS[str(key)]
        #             _LOGGER.debug(
        #                 "Creating capability sensor for key %s with definition: %s",
        #                 key,
        #                 definition,
        #             )
        #             entities.append(
        #                 CapabilitySensor(
        #                     coordinator=coordinator,
        #                     device_id=device_id,
        #                     # key=key,
        #                     key=definition.name,
        #                     name=definition.name,
        #                     icon=definition.icon,
        #                     device_class=definition.device_class,
        #                     state_class=definition.state_class,
        #                     native_unit=definition.native_unit,
        #                     entity_category=definition.entity_category,
        #                 )
        #             )
        #         else:
        #             _LOGGER.debug("No definition found for capability key: %s", key)

        for key, definition in MQTT_SENSORS.items():
            entities.append(
                MqttDiagnosticSensor(
                    coordinator=coordinator,
                    device_id=device_id,
                    key=key,
                    name=definition.name,
                    icon=definition.icon,
                    device_class=definition.device_class,
                    state_class=definition.state_class,
                    native_unit=definition.native_unit,
                )
            )

    async_add_entities(entities)
