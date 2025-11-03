"""Data update coordinator for Elica Connect integration."""

from datetime import timedelta
from functools import cached_property
import logging

from homeassistant.core import HomeAssistant
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

from .const import DOMAIN
from .elica_connect.api.client import ElicaClient
from .elica_connect.domain.device import Device

_LOGGER = logging.getLogger(__name__)

SCAN_INTERVAL = timedelta(seconds=60)


class ElicaDataUpdateCoordinator(DataUpdateCoordinator[list[Device]]):
    """Coordinator to fetch Elica devices data periodically."""

    def __init__(self, hass: HomeAssistant, client: ElicaClient) -> None:
        """Initialize the coordinator."""
        super().__init__(
            hass,
            _LOGGER,
            name=f"{DOMAIN}_coordinator",
            update_interval=SCAN_INTERVAL,
        )
        self.client = client

    @cached_property
    def device_map(self) -> dict[str, Device]:
        """Return a map of device_id -> Device for quick lookup."""
        return {d.id: d for d in self.data or []}

    def get_device(self, device_id: str) -> Device:
        """Return a device by id, or None if not found."""
        device = self.device_map.get(device_id)
        if device is None:
            raise RuntimeError(f"Device {device_id} not found in coordinator")
        return device

    async def _async_update_data(self) -> list[Device]:
        """Fetch latest devices and their states from the API."""
        try:
            _LOGGER.debug("Fetching devices from Elica Connect API")
            return await self.hass.async_add_executor_job(self.client.get_devices)
        except Exception as err:
            raise UpdateFailed(f"Error while fetching devices: {err}") from err
