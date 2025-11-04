"""Config flow for the Elica Connect integration."""

from __future__ import annotations

import logging
from typing import Any

import voluptuous as vol

from homeassistant.config_entries import ConfigFlow, ConfigFlowResult
from homeassistant.const import CONF_PASSWORD, CONF_USERNAME
from homeassistant.core import HomeAssistant
from homeassistant.exceptions import HomeAssistantError

from .const import DOMAIN
from .utils import create_controller

_LOGGER = logging.getLogger(__name__)

STEP_USER_DATA_SCHEMA = vol.Schema(
    {
        vol.Required(CONF_USERNAME): str,
        vol.Required(CONF_PASSWORD): str,
    }
)


async def validate_input(hass: HomeAssistant, data: dict[str, Any]) -> dict[str, Any]:
    """Validate the user input allows us to connect to Elica.

    This function creates a client instance, performs login,
    and retrieves devices to generate a title for the config entry.
    """

    controller = create_controller(
        hass,
        data[CONF_USERNAME],
        data[CONF_PASSWORD],
    )

    # Perform login using username/password from user input
    await controller.login()

    # Raise an error if authentication fails
    if not await controller.is_logged_in():
        raise InvalidAuth

    # Retrieve devices to use the first device's name as the entry title
    devices = await controller.get_devices()
    title = devices[0].name if devices else "Elica Device"

    return {"title": title}


class Hub(ConfigFlow, domain=DOMAIN):
    """Handle the configuration flow for Elica Connect."""

    VERSION = 1

    async def async_step_user(
        self, user_input: dict[str, Any] | None = None
    ) -> ConfigFlowResult:
        """Handle the initial step initiated by the user."""
        errors: dict[str, str] = {}

        if user_input is not None:
            # Check if an entry with the same username already exists
            for entry in self._async_current_entries():
                if entry.data.get(CONF_USERNAME) == user_input[CONF_USERNAME]:
                    return self.async_abort(reason="already_configured")

            try:
                # Validate user input by attempting login and fetching devices
                info = await validate_input(self.hass, user_input)
            except CannotConnect:
                errors["base"] = "cannot_connect"
            except InvalidAuth:
                errors["base"] = "invalid_auth"
            except Exception:
                _LOGGER.exception("Unexpected exception")
                errors["base"] = "unknown"
            else:
                # Create the config entry with the retrieved title
                # The client itself will be created in async_setup_entry
                return self.async_create_entry(title=info["title"], data=user_input)

        # Show the form to the user for username/password input
        return self.async_show_form(
            step_id="user", data_schema=STEP_USER_DATA_SCHEMA, errors=errors
        )


class CannotConnect(HomeAssistantError):
    """Error to indicate we cannot connect to the API."""


class InvalidAuth(HomeAssistantError):
    """Error to indicate invalid authentication credentials."""
