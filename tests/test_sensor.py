"""Tests for Elica Connect sensors."""
from __future__ import annotations

from unittest.mock import patch

import pytest

from homeassistant.const import Platform
from homeassistant.helpers import entity_registry

from custom_components.elica_connect_adapter.const import DOMAIN

from . import (
    DEVICE_ID,
    DEVICE_NAME,
    create_mock_device,
    setup_platform,
)


async def test_sensor_registration(hass):
    """Test sensor registration."""
    device = create_mock_device(
        id=DEVICE_ID,
        name=DEVICE_NAME,
        dataModel={"64": 1, "96": 50, "110": 3},
        mqtt_stats={"last_message": "2023-01-01T00:00:00", "messages_received": 100}
    )
    
    # Patch coordinator data
    with patch("custom_components.elica_connect_adapter.coordinator.ElicaConnectCoordinator.data", 
             {"devices": {DEVICE_ID: device}}):
        entry = await setup_platform(hass, DOMAIN, Platform.SENSOR)
        await hass.async_block_till_done()

        # Get the entity registry
        entity_reg = entity_registry.async_get(hass)
        
        # Verify capability sensors
        cap_sensors = [
            f"sensor.elica_{DEVICE_ID}_capability_64",
            f"sensor.elica_{DEVICE_ID}_capability_96",
            f"sensor.elica_{DEVICE_ID}_capability_110",
        ]
        for entity_id in cap_sensors:
            entry = entity_reg.async_get(entity_id)
            assert entry is not None
            assert entry.unique_id == entity_id.replace("sensor.", "").replace("_capability", "")
        
        # Verify MQTT sensors
        mqtt_sensors = [
            f"sensor.elica_{DEVICE_ID}_mqtt_last_message",
            f"sensor.elica_{DEVICE_ID}_mqtt_messages_received",
        ]
        for entity_id in mqtt_sensors:
            entry = entity_reg.async_get(entity_id)
            assert entry is not None
            assert entry.unique_id == entity_id.replace("sensor.", "")


async def test_capability_sensor_value(hass):
    """Test sensor values from device capabilities."""
    device = create_mock_device(
        id=DEVICE_ID,
        name=DEVICE_NAME,
        dataModel={"96": 75}  # Light brightness at 75%
    )
    
    with patch("custom_components.elica_connect_adapter.coordinator.ElicaConnectCoordinator.data", 
             {"devices": {DEVICE_ID: device}}):
        entry = await setup_platform(hass, DOMAIN, Platform.SENSOR)
        await hass.async_block_till_done()

        state = hass.states.get(f"sensor.elica_{DEVICE_ID}_capability_96")
        assert state is not None
        assert state.state == "75"
        assert state.name == "Light Brightness"
        assert state.attributes["unit_of_measurement"] == "%"


async def test_mqtt_sensor_values(hass):
    """Test MQTT sensor values."""
    device = create_mock_device(
        id=DEVICE_ID,
        name=DEVICE_NAME,
        mqtt_stats={
            "last_message": "2023-01-01T00:00:00",
            "messages_received": 42
        }
    )
    
    with patch("custom_components.elica_connect_adapter.coordinator.ElicaConnectCoordinator.data", 
             {"devices": {DEVICE_ID: device}}):
        entry = await setup_platform(hass, DOMAIN, Platform.SENSOR)
        await hass.async_block_till_done()

        msg_count = hass.states.get(f"sensor.elica_{DEVICE_ID}_mqtt_messages_received")
        assert msg_count is not None
        assert msg_count.state == "42"
        
        last_msg = hass.states.get(f"sensor.elica_{DEVICE_ID}_mqtt_last_message")
        assert last_msg is not None
        assert last_msg.state == "2023-01-01T00:00:00"


async def test_filter_efficiency_capability_sensor(hass):
    """Test filter efficiency capability sensor (capability 128) inversion and extra attributes."""
    device = create_mock_device(
        id=DEVICE_ID,
        name=DEVICE_NAME,
        dataModel={"128": 30}  # Raw saturation 30% -> Efficiency 70%
    )

    with patch("custom_components.elica_connect_adapter.coordinator.ElicaConnectCoordinator.data",
             {"devices": {DEVICE_ID: device}}):
        entry = await setup_platform(hass, DOMAIN, Platform.SENSOR)
        await hass.async_block_till_done()

        state = hass.states.get(f"sensor.elica_{DEVICE_ID}_capability_128")
        assert state is not None
        assert state.state == "70"  # 100 - 30 = 70 efficiency
        assert state.name == "Grease Filter Efficiency"
        assert state.attributes["unit_of_measurement"] == "%"
        assert state.attributes["saturation"] == 30
        assert state.attributes["efficiency"] == 70
        assert state.attributes["min_value"] == 0
        assert state.attributes["max_value"] == 100
        assert state.attributes["scale"] == "100-0 (decreasing)"
        assert state.attributes["capability_id"] == "128"
