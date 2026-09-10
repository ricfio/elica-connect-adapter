"""The Elica Connect integration."""

from __future__ import annotations

import logging

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import Platform
from homeassistant.core import HomeAssistant

from .const import DOMAIN
from .coordinator import ElicaConnectCoordinator
from .utils import create_controller

_LOGGER = logging.getLogger(__name__)

PLATFORMS: list[Platform] = [
    Platform.FAN,
    Platform.LIGHT,
    Platform.SENSOR,
    Platform.SWITCH,
]


async def async_setup(hass: HomeAssistant, config: dict):
    """Set up the Elica Connect integration (YAML)."""
    return True


async def async_setup_entry(hass: HomeAssistant, config_entry: ConfigEntry) -> bool:
    """Set up Elica Connect from a config entry."""

    controller = create_controller(
        hass, config_entry.data["username"], config_entry.data["password"]
    )

    try:
        await controller.login()
    except Exception as err:
        _LOGGER.exception("Failed to initialize Elica controller: %s", err)
        return False

    if not await controller.is_logged_in():
        _LOGGER.error("Authentication failed")
        return False

    coordinator = ElicaConnectCoordinator(hass, controller, config_entry)
    await coordinator.async_config_entry_first_refresh()

    # Cache client and devices
    domain_data = hass.data.setdefault(DOMAIN, {})
    domain_data[config_entry.entry_id] = {
        "controller": controller,
        "coordinator": coordinator,
    }

    # Setup update listener for options changes
    config_entry.async_on_unload(config_entry.add_update_listener(async_update_listener))

    # Setup all the platforms (es. light, fan, switch, etc.)
    await hass.config_entries.async_forward_entry_setups(config_entry, PLATFORMS)
    return True


async def async_update_listener(hass: HomeAssistant, config_entry: ConfigEntry) -> None:
    """Handle options update."""
    await hass.config_entries.async_reload(config_entry.entry_id)


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload a config entry."""
    entry_data = hass.data.get(DOMAIN, {}).get(entry.entry_id)
    if entry_data:
        await entry_data["controller"].stop_listening()

    unload_ok = await hass.config_entries.async_unload_platforms(entry, PLATFORMS)
    if unload_ok:
        hass.data[DOMAIN].pop(entry.entry_id)
    return unload_ok
