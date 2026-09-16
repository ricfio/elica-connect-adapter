"""Support for Elica fans."""

from __future__ import annotations

from homeassistant.components.fan import FanEntity, FanEntityFeature
from homeassistant.core import HomeAssistant

from .api.core import Controller
from .api.domain import Capability, Device, FanPreset
from .const import DOMAIN, FAN_PRESET
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
    """Elica hood fan entity."""

    _attr_supported_features = (
        FanEntityFeature.SET_SPEED
        | FanEntityFeature.PRESET_MODE
        | FanEntityFeature.TURN_OFF
        | FanEntityFeature.TURN_ON
    )
    _attr_speed_count = 3  # 1–2–3 (discrete speed buttons)
    _attr_preset_modes = FAN_PRESET

    def __init__(
        self,
        controller: Controller,
        coordinator: ElicaConnectCoordinator,
        device: Device,
    ) -> None:
        super().__init__(coordinator, device.uid)

        self.coordinator = coordinator
        self._controller = controller
        self._device_id = device.uid
        self._attr_translation_key = "fan"
        self._attr_unique_id = f"elica_{device.uid}_fan"
        self._attr_icon = "mdi:fan"

    @property
    def is_on(self) -> bool:
        """Return true if fan is on."""
        return self.device.state.fan_on

    @property
    def percentage(self) -> int:
        """Return fan speed as percentage (0-100)."""
        if self.device.state.fan_boost:
            return 100

        return round((self.device.state.fan_speed / self._attr_speed_count) * 100)

    @property
    def preset_mode(self) -> str | None:
        """Return the current preset mode."""
        if self.device.state.fan_boost:
            return FanPreset.BOOST

        if self.device.state.fan_speed == 3:
            return FanPreset.HIGH

        if self.device.state.fan_speed == 2:
            return FanPreset.MEDIUM

        if self.device.state.fan_speed == 1:
            return FanPreset.LOW

        return None

    async def async_turn_on(
        self, percentage: int | None = None, preset_mode: str | None = None, **kwargs
    ):
        """Turn the fan on."""
        if preset_mode:
            await self.async_set_preset_mode(preset_mode)
            return

        if percentage is None or percentage == 0:
            percentage = (
                self.percentage
                if self.percentage > 0
                else round(1 / (self._attr_speed_count + 1) * 100)
            )

        await self.async_set_percentage(percentage)

    async def async_turn_off(self, **kwargs):
        """Turn the fan off."""
        accepted = await self._controller.set_fan_mode(
            self.device.uid,
            self.device.state.airmatic,
            0,
            False,
        )
        if accepted:
            self.device.set_fan_speed_optimistic(0)
            self.device.set_fan_boost_optimistic(False)
        self.async_write_ha_state()

    async def async_set_percentage(self, percentage: int):
        """Set fan percentage (0-100)."""
        speed = self._convert_percent_to_speed(percentage)
        intensive = False  # Speed changes via percentage never trigger boost

        accepted = await self._controller.set_fan_mode(
            self.device.uid,
            self.device.state.airmatic,
            speed,
            intensive,
        )
        if accepted:
            self.device.set_fan_speed_optimistic(speed)
            self.device.set_fan_boost_optimistic(intensive)
        self.async_write_ha_state()

    async def async_set_preset_mode(self, preset_mode: str | None):
        """Set fan preset mode."""
        if preset_mode == FanPreset.BOOST:
            speed = 3
            intensive = True
        elif preset_mode == FanPreset.HIGH:
            speed = 3
            intensive = False
        elif preset_mode == FanPreset.MEDIUM:
            speed = 2
            intensive = False
        elif preset_mode == FanPreset.LOW:
            speed = 1
            intensive = False
        else:
            speed = 0
            intensive = False

        accepted = await self._controller.set_fan_mode(
            self.device.uid,
            self.device.state.airmatic,
            speed,
            intensive,
        )
        if accepted:
            self.device.set_fan_speed_optimistic(speed)
            self.device.set_fan_boost_optimistic(intensive)
        self.async_write_ha_state()

    def _convert_percent_to_speed(self, percentage: int) -> int:
        """Convert percentage (0-100) to fan speed level (0-3)."""
        speed = round((self._attr_speed_count) * percentage / 100)

        return min(speed, self._attr_speed_count)
