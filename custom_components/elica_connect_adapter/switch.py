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
    entities = []
    for device in coordinator.data["devices"].values():
        if Capability.FAN_SPEED in device.capabilities:
            entities.append(ElicaAirmaticSwitch(controller, coordinator, device))
            entities.append(ElicaBoostSwitch(controller, coordinator, device))
            # entities.append(ElicaShutoffTimerSwitch(controller, coordinator, device))
    async_add_entities(entities)


class ElicaAirmaticSwitch(ElicaDeviceEntity, SwitchEntity):
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
        self._attr_icon = "mdi:fan-auto"

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
        accepted = await self._controller.toggle_airmatic(
            self.device.uid,
            enable,
        )
        if accepted:
            self.device.set_airmatic_optimistic(enable)
        self.async_write_ha_state()


class ElicaBoostSwitch(ElicaDeviceEntity, SwitchEntity):
    """Representation of an Elica Boost switch."""

    def __init__(
        self,
        controller: Controller,
        coordinator: ElicaConnectCoordinator,
        device: Device,
    ) -> None:
        """Initialize the switch."""
        super().__init__(coordinator, device.uid)
        self._controller = controller
        self._attr_translation_key = "boost"
        self._attr_unique_id = f"elica_{device.uid}_boost"
        self._attr_icon = "mdi:rocket-launch"

    @property
    def is_on(self) -> bool:
        """Return True if Boost mode is active."""
        return self.device.state.fan_boost

    async def async_turn_on(self, **kwargs):
        """Turn on Boost."""
        await self._async_toggle(True)

    async def async_turn_off(self, **kwargs):
        """Turn off Boost."""
        await self._async_toggle(False)

    async def _async_toggle(self, enable: bool):
        """Internal helper to toggle Boost mode."""
        accepted = await self._controller.toggle_boost(
            self.device.uid,
            enable,
        )
        if accepted:
            self.device.set_fan_boost_optimistic(enable)
        self.async_write_ha_state()


class ElicaShutoffTimerSwitch(ElicaDeviceEntity, SwitchEntity):
    """Representation of an Elica Shut-off Timer switch (Start/Stop)."""

    def __init__(
        self,
        controller: Controller,
        coordinator: ElicaConnectCoordinator,
        device: Device,
    ) -> None:
        """Initialize the switch."""
        super().__init__(coordinator, device.uid)
        self._controller = controller
        self._attr_translation_key = "shutoff_timer_switch"
        self._attr_unique_id = f"elica_{device.uid}_shutoff_timer_switch"
        self._attr_icon = "mdi:timer-play"

    @property
    def is_on(self) -> bool:
        """Return True if Shut-off Timer is active (> 0)."""
        return self.device.state.shutoff_timer > 0

    async def async_turn_on(self, **kwargs):
        """Turn on Shut-off Timer (starts with current number value or default 15 min)."""
        minutes = (
            self.device.state.shutoff_timer
            if self.device.state.shutoff_timer > 0
            else 15
        )
        accepted = await self._controller.set_fan_shutoff_timer(
            self.device.uid, minutes
        )
        if accepted:
            self.device.state.shutoff_timer = minutes
        self.async_write_ha_state()
        await self.coordinator.async_request_refresh()

    async def async_turn_off(self, **kwargs):
        """Turn off Shut-off Timer (stops / sets to 0)."""
        accepted = await self._controller.set_fan_shutoff_timer(self.device.uid, 0)
        if accepted:
            self.device.state.shutoff_timer = 0
        self.async_write_ha_state()
        await self.coordinator.async_request_refresh()
