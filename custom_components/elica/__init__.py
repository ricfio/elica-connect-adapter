"""The Elica Connect integration."""

from __future__ import annotations

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import Platform
from homeassistant.core import HomeAssistant

from .const import DOMAIN
from .coordinator import ElicaDataUpdateCoordinator
from .utils import create_client

PLATFORMS: list[Platform] = [
    Platform.FAN,
    Platform.LIGHT,
    Platform.SWITCH,
]


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up Elica Connect from a config entry."""

    client = create_client(entry.data["username"], entry.data["password"])

    # Effettuiamo il login con username/password dell'entry
    await hass.async_add_executor_job(
        client.login,
        # entry.data["username"],
        # entry.data["password"],
        # entry.data.get("app_uuid", "home-assistant"),
    )

    if not client.is_logged_in():
        return False

    coordinator = ElicaDataUpdateCoordinator(hass, client)
    await coordinator.async_config_entry_first_refresh()

    # devices = await hass.async_add_executor_job(client.get_devices)

    # Cache client and devices
    hass.data.setdefault(DOMAIN, {})
    hass.data[DOMAIN][entry.entry_id] = {
        "client": client,
        # "devices": devices,
        "coordinator": coordinator,
    }

    # Setup all the platforms (es. light, fan, switch, etc.)
    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)
    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload a config entry."""
    unload_ok = await hass.config_entries.async_unload_platforms(entry, PLATFORMS)
    if unload_ok:
        hass.data[DOMAIN].pop(entry.entry_id)
    return unload_ok
