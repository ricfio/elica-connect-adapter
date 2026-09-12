"""Tests for Elica Connect switches."""

from __future__ import annotations

import json
from unittest.mock import patch

import pytest
from homeassistant.const import Platform
from homeassistant.helpers import entity_registry

from custom_components.elica_connect_adapter.const import DOMAIN

from .conftest import DEVICE_ID, DEVICE_NAME, create_mock_device, setup_platform

pytestmark = pytest.mark.usefixtures("enable_custom_integrations")


async def test_airmatic_switch_mqtt_update(hass):
    """Test Airmatic switch updates instantly when FAN_MODE includes bitmask 32 (Airmatic)."""
    device = create_mock_device(
        id=DEVICE_ID,
        name=DEVICE_NAME,
        dataModel={"64": 0, "110": 1},
    )

    with patch(
        "custom_components.elica_connect_adapter.coordinator.ElicaConnectCoordinator._async_update_data",
        return_value={"devices": {DEVICE_ID: device}, "mqtt_stats": {}},
    ):
        entry = await setup_platform(hass, DOMAIN, Platform.SWITCH)
        await hass.async_block_till_done()

        state = hass.states.get("switch.test_elica_hood_automatic_extraction")
        assert state is not None
        assert state.state == "off"

        # Simulate MQTT update with airmatic bitmask 32
        payload = json.dumps([{"cuid": device.cuid, "dataModel": {"64": 32}}])
        entry_data = hass.data[DOMAIN][entry.entry_id]
        coordinator = entry_data["coordinator"]
        await coordinator._async_update_from_mqtt(f"elica/{device.cuid}/state", payload)
        await hass.async_block_till_done()

        state_on = hass.states.get("switch.test_elica_hood_automatic_extraction")
        assert state_on.state == "on"

        # Simulate MQTT update turning off airmatic (bitmask 0)
        payload_off = json.dumps([{"cuid": device.cuid, "dataModel": {"64": 0}}])
        await coordinator._async_update_from_mqtt(f"elica/{device.cuid}/state", payload_off)
        await hass.async_block_till_done()

        state_off = hass.states.get("switch.test_elica_hood_automatic_extraction")
        assert state_off.state == "off"


async def test_airmatic_switch_optimistic_lock_ignores_stale_mqtt(hass):
    """Test that during the optimistic lock grace period, stale MQTT messages reporting old state are ignored."""
    device = create_mock_device(
        id=DEVICE_ID,
        name=DEVICE_NAME,
        dataModel={"64": 32, "110": 1},
    )
    device.state.airmatic = True

    with patch(
        "custom_components.elica_connect_adapter.coordinator.ElicaConnectCoordinator._async_update_data",
        return_value={"devices": {DEVICE_ID: device}, "mqtt_stats": {}},
    ):
        entry = await setup_platform(hass, DOMAIN, Platform.SWITCH)
        await hass.async_block_till_done()

        state = hass.states.get("switch.test_elica_hood_automatic_extraction")
        assert state.state == "on"

        # Optimistically set airmatic to False (turn off)
        device.set_airmatic_optimistic(False)
        assert device.state.airmatic is False

        # Simulate receiving a stale MQTT message with bitmask 32 (Airmatic ON) during the lock window
        payload_stale = json.dumps([{"cuid": device.cuid, "dataModel": {"64": 32}}])
        entry_data = hass.data[DOMAIN][entry.entry_id]
        coordinator = entry_data["coordinator"]
        await coordinator._async_update_from_mqtt(f"elica/{device.cuid}/state", payload_stale)
        await hass.async_block_till_done()

        # State should remain False (stale MQTT ignored)
        assert device.state.airmatic is False


async def test_boost_switch_mqtt_update(hass):
    """Test Boost switch updates instantly when FAN_MODE includes bitmask 4 (Boost)."""
    device = create_mock_device(
        id=DEVICE_ID,
        name=DEVICE_NAME,
        dataModel={"64": 0, "110": 1},
    )

    with patch(
        "custom_components.elica_connect_adapter.coordinator.ElicaConnectCoordinator._async_update_data",
        return_value={"devices": {DEVICE_ID: device}, "mqtt_stats": {}},
    ):
        entry = await setup_platform(hass, DOMAIN, Platform.SWITCH)
        await hass.async_block_till_done()

        state = hass.states.get("switch.test_elica_hood_intensive_extraction")
        assert state is not None
        assert state.state == "off"

        # Simulate MQTT update with boost bitmask 4
        payload = json.dumps([{"cuid": device.cuid, "dataModel": {"64": 4}}])
        entry_data = hass.data[DOMAIN][entry.entry_id]
        coordinator = entry_data["coordinator"]
        await coordinator._async_update_from_mqtt(f"elica/{device.cuid}/state", payload)
        await hass.async_block_till_done()

        state_on = hass.states.get("switch.test_elica_hood_intensive_extraction")
        assert state_on.state == "on"

        # Simulate MQTT update turning off boost (bitmask 0)
        payload_off = json.dumps([{"cuid": device.cuid, "dataModel": {"64": 0}}])
        await coordinator._async_update_from_mqtt(f"elica/{device.cuid}/state", payload_off)
        await hass.async_block_till_done()

        state_off = hass.states.get("switch.test_elica_hood_intensive_extraction")
        assert state_off.state == "off"


async def test_boost_switch_optimistic_lock_ignores_stale_mqtt(hass):
    """Test that during the optimistic lock grace period, stale MQTT messages reporting old state are ignored for boost."""
    device = create_mock_device(
        id=DEVICE_ID,
        name=DEVICE_NAME,
        dataModel={"64": 4, "110": 3},
    )
    device.state.fan_boost = True

    with patch(
        "custom_components.elica_connect_adapter.coordinator.ElicaConnectCoordinator._async_update_data",
        return_value={"devices": {DEVICE_ID: device}, "mqtt_stats": {}},
    ):
        entry = await setup_platform(hass, DOMAIN, Platform.SWITCH)
        await hass.async_block_till_done()

        state = hass.states.get("switch.test_elica_hood_intensive_extraction")
        assert state.state == "on"

        # Optimistically set fan_boost to False (turn off)
        device.set_fan_boost_optimistic(False)
        assert device.state.fan_boost is False

        # Simulate receiving a stale MQTT message with bitmask 4 (Boost ON) during the lock window
        payload_stale = json.dumps([{"cuid": device.cuid, "dataModel": {"64": 4}}])
        entry_data = hass.data[DOMAIN][entry.entry_id]
        coordinator = entry_data["coordinator"]
        await coordinator._async_update_from_mqtt(f"elica/{device.cuid}/state", payload_stale)
        await hass.async_block_till_done()

        # State should remain False (stale MQTT ignored)
        assert device.state.fan_boost is False

