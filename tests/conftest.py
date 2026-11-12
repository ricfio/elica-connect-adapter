"""Common fixtures for the Elica Connect tests."""

from __future__ import annotations

from collections.abc import Generator
from typing import Any
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from homeassistant.core import HomeAssistant
from pytest_homeassistant_custom_component.common import MockConfigEntry

from custom_components.elica_connect_adapter.api.domain import (
    MANUFACTURER,
    Device,
    DeviceState,
)

DEVICE_ID = "test_device"
DEVICE_NAME = "Test Elica Hood"
USERNAME = "test@example.com"
PASSWORD = "testpassword"


def create_mock_device(
    id: str = DEVICE_ID,
    name: str = DEVICE_NAME,
    dataModel: dict[str, Any] | None = None,
    mqtt_stats: dict[str, Any] | None = None,
    **kwargs,
) -> Device:
    """Create a mock device for testing."""
    dm = dataModel or kwargs.get("data_model", {})
    state = DeviceState.from_json({"dataModel": dm})
    device = Device(
        uid=id,
        cuid=f"cuid_{id}",
        name=name,
        manufacturer=kwargs.get("manufacturer", MANUFACTURER),
        model=kwargs.get("model", "Test Model"),
        sw_version=kwargs.get("sw_version", "1.0.0"),
        data_model=dm,
        capabilities=list(dm.keys()),
        state=state,
    )
    if mqtt_stats:
        device.mqtt_stats = mqtt_stats
    return device


@pytest.fixture
def mock_setup_entry() -> Generator[AsyncMock, None, None]:
    """Mock setup entry."""
    with patch(
        "custom_components.elica_connect_adapter.async_setup_entry",
        return_value=True,
    ) as mock_setup:
        yield mock_setup


@pytest.fixture
def auto_mock_mqtt(mqtt_mock):
    """Auto mock MQTT integration."""
    return mqtt_mock


async def setup_platform(
    hass: HomeAssistant, domain: str, platform: str
) -> MockConfigEntry:
    """Set up the Elica platform for testing."""
    config_entry = MockConfigEntry(
        domain=domain,
        data={"username": USERNAME, "password": PASSWORD},
        title="Test",
    )
    config_entry.add_to_hass(hass)

    mock_controller = MagicMock()
    mock_controller.login = AsyncMock(return_value=True)
    mock_controller.is_logged_in = AsyncMock(return_value=True)
    mock_controller.get_devices = AsyncMock(return_value=[])
    mock_controller.stop_listening = AsyncMock(return_value=None)

    with patch(
        "custom_components.elica_connect_adapter.create_controller",
        return_value=mock_controller,
    ):
        assert await hass.config_entries.async_setup(config_entry.entry_id)
        await hass.async_block_till_done()

    return config_entry
