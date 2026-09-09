"""Common fixtures for the Elica Connect tests."""
from __future__ import annotations

from collections.abc import Generator
from dataclasses import dataclass
from typing import Any
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.setup import async_setup_component

from custom_components.elica_connect_adapter.const import DOMAIN


DEVICE_ID = "test_device"
DEVICE_NAME = "Test Elica Hood"
USERNAME = "test@example.com"
PASSWORD = "testpassword"


@dataclass
class Device:
    """Mock device for testing."""
    id: str
    name: str
    manufacturer: str = "Elica"
    model: str = "Test Model"
    sw_version: str = "1.0.0"
    dataModel: dict[str, Any] | None = None
    mqtt_stats: dict[str, Any] | None = None


def create_mock_device(**kwargs) -> Device:
    """Create a mock device with default values."""
    return Device(**kwargs)


@pytest.fixture
async def hass(hass) -> HomeAssistant:
    """Set up HomeAssistant for testing."""
    assert await async_setup_component(hass, DOMAIN, {})
    return hass


@pytest.fixture
def mock_config_entry() -> ConfigEntry:
    """Create a mock config entry."""
    return ConfigEntry(
        version=1,
        minor_version=1,
        domain=DOMAIN,
        title=USERNAME,
        data={
            "username": USERNAME,
            "password": PASSWORD,
        },
        options={},
        source="user",
        unique_id=USERNAME,
    )


async def setup_platform(hass: HomeAssistant, domain: str, platform: str) -> ConfigEntry:
    """Set up the Elica platform for testing."""
    config_entry = await hass.config_entries.async_add_entry(
        title="Test",
        data={"username": USERNAME, "password": PASSWORD},
        domain=domain,
    )
    
    mock_controller = MagicMock()
    mock_controller.login = AsyncMock(return_value=True)
    mock_controller.is_logged_in = AsyncMock(return_value=True)
    
    with patch("custom_components.elica_connect_adapter.utils.create_controller",
              return_value=mock_controller):
        assert await hass.config_entries.async_setup(config_entry.entry_id)
        await hass.async_block_till_done()
        
    return config_entry
