"""Test the Elica Connect config flow."""

from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from homeassistant import config_entries
from homeassistant.const import CONF_PASSWORD, CONF_USERNAME
from homeassistant.core import HomeAssistant
from homeassistant.data_entry_flow import FlowResultType

from custom_components.elica_connect_adapter.config_flow import (
    CannotConnect,
    InvalidAuth,
)
from custom_components.elica_connect_adapter.const import DOMAIN

pytestmark = pytest.mark.usefixtures("enable_custom_integrations")


async def test_form(hass: HomeAssistant, mock_setup_entry: AsyncMock) -> None:
    """Test we get the form."""
    result = await hass.config_entries.flow.async_init(
        DOMAIN, context={"source": config_entries.SOURCE_USER}
    )
    assert result["type"] is FlowResultType.FORM
    assert result["errors"] == {}

    mock_controller = MagicMock()
    mock_controller.login = AsyncMock(return_value=None)
    mock_controller.is_logged_in = AsyncMock(return_value=True)
    mock_controller.get_account = AsyncMock(return_value={"id": "test_account_id"})
    mock_controller.get_devices = AsyncMock(return_value=[])

    with patch(
        "custom_components.elica_connect_adapter.config_flow.create_controller",
        return_value=mock_controller,
    ):
        result = await hass.config_entries.flow.async_configure(
            result["flow_id"],
            {
                CONF_USERNAME: "test-username",
                CONF_PASSWORD: "test-password",
            },
        )
        await hass.async_block_till_done()

    assert result["type"] is FlowResultType.CREATE_ENTRY
    assert result["title"] == "test-username"
    assert result["data"] == {
        CONF_USERNAME: "test-username",
        CONF_PASSWORD: "test-password",
        "account_id": "test_account_id",
    }
    assert len(mock_setup_entry.mock_calls) == 1


async def test_form_invalid_auth(
    hass: HomeAssistant, mock_setup_entry: AsyncMock
) -> None:
    """Test we handle invalid auth."""
    result = await hass.config_entries.flow.async_init(
        DOMAIN, context={"source": config_entries.SOURCE_USER}
    )

    mock_controller = MagicMock()
    mock_controller.login = AsyncMock(return_value=None)
    mock_controller.is_logged_in = AsyncMock(return_value=False)

    with patch(
        "custom_components.elica_connect_adapter.config_flow.create_controller",
        return_value=mock_controller,
    ):
        result = await hass.config_entries.flow.async_configure(
            result["flow_id"],
            {
                CONF_USERNAME: "test-username",
                CONF_PASSWORD: "test-password",
            },
        )

    assert result["type"] is FlowResultType.FORM
    assert result["errors"] == {"base": "invalid_auth"}

    mock_controller_ok = MagicMock()
    mock_controller_ok.login = AsyncMock(return_value=None)
    mock_controller_ok.is_logged_in = AsyncMock(return_value=True)
    mock_controller_ok.get_account = AsyncMock(return_value={"id": "test_account_id"})
    mock_controller_ok.get_devices = AsyncMock(return_value=[])

    with patch(
        "custom_components.elica_connect_adapter.config_flow.create_controller",
        return_value=mock_controller_ok,
    ):
        result = await hass.config_entries.flow.async_configure(
            result["flow_id"],
            {
                CONF_USERNAME: "test-username",
                CONF_PASSWORD: "test-password",
            },
        )
        await hass.async_block_till_done()

    assert result["type"] is FlowResultType.CREATE_ENTRY
    assert result["title"] == "test-username"
    assert result["data"] == {
        CONF_USERNAME: "test-username",
        CONF_PASSWORD: "test-password",
        "account_id": "test_account_id",
    }
    assert len(mock_setup_entry.mock_calls) == 1


async def test_form_cannot_connect(
    hass: HomeAssistant, mock_setup_entry: AsyncMock
) -> None:
    """Test we handle cannot connect error."""
    result = await hass.config_entries.flow.async_init(
        DOMAIN, context={"source": config_entries.SOURCE_USER}
    )

    mock_controller = MagicMock()
    mock_controller.login = AsyncMock(side_effect=Exception("Connection error"))

    with patch(
        "custom_components.elica_connect_adapter.config_flow.create_controller",
        return_value=mock_controller,
    ):
        result = await hass.config_entries.flow.async_configure(
            result["flow_id"],
            {
                CONF_USERNAME: "test-username",
                CONF_PASSWORD: "test-password",
            },
        )

    assert result["type"] is FlowResultType.FORM
    assert result["errors"] == {"base": "cannot_connect"}

    mock_controller_ok = MagicMock()
    mock_controller_ok.login = AsyncMock(return_value=None)
    mock_controller_ok.is_logged_in = AsyncMock(return_value=True)
    mock_controller_ok.get_account = AsyncMock(return_value={"id": "test_account_id"})
    mock_controller_ok.get_devices = AsyncMock(return_value=[])

    with patch(
        "custom_components.elica_connect_adapter.config_flow.create_controller",
        return_value=mock_controller_ok,
    ):
        result = await hass.config_entries.flow.async_configure(
            result["flow_id"],
            {
                CONF_USERNAME: "test-username",
                CONF_PASSWORD: "test-password",
            },
        )
        await hass.async_block_till_done()

    assert result["type"] is FlowResultType.CREATE_ENTRY
    assert result["title"] == "test-username"
    assert result["data"] == {
        CONF_USERNAME: "test-username",
        CONF_PASSWORD: "test-password",
        "account_id": "test_account_id",
    }
    assert len(mock_setup_entry.mock_calls) == 1
