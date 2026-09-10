"""Base classes for Elica Connect entities."""
from __future__ import annotations

from homeassistant.helpers.entity import DeviceInfo
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DOMAIN
from .coordinator import ElicaConnectCoordinator


class BaseEntity(CoordinatorEntity):
    """Base entity class for Elica Connect."""

    def __init__(
        self,
        coordinator: ElicaConnectCoordinator,
        device_id: str,
    ) -> None:
        """Initialize the base entity."""
        super().__init__(coordinator)
        self._device_id = device_id

    @property
    def device_info(self) -> DeviceInfo:
        """Return device info."""
        device = self.coordinator.get_device(self._device_id)
        return DeviceInfo(
            identifiers={(DOMAIN, self._device_id)},
            manufacturer=device.manufacturer,
            model=device.model,
            name=device.name,
            sw_version=device.sw_version,
        )
