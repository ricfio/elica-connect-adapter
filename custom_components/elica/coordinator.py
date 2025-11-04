"""Data Update Coordinator for Elica."""

from datetime import timedelta
import logging
from typing import Any

from homeassistant.core import HomeAssistant
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

from .connect.core import Controller
from .connect.domain import Device
from .const import DOMAIN

_LOGGER = logging.getLogger(__name__)

SCAN_INTERVAL = timedelta(seconds=60)


class ElicaDataUpdateCoordinator(DataUpdateCoordinator[dict[str, Any]]):
    """Data Update Coordinator for Elica.

    self.data: dict with key "devices", value dict[str, Device]
    """

    def __init__(self, hass: HomeAssistant, controller: Controller) -> None:
        """Initialize the coordinator."""
        super().__init__(
            hass,
            _LOGGER,
            name=f"{DOMAIN}_coordinator",
            update_interval=SCAN_INTERVAL,
        )
        self.controller = controller

    def get_device(self, device_id: str) -> Device:
        """Return a device by id, or raise if not found."""
        try:
            return self.data["devices"][device_id]
        except KeyError as err:
            raise RuntimeError(f"Device {device_id} not found in coordinator") from err

    async def _async_update_data(self) -> dict[str, Any]:
        """Fetch latest devices and their states."""
        try:
            devices = await self.controller.get_devices()
            return {
                "devices": {device.id: device for device in devices},
            }
        except Exception as err:
            raise UpdateFailed(f"Error while fetching devices: {err}") from err
