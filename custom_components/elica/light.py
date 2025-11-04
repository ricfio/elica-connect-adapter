"""Support for Elica lights."""

from homeassistant.components.light import ColorMode, LightEntity
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity import DeviceInfo
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .connect.core import Controller
from .connect.domain import Capability, Device
from .const import DOMAIN
from .coordinator import ElicaDataUpdateCoordinator


async def async_setup_entry(hass: HomeAssistant, entry, async_add_entities):
    """Setup light entities."""
    entry_data = hass.data[DOMAIN][entry.entry_id]
    controller: Controller = entry_data["controller"]
    coordinator: ElicaDataUpdateCoordinator = entry_data["coordinator"]
    entities = [
        ElicaLight(controller, coordinator, device)
        for device in coordinator.data["devices"].values()
        if Capability.LIGHT_BRIGHTNESS in device.capabilities
    ]
    async_add_entities(entities)


class ElicaLight(CoordinatorEntity, LightEntity):
    """Representation of an Elica light."""

    def __init__(
        self,
        controller: Controller,
        coordinator: ElicaDataUpdateCoordinator,
        device: Device,
    ) -> None:
        """Initialize the light."""
        CoordinatorEntity.__init__(self, coordinator)
        LightEntity.__init__(self)
        self.coordinator = coordinator
        self._controller = controller
        self._device_id = device.id
        self._attr_name = "Light"
        self._attr_unique_id = f"elica_{device.id}_light"
        self._attr_supported_color_modes = {ColorMode.BRIGHTNESS}
        # self._attr_color_mode = ColorMode.BRIGHTNESS

    @property
    def _device(self) -> Device:
        return self.coordinator.get_device(self._device_id)

    @property
    def device_info(self) -> DeviceInfo:  # noqa: D102
        return DeviceInfo(
            identifiers={(DOMAIN, self._device.id)},
            manufacturer=self._device.manufacturer,
            model=self._device.model,
            model_id=self._device.model_id,
            name=self._device.name,
            serial_number=self._device.serial_number,
            sw_version=self._device.sw_version,
            # via_device=(DOMAIN, self._device.id),
        )

    @property
    def is_on(self) -> bool:
        """Return true if light is on."""
        return self._device.state.light_on

    @property
    def brightness(self) -> int | None:
        """Return the brightness of this light between 0..255."""
        return round((self._device.state.light_brightness / 100) * 255)

    async def async_turn_on(self, **kwargs) -> None:  # noqa: D102
        brightness = kwargs.get("brightness", self._attr_brightness) or 255
        brightness_pct = round((brightness / 255) * 100)
        accepted = await self._controller.set_light_brightness(
            self._device.id,
            brightness_pct,
        )
        if accepted:
            await self.coordinator.async_request_refresh()
        self.async_write_ha_state()

    async def async_turn_off(self, **kwargs) -> None:  # noqa: D102
        accepted = await self._controller.toggle_light(
            self._device.id,
            False,
        )
        if accepted:
            await self.coordinator.async_request_refresh()
        self.async_write_ha_state()
