"""Support for Elica sensors."""

from __future__ import annotations

import logging

# from .capability_sensor import CAPABILITY_SENSORS, CapabilitySensor
from .api.domain.capabilities import Capability
from homeassistant.components.sensor import SensorDeviceClass, SensorStateClass
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import PERCENTAGE
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity import EntityCategory
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import CAPABILITIES, DOMAIN
from .coordinator import ElicaConnectCoordinator
from .sensors.capability_sensor import CapabilitySensor, CAPABILITY_SENSORS
from .sensors.miscellaneous_sensors import ConnectivityStateSensor, MqttConnectionSensor
from .sensors.mqtt_sensors import MQTT_SENSORS, MqttStateSensor, MqttMessagesSensor

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
        [
            entities.append(sensor)
            for sensor in [
                ConnectivityStateSensor(coordinator, device_id),
                # MqttConnectionSensor(coordinator, device_id),
            ]
        ]

        # Add capability sensors for each device's dataModel values
        for key in device.data_model:
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

        # Add MQTT sensors
        entities.extend([
            MqttStateSensor(coordinator, device_id),
            MqttMessagesSensor(coordinator, device_id),
        ])

    async_add_entities(entities)
