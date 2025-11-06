"""The Elica Connect integration."""

from __future__ import annotations

import logging

from homeassistant.components import mqtt
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import Platform
from homeassistant.core import HomeAssistant

from .const import DOMAIN
from .coordinator import ElicaDataUpdateCoordinator
from .utils import create_controller

_LOGGER = logging.getLogger(__name__)

PLATFORMS: list[Platform] = [
    Platform.FAN,
    Platform.LIGHT,
    Platform.SWITCH,
]


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up Elica Connect from a config entry."""

    controller = create_controller(hass, entry.data["username"], entry.data["password"])

    await controller.login()

    if not await controller.is_logged_in():
        _LOGGER.error(
            "Authentication failed for user %s", entry.data["username"]
        )
        return False

    coordinator = ElicaDataUpdateCoordinator(hass, controller)
    await coordinator.async_config_entry_first_refresh()

    # Cache client and devices
    domain_data = hass.data.setdefault(DOMAIN, {})
    domain_data[entry.entry_id] = {
        "controller": controller,
        "coordinator": coordinator,
    }

    # Setup all the platforms (es. light, fan, switch, etc.)
    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)
    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload a config entry."""
    mqtt_unsubscribes = hass.data.get(DOMAIN, {}).pop("mqtt_unsubscribes", [])
    for unsubscribe in mqtt_unsubscribes:
        if unsubscribe:
            unsubscribe()

    unload_ok = await hass.config_entries.async_unload_platforms(entry, PLATFORMS)
    if unload_ok:
        hass.data[DOMAIN].pop(entry.entry_id)
    return unload_ok
