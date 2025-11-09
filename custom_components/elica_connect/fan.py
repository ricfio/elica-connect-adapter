"""Support for Elica fans."""

from __future__ import annotations

from elica_connect_api.core import Controller
from elica_connect_api.domain import Capability, Device
from homeassistant.components.fan import FanEntity, FanEntityFeature
from homeassistant.core import HomeAssistant

from .const import DOMAIN
from .coordinator import ElicaConnectCoordinator
from .entity import ElicaDeviceEntity


async def async_setup_entry(hass: HomeAssistant, entry, async_add_entities):
    """Setup fan entities."""
    entry_data = hass.data[DOMAIN][entry.entry_id]
    controller: Controller = entry_data["controller"]
    coordinator: ElicaConnectCoordinator = entry_data["coordinator"]
    entities = [
        ElicaFan(controller, coordinator, device)
        for device in coordinator.data["devices"].values()
        if Capability.FAN_SPEED in device.capabilities
    ]
    async_add_entities(entities)


class ElicaFan(ElicaDeviceEntity, FanEntity):
    """Representation of Elica hood fan."""

    _attr_supported_features = (
        FanEntityFeature.SET_SPEED
        | FanEntityFeature.TURN_OFF
        | FanEntityFeature.TURN_ON
    )
    _attr_speed_count = 3  # 1–2–3

    def __init__(
        self,
        controller: Controller,
        coordinator: ElicaConnectCoordinator,
        device: Device,
    ) -> None:
        """Initialize the fan entity."""
        super().__init__(coordinator, device.id)

        self.coordinator = coordinator
        self._controller = controller
        self._device_id = device.id
        self._attr_unique_id = f"elica_{device.id}_fan"
        self._attr_name = "Fan"
        self._attr_icon = "mdi:fan"

    @property
    def is_on(self) -> bool:
        """Return true if fan is on."""
        return self.device.state.fan_on

    @property
    def percentage(self) -> int:
        """Return fan speed as percentage (0-100)."""
        speed = self.device.state.fan_speed
        return round((speed / self._attr_speed_count) * 100)

    async def async_turn_on(
        self, percentage: int | None = None, preset_mode: str | None = None, **kwargs
    ):
        """Turn the fan on."""
        if percentage is None:
            percentage = self.percentage
        accepted = await self._set_fan_mode(percentage)
        if accepted:
            await self.coordinator.async_request_refresh()
        self.async_write_ha_state()

    async def async_turn_off(self, **kwargs):
        """Turn the fan off."""
        accepted = await self._set_fan_mode(0)
        if accepted:
            await self.coordinator.async_request_refresh()
        self.async_write_ha_state()

    async def async_set_percentage(self, percentage: int):
        """Set fan speed as percentage (0-100)."""
        accepted = await self._set_fan_mode(percentage)
        if accepted:
            await self.coordinator.async_request_refresh()
        self.async_write_ha_state()

    async def _set_fan_mode(self, percentage: int):
        speed = self._calculate_speed(percentage)
        device = self.device
        intensive = device.state.fan_boost
        aimatic = device.state.aimatic
        await self._controller.set_fan_mode(
            device.id, aimatic, min(speed, 3), intensive
        )

    def _calculate_speed(self, percentage: int) -> int:
        """Convert percentage (0-100) to fan speed level (0-3)."""
        speed = round((percentage / 100) * self._attr_speed_count)
        return max(0, min(self._attr_speed_count, speed))

    # def _calculate_percentage(self, speed: int) -> int:
    #     """Convert fan speed level (0-3) to percentage (0-100)."""
    #     return round((speed / self._attr_speed_count) * 100)
