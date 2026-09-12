"""Support for Elica sensors."""

from __future__ import annotations

import logging

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .api.domain.capabilities import Capability
from .const import DOMAIN
from .coordinator import ElicaConnectCoordinator
from .sensors.capability import UnknownCapabilitySensor
from .sensors.cloud_connectivity import CloudConnectivitySensor
from .sensors.definitions import CAPABILITY_SENSORS
from .sensors.info import DeviceInformationSensor
from .sensors.mqtt_connectivity import MqttConnectivitySensor
from .sensors.mqtt_messages import MqttMessagesSensor

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
        entities.append(CloudConnectivitySensor(coordinator, device_id))
        entities.append(DeviceInformationSensor(coordinator, device_id))

        # Add capability sensors for each device's dataModel values
        for key in device.data_model:
            # Skip some specific known capability sensors
            if key in [Capability.FAN_MODE]:
                continue
            if key in CAPABILITY_SENSORS:
                # Add known capability sensors
                definition = CAPABILITY_SENSORS[key]
                entities.append(definition.create_sensor(coordinator, device_id, key))
            else:
                # Add unknown capability sensors
                entities.append(UnknownCapabilitySensor(coordinator, device_id, key))

        # Add extra capability sensors
        entities.append(
            CAPABILITY_SENSORS[Capability.FAN_SHUTOFF_TIMER].create_sensor(
                coordinator, device_id, Capability.FAN_SHUTOFF_TIMER
            )
        )

        # Add MQTT sensors
        entities.extend(
            [
                MqttConnectivitySensor(coordinator, device_id),
                MqttMessagesSensor(coordinator, device_id),
            ]
        )

    async_add_entities(entities)
