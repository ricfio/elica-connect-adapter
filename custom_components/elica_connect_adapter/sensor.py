"""Support for Elica sensors."""

from __future__ import annotations

import logging

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .api.domain.capabilities import Capability
from .const import DOMAIN
from .coordinator import ElicaConnectCoordinator
from .sensors.base import ElicaSensor
from .sensors.capability import UnknownCapabilitySensor
from .sensors.cloud_connectivity import CloudConnectivitySensor
from .sensors.definitions import CAPABILITY_SENSORS
from .sensors.details import DeviceDetailsSensor
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

    entities: list[ElicaSensor] = []

    # Add sensors for each device
    for device_id in coordinator.data["devices"]:
        entities.extend(
            [
                DeviceDetailsSensor(coordinator, device_id),
                CloudConnectivitySensor(coordinator, device_id),
                MqttConnectivitySensor(coordinator, device_id),
                MqttMessagesSensor(coordinator, device_id),
            ]
        )

        # Add setup capability sensors
        device = coordinator.get_device(device_id)
        for key in device.data_model:
            # Skip some known specific capability sensors
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

    async_add_entities(entities)
