"""Tests for the MQTT listener lifecycle."""

from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from homeassistant.core import HomeAssistant
from pytest_homeassistant_custom_component.common import MockConfigEntry

from custom_components.elica_connect_adapter import async_unload_entry
from custom_components.elica_connect_adapter.const import DOMAIN

pytestmark = pytest.mark.usefixtures("enable_custom_integrations")


async def test_unload_stops_mqtt_listener(hass: HomeAssistant) -> None:
    """Unloading an entry stops its MQTT client before removing the entry data."""
    entry = MockConfigEntry(domain=DOMAIN)
    controller = MagicMock()
    controller.stop_listening = AsyncMock()
    hass.data[DOMAIN] = {entry.entry_id: {"controller": controller}}

    with patch.object(
        hass.config_entries, "async_unload_platforms", AsyncMock(return_value=True)
    ):
        assert await async_unload_entry(hass, entry)
    controller.stop_listening.assert_awaited_once()
    assert entry.entry_id not in hass.data[DOMAIN]
