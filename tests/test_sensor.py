"""Tests for Elica Connect sensors."""
from __future__ import annotations

from unittest.mock import patch

import pytest

from homeassistant.const import Platform
from homeassistant.helpers import entity_registry

from custom_components.elica_connect_adapter.const import DOMAIN

from .conftest import (
    DEVICE_ID,
    DEVICE_NAME,
    create_mock_device,
    setup_platform,
)

pytestmark = pytest.mark.usefixtures("enable_custom_integrations")


async def test_sensor_registration(hass):
    """Test sensor registration."""
    device = create_mock_device(
        id=DEVICE_ID,
        name=DEVICE_NAME,
        dataModel={"128": 30},
        mqtt_stats={"last_message": "2023-01-01T00:00:00", "messages_received": 100}
    )

    # Patch coordinator data
    with patch(
        "custom_components.elica_connect_adapter.coordinator.ElicaConnectCoordinator._async_update_data",
        return_value={"devices": {DEVICE_ID: device}, "mqtt_stats": getattr(device, "mqtt_stats", {})}
    ):
        entry = await setup_platform(hass, DOMAIN, Platform.SENSOR)
        await hass.async_block_till_done()

        # Get the entity registry
        entity_reg = entity_registry.async_get(hass)

        # Verify filter efficiency capability sensor
        filter_entity = entity_reg.async_get("sensor.test_elica_hood_grease_filter_efficiency")
        assert filter_entity is not None

        # Verify MQTT sensors
        mqtt_sensors = [
            "sensor.test_elica_hood_mqtt_state",
            "sensor.test_elica_hood_mqtt_messages",
        ]
        for entity_id in mqtt_sensors:
            entry = entity_reg.async_get(entity_id)
            assert entry is not None


async def test_capability_sensor_value(hass):
    """Test sensor values from device capabilities."""
    device = create_mock_device(
        id=DEVICE_ID,
        name=DEVICE_NAME,
        dataModel={"128": 20}  # Raw saturation 20% -> Efficiency 80%
    )

    with patch(
        "custom_components.elica_connect_adapter.coordinator.ElicaConnectCoordinator._async_update_data",
        return_value={"devices": {DEVICE_ID: device}, "mqtt_stats": {}}
    ):
        entry = await setup_platform(hass, DOMAIN, Platform.SENSOR)
        await hass.async_block_till_done()

        state = hass.states.get("sensor.test_elica_hood_grease_filter_efficiency")
        assert state is not None
        assert state.state == "80"
        assert state.name == "Test Elica Hood Grease Filter Efficiency"


async def test_mqtt_sensor_values(hass):
    """Test MQTT sensor values."""
    device = create_mock_device(
        id=DEVICE_ID,
        name=DEVICE_NAME,
        mqtt_stats={
            "last_message_timestamp": "2023-01-01T00:00:00",
            "total_messages": 42
        }
    )

    with patch(
        "custom_components.elica_connect_adapter.coordinator.ElicaConnectCoordinator._async_update_data",
        return_value={"devices": {DEVICE_ID: device}, "mqtt_stats": getattr(device, "mqtt_stats", {})}
    ):
        entry = await setup_platform(hass, DOMAIN, Platform.SENSOR)
        await hass.async_block_till_done()

        msg_count = hass.states.get("sensor.test_elica_hood_mqtt_messages")
        assert msg_count is not None
        assert msg_count.state == "42"

        mqtt_state = hass.states.get("sensor.test_elica_hood_mqtt_state")
        assert mqtt_state is not None


async def test_filter_efficiency_capability_sensor(hass):
    """Test filter efficiency capability sensor (capability 128) inversion and extra attributes."""
    device = create_mock_device(
        id=DEVICE_ID,
        name=DEVICE_NAME,
        dataModel={"128": 30}  # Raw saturation 30% -> Efficiency 70%
    )

    with patch(
        "custom_components.elica_connect_adapter.coordinator.ElicaConnectCoordinator._async_update_data",
        return_value={"devices": {DEVICE_ID: device}, "mqtt_stats": {}}
    ):
        await setup_platform(hass, DOMAIN, Platform.SENSOR)
        await hass.async_block_till_done()

        state = hass.states.get("sensor.test_elica_hood_grease_filter_efficiency")
        assert state is not None
        assert state.state == "70"  # 100 - 30 = 70 efficiency
        assert state.name == "Test Elica Hood Grease Filter Efficiency"
        assert state.attributes["unit_of_measurement"] == "%"
        assert state.attributes["saturation"] == 30
        assert state.attributes["efficiency"] == 70
        assert state.attributes["min_value"] == 0
        assert state.attributes["max_value"] == 100
        assert state.attributes["scale"] == "100-0 (decreasing)"
        assert state.attributes["capability_id"] == "128"
