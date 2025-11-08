"""Support for Elica sensors."""
from __future__ import annotations

import logging

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import DOMAIN

_LOGGER = logging.getLogger(__name__)
from .capability_sensor import CAPABILITY_SENSORS, CapabilitySensor
from .coordinator import ElicaConnectCoordinator
from .mqtt_sensor import MQTT_SENSORS, MqttDiagnosticSensor


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
    
        # Add capability sensors for each device's dataModel values
        # Add capability sensors for each device's dataModel values
        if hasattr(device, "dataModel"):
            _LOGGER.debug("Device %s has dataModel: %s", device_id, device.dataModel)
            for key in device.dataModel:
                if str(key) in CAPABILITY_SENSORS:
                    definition = CAPABILITY_SENSORS[str(key)]
                    _LOGGER.debug("Creating capability sensor for key %s with definition: %s",
                                key, definition)
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
                        )
                    )
                else:
                    _LOGGER.debug("No definition found for capability key: %s", key)

    async_add_entities(entities)