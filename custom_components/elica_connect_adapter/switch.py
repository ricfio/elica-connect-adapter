"""Support for Elica switches."""

from homeassistant.components.switch import SwitchEntity
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity import DeviceInfo
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .api.core import Controller
from .api.domain import Capability, Device
from .const import DOMAIN
from .coordinator import ElicaConnectCoordinator
from .entity import ElicaDeviceEntity


async def async_setup_entry(hass: HomeAssistant, entry, async_add_entities):
    """Set up switch entities."""
    entry_data = hass.data[DOMAIN][entry.entry_id]
    controller: Controller = entry_data["controller"]
    coordinator: ElicaConnectCoordinator = entry_data["coordinator"]
    entities = [
        ElicaAirMaticSwitch(controller, coordinator, device)
        for device in coordinator.data["devices"].values()
        if Capability.FAN_SPEED in device.capabilities
    ]
    async_add_entities(entities)


class ElicaAirMaticSwitch(ElicaDeviceEntity, SwitchEntity):
    """Representation of an Elica Airmatic switch."""

    def __init__(
        self,
        controller: Controller,
        coordinator: ElicaConnectCoordinator,
        device: Device,
    ) -> None:
        """Initialize the switch."""
        super().__init__(coordinator, device.uid)
        self._controller = controller
        self._attr_translation_key = "airmatic"
        self._attr_unique_id = f"elica_{device.uid}_airmatic"
        self._attr_icon = "mdi:fan"

    @property
    def is_on(self) -> bool:
        """Return True if Airmatic mode is active."""
        return self.device.state.airmatic

    async def async_turn_on(self, **kwargs):
        """Turn on Airmatic."""
        await self._async_toggle(True)

    async def async_turn_off(self, **kwargs):
        """Turn off Airmatic."""
        await self._async_toggle(False)

    async def _async_toggle(self, enable: bool):
        """Internal helper to toggle Airmatic mode."""
        await self._controller.toggle_airmatic(
            self.device.uid,
            enable,
        )
        await self.coordinator.async_request_refresh()
        self.async_write_ha_state()
