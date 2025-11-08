"""Base entity class."""

from elica_connect_api.domain import Device
from homeassistant.helpers.entity import DeviceInfo
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DOMAIN
from .coordinator import ElicaConnectCoordinator


class BaseEntity(CoordinatorEntity[ElicaConnectCoordinator]):
    """Base entity class for Elica devices."""

    _attr_has_entity_name = True

    def __init__(self, coordinator: ElicaConnectCoordinator, device) -> None:
        """Initialize the entity."""
        super().__init__(coordinator)

        self._device_id = device.id

        # Device info should be set only once per physical device
        self._attr_device_info = DeviceInfo(
            identifiers={(DOMAIN, device.id)},
            name=device.name,
            manufacturer="Elica",
            model=getattr(device, "model", None),
            sw_version=getattr(device, "firmware_version", None),
            # Optional: if you have hw_version
            hw_version=getattr(device, "hardware_version", None),
        )

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
