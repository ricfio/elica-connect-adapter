"""Tests for Elica Connect fans."""

from __future__ import annotations

from unittest.mock import AsyncMock, patch

import pytest
from homeassistant.const import Platform

from custom_components.elica_connect_adapter.const import DOMAIN

from .conftest import DEVICE_ID, DEVICE_NAME, create_mock_device, setup_platform

pytestmark = pytest.mark.usefixtures("enable_custom_integrations")


async def test_fan_turn_on_default_percentage(hass):
    """Test turning on fan without percentage defaults to speed 1 (33%)."""
    device = create_mock_device(
        id=DEVICE_ID,
        name=DEVICE_NAME,
        dataModel={"110": 0, "64": 0},
    )

    with patch(
        "custom_components.elica_connect_adapter.coordinator.ElicaConnectCoordinator._async_update_data",
        return_value={"devices": {DEVICE_ID: device}, "mqtt_stats": {}},
    ):
        entry = await setup_platform(hass, DOMAIN, Platform.FAN)
        await hass.async_block_till_done()

        entry_data = hass.data[DOMAIN][entry.entry_id]
        mock_controller = entry_data["controller"]
        mock_controller.set_fan_mode = AsyncMock(return_value=True)

        state = hass.states.get("fan.test_elica_hood_extraction")
        assert state is not None
        assert state.state == "off"

        from homeassistant.components.fan import DOMAIN as FAN_DOMAIN
        from homeassistant.components.fan import SERVICE_TURN_ON

        await hass.services.async_call(
            FAN_DOMAIN,
            SERVICE_TURN_ON,
            {"entity_id": "fan.test_elica_hood_extraction"},
            blocking=True,
        )

        mock_controller.set_fan_mode.assert_awaited_once_with(
            DEVICE_ID,
            False,
            1,
            False,
        )

        await hass.config_entries.async_unload(entry.entry_id)
        await hass.async_block_till_done()


async def test_fan_turn_on_with_percentage(hass):
    """Test turning on fan with specific percentage."""
    device = create_mock_device(
        id=DEVICE_ID,
        name=DEVICE_NAME,
        dataModel={"110": 0, "64": 0},
    )

    with patch(
        "custom_components.elica_connect_adapter.coordinator.ElicaConnectCoordinator._async_update_data",
        return_value={"devices": {DEVICE_ID: device}, "mqtt_stats": {}},
    ):
        entry = await setup_platform(hass, DOMAIN, Platform.FAN)
        await hass.async_block_till_done()

        entry_data = hass.data[DOMAIN][entry.entry_id]
        mock_controller = entry_data["controller"]
        mock_controller.set_fan_mode = AsyncMock(return_value=True)

        from homeassistant.components.fan import DOMAIN as FAN_DOMAIN
        from homeassistant.components.fan import SERVICE_TURN_ON

        await hass.services.async_call(
            FAN_DOMAIN,
            SERVICE_TURN_ON,
            {"entity_id": "fan.test_elica_hood_extraction", "percentage": 67},
            blocking=True,
        )

        mock_controller.set_fan_mode.assert_awaited_once_with(
            DEVICE_ID,
            False,
            2,
            False,
        )

        await hass.config_entries.async_unload(entry.entry_id)
        await hass.async_block_till_done()


async def test_fan_turn_off(hass):
    """Test turning off fan."""
    device = create_mock_device(
        id=DEVICE_ID,
        name=DEVICE_NAME,
        dataModel={"110": 2, "64": 1},
    )

    with patch(
        "custom_components.elica_connect_adapter.coordinator.ElicaConnectCoordinator._async_update_data",
        return_value={"devices": {DEVICE_ID: device}, "mqtt_stats": {}},
    ):
        entry = await setup_platform(hass, DOMAIN, Platform.FAN)
        await hass.async_block_till_done()

        entry_data = hass.data[DOMAIN][entry.entry_id]
        mock_controller = entry_data["controller"]
        mock_controller.set_fan_mode = AsyncMock(return_value=True)

        from homeassistant.components.fan import DOMAIN as FAN_DOMAIN
        from homeassistant.components.fan import SERVICE_TURN_OFF

        await hass.services.async_call(
            FAN_DOMAIN,
            SERVICE_TURN_OFF,
            {"entity_id": "fan.test_elica_hood_extraction"},
            blocking=True,
        )

        mock_controller.set_fan_mode.assert_awaited_once_with(
            DEVICE_ID,
            False,
            0,
            False,
        )

        await hass.config_entries.async_unload(entry.entry_id)
        await hass.async_block_till_done()
