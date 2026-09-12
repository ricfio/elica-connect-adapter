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
    """Representation of Elica hood fan."""

    _attr_supported_features = (
        FanEntityFeature.SET_SPEED
        | FanEntityFeature.PRESET_MODE
        | FanEntityFeature.TURN_OFF
        | FanEntityFeature.TURN_ON
    )
    _attr_speed_count = 3  # 1–2–3
    _attr_preset_modes = FAN_PRESET

    def __init__(
        self,
        controller: Controller,
        coordinator: ElicaConnectCoordinator,
        device: Device,
    ) -> None:
        """Initialize the fan entity."""
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
        speed = min(self.device.state.fan_speed, self._attr_speed_count)
        return round((speed / self._attr_speed_count) * 100)

    @property
    def preset_mode(self) -> str | None:
        """Return the current preset mode."""
        return FanPreset.BOOST if self.device.state.fan_boost else None

    async def async_turn_on(
        self, percentage: int | None = None, preset_mode: str | None = None, **kwargs
    ):
        """Turn the fan on."""
        if preset_mode == FanPreset.BOOST:
            accepted = await self._set_fan_mode(
                self._attr_speed_count,
                intensive=True,
            )
        else:
            if percentage is None or percentage == 0:
                percentage = (
                    self.percentage
                    if self.percentage > 0
                    else round((1 / self._attr_speed_count) * 100)
                )

            accepted = await self._set_fan_mode(
                percentage,
                intensive=False,
            )

        if accepted:
            if preset_mode == FanPreset.BOOST:
                self.device.set_fan_speed_optimistic(self._attr_speed_count)
                self.device.set_fan_boost_optimistic(True)
            else:
                speed = self._calculate_speed(percentage)
                self.device.set_fan_speed_optimistic(speed)
                self.device.set_fan_boost_optimistic(False)
        self.async_write_ha_state()

    async def async_turn_off(self, **kwargs):
        """Turn the fan off."""
        accepted = await self._set_fan_mode(
            0,
            intensive=False,
        )
        if accepted:
            self.device.set_fan_speed_optimistic(0)
            self.device.set_fan_boost_optimistic(False)
        self.async_write_ha_state()

    async def async_set_percentage(self, percentage: int):
        """Set fan speed as percentage (0-100)."""
        accepted = await self._set_fan_mode(
            percentage,
            intensive=False,
        )
        if accepted:
            speed = self._calculate_speed(percentage)
            self.device.set_fan_speed_optimistic(speed)
            self.device.set_fan_boost_optimistic(False)
        self.async_write_ha_state()

    async def async_set_preset_mode(self, preset_mode: str | None):
        """Set fan preset mode."""
        if preset_mode is not None and preset_mode != FanPreset.BOOST:
            raise ValueError(f"Unsupported preset mode: {preset_mode}")

        if preset_mode == FanPreset.BOOST:
            accepted = await self._set_fan_mode(
                100,
                intensive=True,
            )
        else:
            accepted = await self._set_fan_mode(
                self.percentage,
                intensive=False,
            )
        if accepted:
            is_boost = preset_mode == FanPreset.BOOST
            if is_boost:
                self.device.set_fan_speed_optimistic(self._attr_speed_count)
            self.device.set_fan_boost_optimistic(is_boost)
        self.async_write_ha_state()

    async def _set_fan_mode(self, percentage: int, intensive: bool):
        device = self.device
        airmatic = device.state.airmatic

        if intensive:
            speed = self._attr_speed_count
        else:
            speed = self._calculate_speed(percentage)

        return await self._controller.set_fan_mode(
            device.uid,
            airmatic,
            speed,
            intensive,
        )

    def _calculate_speed(self, percentage: int) -> int:
        """Convert percentage (0-100) to fan speed level (0-3)."""
        speed = round((percentage / 100) * self._attr_speed_count)
        return max(0, min(self._attr_speed_count, speed))
