"""Support for Elica lights."""

from homeassistant.components.light import ColorMode, LightEntity
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity import DeviceInfo

from .const import DOMAIN
from .coordinator import ElicaDataUpdateCoordinator
from .elica_connect.api.client import ElicaClient
from .elica_connect.domain import Capability, Device


async def async_setup_entry(hass: HomeAssistant, entry, async_add_entities):
    """Set up Elica light entities."""
    entry_data = hass.data[DOMAIN][entry.entry_id]
    coordinator: ElicaDataUpdateCoordinator = entry_data["coordinator"]
    client: ElicaClient = entry_data["client"]

    # devices: list[Device] = entry_data["devices"]
    devices: list[Device] = coordinator.data
    entities = []
    for device in devices:
        if Capability.LIGHT_BRIGHTNESS in device.capabilities:
            entities.append(ElicaLight(client, coordinator, device))
    async_add_entities(entities)


class ElicaLight(LightEntity):
    """Representation of an Elica light."""

    def __init__(
        self,
        client: ElicaClient,
        coordinator: ElicaDataUpdateCoordinator,
        device: Device,
    ) -> None:  # noqa: D107
        self.coordinator = coordinator
        self._client = client
        self._device_id = device.id
        self._attr_unique_id = f"elica_{device.id}_light"
        self._attr_name = f"{device.name} Light"
        self._attr_supported_color_modes = {ColorMode.BRIGHTNESS}
        self._attr_color_mode = ColorMode.BRIGHTNESS
        self._attr_is_on = device.state.light_on
        self._attr_brightness = round((device.state.light_brightness / 100) * 255)

    @property
    def _device(self) -> Device:
        return self.coordinator.get_device(self._device_id)

    @property
    def name(self) -> str:
        return f"{self._device.name} Light"

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
    def brightness(self) -> int | None:
        return round((self._device.state.light_brightness / 100) * 255)

    @property
    def is_on(self) -> bool:
        return self._device.state.light_on

    @property
    def supported_color_modes(self) -> set[ColorMode]:
        return {ColorMode.BRIGHTNESS}

    @property
    def color_mode(self) -> ColorMode:
        return ColorMode.BRIGHTNESS

    async def async_turn_on(self, **kwargs) -> None:  # noqa: D102
        brightness = kwargs.get("brightness", self._attr_brightness) or 255
        brightness_pct = round((brightness / 255) * 100)
        accepted = await self.hass.async_add_executor_job(
            self._client.set_light_brightness,
            self._device,
            brightness_pct,
        )
        if accepted:
            await self.coordinator.async_request_refresh()
        self.async_write_ha_state()

    async def async_turn_off(self, **kwargs) -> None:  # noqa: D102
        accepted = await self.hass.async_add_executor_job(
            self._client.turn_off_light, self._device
        )
        if accepted:
            await self.coordinator.async_request_refresh()
        self.async_write_ha_state()
