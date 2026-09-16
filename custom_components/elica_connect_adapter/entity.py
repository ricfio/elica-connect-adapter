"""Base entity class."""

from homeassistant.helpers.entity import DeviceInfo
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .api.domain import Device
from .const import DOMAIN
from .coordinator import ElicaConnectCoordinator


class ElicaDeviceEntity(CoordinatorEntity[ElicaConnectCoordinator]):
    """Elica device entity base class."""

    _attr_has_entity_name = True

    def __init__(self, coordinator: ElicaConnectCoordinator, device_id: str) -> None:
        super().__init__(coordinator)

        self.coordinator = coordinator
        self.device_id = device_id

        device = self.device
        self._attr_device_info = DeviceInfo(
            configuration_url=device.product_url
            or device.metadata.get("productManualUrl"),
            # connections: set[tuple[str, str]]
            # entry_type: DeviceEntryType | None
            identifiers={(DOMAIN, device.uid)},
            manufacturer=device.manufacturer,
            model=device.commercial_name or device.product_reference or device.model,
            model_id=device.model_id,
            name=device.name,
            serial_number=device.serial_number,
            # suggested_area: str | None
            sw_version=device.sw_version,
            hw_version=device.installation_type,
            # translation_key: str | None
            # translation_placeholders: Mapping[str, str] | None
            # via_device_id: str
        )

    @property
    def device(self) -> Device:
        """Return the device."""
        return self.coordinator.get_device(self.device_id)
