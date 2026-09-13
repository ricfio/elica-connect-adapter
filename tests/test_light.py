"""Tests for Elica Connect lights."""

from __future__ import annotations

import json
from unittest.mock import AsyncMock, patch

import pytest
from homeassistant.const import Platform

from custom_components.elica_connect_adapter.const import DOMAIN

from .conftest import (DEVICE_ID, DEVICE_NAME, create_mock_device,
                       setup_platform)

pytestmark = pytest.mark.usefixtures("enable_custom_integrations")


async def test_light_mqtt_update(hass):
    """Test light brightness updates instantly when LIGHT_BRIGHTNESS (96) capability changes via MQTT."""
    device = create_mock_device(
        id=DEVICE_ID,
        name=DEVICE_NAME,
        dataModel={"96": 0},
    )

    with patch(
        "custom_components.elica_connect_adapter.coordinator.ElicaConnectCoordinator._async_update_data",
        return_value={"devices": {DEVICE_ID: device}, "mqtt_stats": {}},
    ):
        entry = await setup_platform(hass, DOMAIN, Platform.LIGHT)
        await hass.async_block_till_done()

        state = hass.states.get("light.test_elica_hood_light")
        assert state is not None
        assert state.state == "off"

        # Simulate MQTT update with light brightness 80% (capability 96)
        payload = json.dumps([{"cuid": device.cuid, "dataModel": {"96": 80}}])
        entry_data = hass.data[DOMAIN][entry.entry_id]
        coordinator = entry_data["coordinator"]
        await coordinator._async_update_from_mqtt(f"elica/{device.cuid}/state", payload)
        await hass.async_block_till_done()

        state_on = hass.states.get("light.test_elica_hood_light")
        assert state_on is not None
        assert state_on.state == "on"
        assert state_on.attributes["brightness"] == round((80 / 100) * 255)
        assert device.state.light_brightness == 80

        # Simulate MQTT update turning off light (brightness 0)
        payload_off = json.dumps([{"cuid": device.cuid, "dataModel": {"96": 0}}])
        await coordinator._async_update_from_mqtt(
            f"elica/{device.cuid}/state", payload_off
        )
        await hass.async_block_till_done()

        state_off = hass.states.get("light.test_elica_hood_light")
        assert state_off.state == "off"
        assert device.state.light_brightness == 0
