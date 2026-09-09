"""Support for Elica switches."""

from .api.core import Controller
from .api.domain import Capability, Device
from homeassistant.components.switch import SwitchEntity
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity import DeviceInfo
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DOMAIN
from .coordinator import ElicaConnectCoordinator
from .entity import ElicaDeviceEntity


async def async_setup_entry(hass: HomeAssistant, entry, async_add_entities):
    """Set up switch entities."""
    entry_data = hass.data[DOMAIN][entry.entry_id]
    controller: Controller = entry_data["controller"]
    coordinator: ElicaConnectCoordinator = entry_data["coordinator"]
    entities = [
        ElicaAIMaticSwitch(controller, coordinator, device)
        for device in coordinator.data["devices"].values()
        if Capability.FAN_SPEED in device.capabilities
    ]
    async_add_entities(entities)


class ElicaAIMaticSwitch(ElicaDeviceEntity, SwitchEntity):
    """Representation of an Elica AIMatic switch."""

    def __init__(
        self,
        controller: Controller,
        coordinator: ElicaConnectCoordinator,
        device: Device,
    ) -> None:
        """Initialize the switch."""
        super().__init__(coordinator, device.uid)
        self._controller = controller
        self._attr_translation_key = "aimatic"
        self._attr_unique_id = f"elica_{device.uid}_aimatic"
        self._attr_icon = "mdi:fan"

    @property
    def is_on(self) -> bool:
        """Return True if AIMatic mode is active."""
        return self.device.state.aimatic

    async def async_turn_on(self, **kwargs):
        """Turn on AIMatic."""
        await self._async_toggle(True)

    async def async_turn_off(self, **kwargs):
        """Turn off AIMatic."""
        await self._async_toggle(False)

    async def _async_toggle(self, enable: bool):
        """Internal helper to toggle AIMatic mode."""
        await self._controller.toggle_aimatic(
            self.device.uid,
            enable,
        )
        await self.coordinator.async_request_refresh()
        self.async_write_ha_state()
