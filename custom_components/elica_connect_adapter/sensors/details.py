"""Device details sensor entity for Elica Connect."""

from __future__ import annotations

from typing import Any

from ..coordinator import ElicaConnectCoordinator
from .base import ElicaDiagnosticSensor


class DeviceDetailsSensor(ElicaDiagnosticSensor):
    """Elica device details sensor containing all extended metadata attributes."""

    def __init__(self, coordinator: ElicaConnectCoordinator, device_id: str) -> None:
        super().__init__(
            coordinator,
            device_id,
            icon="mdi:information-outline",
            translation_key="device_details",
        )
        self._attr_unique_id = f"elica_{device_id}_{self.translation_key}"

    @property
    def native_value(self) -> str:
        return self.device.uid if self.device else "unknown"

    @property
    def extra_state_attributes(self) -> dict[str, Any]:
        dev = self.device
        if not dev:
            return {}
        return {
            # Identifiers & References
            "id": dev.uid,
            "cuid": dev.cuid,
            "product_reference": dev.product_reference,
            # Status & Flags
            "iot": dev.metadata.get("iot"),
            "demo": dev.metadata.get("demo"),
            "is_legacy": dev.is_legacy,
            "never_connected": dev.never_connected,
            # Device Configuration & Specs
            "installation_type": dev.installation_type,
            "usage_frequency": dev.usage_frequency,
            "time_zone": dev.metadata.get("timeZone"),
            "purchase_date": dev.purchase_date,
            "data_model_idx": dev.metadata.get("dataModelIdx"),
            "has_snap_timer": dev.snap_timer is not None,
            "temperature_unit": dev.temperature.unit if dev.temperature else None,
            # Media & Links
            "media_type": dev.media.type if dev.media else None,
            "media_url": dev.media.url if dev.media else None,
            "product_manual_url": dev.metadata.get("productManualUrl"),
            "accessories_url": dev.metadata.get("accessoriesURL"),
            "auto_light_pause_interval": dev.metadata.get("autoLightPauseInterval"),
            # Ownership & Sharing
            "owner_id": dev.owner.id if dev.owner else None,
            "owner_fullname": dev.owner.fullname if dev.owner else None,
            "groups_count": len(dev.groups),
            "shares_count": len(dev.shares),
        }
