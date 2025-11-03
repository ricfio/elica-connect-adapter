"""Support for Elica fans."""

from __future__ import annotations

from homeassistant.components.fan import FanEntity, FanEntityFeature
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity import DeviceInfo

from .const import DOMAIN
from .coordinator import ElicaDataUpdateCoordinator
from .elica_connect.api.client import ElicaClient
from .elica_connect.domain import Capability, Device


async def async_setup_entry(hass: HomeAssistant, entry, async_add_entities):
    """Set up Elica fan entities."""
    entry_data = hass.data[DOMAIN][entry.entry_id]
    coordinator: ElicaDataUpdateCoordinator = entry_data["coordinator"]
    client: ElicaClient = entry_data["client"]

    devices: list[Device] = coordinator.data
    entities = [
        ElicaFan(client, coordinator, device)
        for device in devices
        if Capability.FAN_SPEED in device.capabilities
    ]
    async_add_entities(entities)


class ElicaFan(FanEntity):
    """Representation of an Elica fan."""

    _attr_supported_features = (
        FanEntityFeature.SET_SPEED
        | FanEntityFeature.TURN_OFF
        | FanEntityFeature.TURN_ON
    )
    _attr_speed_count = 3  # 1–2–3

    def __init__(
        self,
        client: ElicaClient,
        coordinator: ElicaDataUpdateCoordinator,
        device: Device,
    ) -> None:
        self._client = client
        self.coordinator = coordinator
        self._device_id = device.id

        self._attr_unique_id = f"elica_{device.id}_fan"
        self._attr_icon = "mdi:fan"

    @property
    def _device(self) -> Device:
        return self.coordinator.get_device(self._device_id)

    @property
    def name(self) -> str:
        return f"{self._device.name} Fan"

    @property
    def device_info(self) -> DeviceInfo:
        return DeviceInfo(
            identifiers={(DOMAIN, self._device.id)},
            manufacturer=self._device.manufacturer,
            model=self._device.model,
            model_id=self._device.model_id,
            name=self._device.name,
            serial_number=self._device.serial_number,
            sw_version=self._device.sw_version,
        )

    @property
    def is_on(self) -> bool:
        return self._device.state.fan_on

    @property
    def percentage(self) -> int:
        """Return fan speed as percentage (0-100)."""
        speed = self._device.state.fan_speed or 1
        return round((speed / self._attr_speed_count) * 100)

    async def async_turn_on(
        self, percentage: int | None = None, preset_mode: str | None = None, **kwargs
    ):
        if percentage is None:
            percentage = self.percentage
        await self.hass.async_add_executor_job(self._set_fan_mode, percentage)
        await self.coordinator.async_request_refresh()
        self.async_write_ha_state()

    async def async_turn_off(self, **kwargs):
        await self.hass.async_add_executor_job(self._set_fan_mode, 0)
        await self.coordinator.async_request_refresh()
        self.async_write_ha_state()

    async def async_set_percentage(self, percentage: int):
        await self.hass.async_add_executor_job(self._set_fan_mode, percentage)
        await self.coordinator.async_request_refresh()
        self.async_write_ha_state()

    def _set_fan_mode(self, percentage: int):
        speed = self._calculate_speed(percentage)
        device = self._device
        intensive = device.state.fan_boost
        aimatic = device.state.aimatic
        self._client.set_fan_mode(device, min(speed, 3), intensive, aimatic)

    def _calculate_speed(self, percentage: int) -> int:
        """Convert percentage (0-100) to fan speed level (0-3)."""
        speed = round((percentage / 100) * self._attr_speed_count)
        return max(0, min(self._attr_speed_count, speed))

    # def _calculate_percentage(self, speed: int) -> int:
    #     """Convert fan speed level (0-3) to percentage (0-100)."""
    #     return round((speed / self._attr_speed_count) * 100)
