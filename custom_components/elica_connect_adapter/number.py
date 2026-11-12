"""Support for Elica number entities."""

from __future__ import annotations

from homeassistant.components.number import NumberEntity, NumberMode
from homeassistant.const import UnitOfTime
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .api.core import Controller
from .api.domain import Device
from .coordinator import ElicaConnectCoordinator
from .entity import ElicaDeviceEntity


async def async_setup_entry(
    hass: HomeAssistant, entry, async_add_entities: AddEntitiesCallback
):
    """Set up Elica number entities."""
    # entry_data = hass.data[DOMAIN][entry.entry_id]
    # controller: Controller = entry_data["controller"]
    # coordinator: ElicaConnectCoordinator = entry_data["coordinator"]
    # entities = [
    #     ElicaShutoffTimerNumber(controller, coordinator, device)
    #     for device in coordinator.data["devices"].values()
    #     if Capability.FAN_SPEED in device.capabilities
    # ]
    # async_add_entities(entities)


class ElicaShutoffTimerNumber(ElicaDeviceEntity, NumberEntity):
    """Elica fan shut-off timer number entity."""

    _attr_native_min_value = 0
    _attr_native_max_value = 180
    _attr_native_step = 1
    _attr_native_unit_of_measurement = UnitOfTime.MINUTES
    _attr_mode = NumberMode.BOX
    _attr_icon = "mdi:timer-sand"

    def __init__(
        self,
        controller: Controller,
        coordinator: ElicaConnectCoordinator,
        device: Device,
    ) -> None:
        super().__init__(coordinator, device.uid)
        self._controller = controller
        self._attr_translation_key = "shutoff_timer_number"
        self._attr_unique_id = f"elica_{device.uid}_shutoff_timer_number"

    @property
    def native_value(self) -> float:
        """Return the current set/remaining minutes."""
        return float(self.device.state.shutoff_timer)

    async def async_set_native_value(self, value: float) -> None:
        """Set the shut-off timer duration."""
        minutes = int(value)
        accepted = await self._controller.set_fan_shutoff_timer(
            self.device.uid, minutes
        )
        if accepted:
            self.device.state.shutoff_timer = minutes
            self.async_write_ha_state()
        await self.coordinator.async_request_refresh()
