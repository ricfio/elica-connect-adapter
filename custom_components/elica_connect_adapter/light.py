"""Support for Elica lights."""

from .api.core import Controller
from .api.domain import Capability, Device
from homeassistant.components.light import ColorMode, LightEntity
from homeassistant.core import HomeAssistant

from .const import DOMAIN
from .coordinator import ElicaConnectCoordinator
from .entity import ElicaDeviceEntity


async def async_setup_entry(hass: HomeAssistant, entry, async_add_entities):
    """Setup light entities."""
    entry_data = hass.data[DOMAIN][entry.entry_id]
    controller: Controller = entry_data["controller"]
    coordinator: ElicaConnectCoordinator = entry_data["coordinator"]
    entities = [
        ElicaLight(controller, coordinator, device)
        for device in coordinator.data["devices"].values()
        if Capability.LIGHT_BRIGHTNESS in device.capabilities
    ]
    async_add_entities(entities)


class ElicaLight(ElicaDeviceEntity, LightEntity):
    """Representation of an Elica light."""

    def __init__(
        self,
        controller: Controller,
        coordinator: ElicaConnectCoordinator,
        device: Device,
    ) -> None:
        """Initialize the light."""
        ElicaDeviceEntity.__init__(self, coordinator, device.uid)
        LightEntity.__init__(self)
        self.coordinator = coordinator
        self._controller = controller
        self._device_id = device.uid
        self._attr_translation_key = "hood_light"
        self._attr_unique_id = f"elica_{device.uid}_light"
        self._attr_supported_color_modes = {ColorMode.BRIGHTNESS}
        self._attr_color_mode = ColorMode.BRIGHTNESS

    @property
    def is_on(self) -> bool:
        """Return true if light is on."""
        return self.device.state.light_on

    @property
    def brightness(self) -> int | None:
        """Return the brightness of this light between 0..255."""
        return round((self.device.state.light_brightness / 100) * 255)

    async def async_turn_on(self, **kwargs) -> None:  # noqa: D102
        brightness = kwargs.get("brightness", self._attr_brightness) or 255
        brightness_pct = round((brightness / 255) * 100)
        accepted = await self._controller.set_light_brightness(
            self.device.uid,
            brightness_pct,
        )
        if accepted:
            await self.coordinator.async_request_refresh()
        self.async_write_ha_state()

    async def async_turn_off(self, **kwargs) -> None:  # noqa: D102
        accepted = await self._controller.toggle_light(
            self.device.uid,
            False,
        )
        if accepted:
            await self.coordinator.async_request_refresh()
        self.async_write_ha_state()
