"""Support for Elica switches."""

from homeassistant.components.switch import SwitchEntity
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity import DeviceInfo

from .const import DOMAIN
from .coordinator import ElicaDataUpdateCoordinator
from .elica_connect.api.client import ElicaClient
from .elica_connect.domain import Capability, Device


async def async_setup_entry(hass: HomeAssistant, entry, async_add_entities):
    """Set up switch entities."""
    entry_data = hass.data[DOMAIN][entry.entry_id]
    coordinator: ElicaDataUpdateCoordinator = entry_data["coordinator"]
    client: ElicaClient = entry_data["client"]

    # devices: list[Device] = entry_data["devices"]
    devices: list[Device] = coordinator.data
    entities = []
    for device in devices:
        if Capability.FAN_SPEED in device.capabilities:
            entities.append(ElicaAIMaticSwitch(client, coordinator, device))
    async_add_entities(entities)


class ElicaAIMaticSwitch(SwitchEntity):
    """Representation of an Elica AIMatic switch."""

    def __init__(
        self,
        client: ElicaClient,
        coordinator: ElicaDataUpdateCoordinator,
        device: Device,
    ) -> None:
        self.coordinator = coordinator
        self._client = client
        self._device_id = device.id
        self._attr_unique_id = f"elica_{device.id}_aimatic"
        self._attr_icon = "mdi:fan"

    @property
    def _device(self) -> Device:
        return self.coordinator.get_device(self._device_id)

    @property
    def name(self) -> str:
        return f"{self._device.name} AIMatic"

    @property
    def device_info(self) -> DeviceInfo:  # noqa: D102
        return DeviceInfo(
            identifiers={(DOMAIN, self._device.id)},  # chiave unica del device
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
        """Return True if AIMatic mode is active."""
        return self._device.state.aimatic

    async def async_turn_on(self, **kwargs):
        """Turn on AIMatic."""
        await self._async_toggle(True)

    async def async_turn_off(self, **kwargs):
        """Turn off AIMatic."""
        await self._async_toggle(False)

    async def _async_toggle(self, enable: bool):
        """Internal helper to toggle AIMatic mode."""
        await self.hass.async_add_executor_job(
            self._client.toggle_aimatic,
            self._device,
            enable,
        )
        await self.coordinator.async_request_refresh()
        self.async_write_ha_state()
