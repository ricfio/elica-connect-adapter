"""Base entity class."""

from homeassistant.helpers.entity import DeviceInfo
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .api.domain import Device
from .const import DOMAIN
from .coordinator import ElicaConnectCoordinator


class ElicaDeviceEntity(CoordinatorEntity[ElicaConnectCoordinator]):
    """Representation of Elica Device entity."""

    _attr_has_entity_name = True

    def __init__(self, coordinator: ElicaConnectCoordinator, device_id: str) -> None:
        """Initialize the entity."""
        super().__init__(coordinator)

        self.coordinator = coordinator
        self.device_id = device_id

        device = self.device
        self._attr_device_info = DeviceInfo(
            identifiers={(DOMAIN, device.uid)},
            name=device.name,
            manufacturer=device.manufacturer,
            model=device.model,
            model_id=device.model_id,
            serial_number=device.serial_number,
            sw_version=device.sw_version,
        )

    @property
    def device(self) -> Device:
        """Return the device."""
        return self.coordinator.get_device(self.device_id)
