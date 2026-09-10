"""Config flow for the Elica Connect integration."""

from __future__ import annotations

import logging
from typing import Any

import voluptuous as vol
from homeassistant.config_entries import ConfigEntry, ConfigFlow, OptionsFlow

try:
    from homeassistant.config_entries import ConfigFlowResult
except ImportError:
    from homeassistant.data_entry_flow import FlowResult as ConfigFlowResult

from homeassistant.const import CONF_PASSWORD, CONF_USERNAME
from homeassistant.core import HomeAssistant, callback
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
    try:
        await controller.login()
    except Exception as exc:
        _LOGGER.debug("Error while logging in: %s", exc)
        raise CannotConnect from exc

    # Raise an error if authentication fails
    if not await controller.is_logged_in():
        raise InvalidAuth

    account = await controller.get_account()

    # Retrieve all devices for the account
    devices_entries = await controller.get_devices()
    devices = [
        {
            "uid": device.uid,
            "name": device.name,
            "manufacturer": "Elica",
            "model": getattr(device, "model", None),
            "serial": getattr(device, "serial", None),
        }
        for device in devices_entries
    ]

    return {
        "title": data[CONF_USERNAME],
        "unique_id": account["id"],
        "account_id": account["id"],
        "devices": devices,
        "is_local": False,
        "capabilities": {"fan_speed": True, "light": False},
    }


class ElicaConnectConfigFlow(ConfigFlow, domain=DOMAIN):
    """Handle the Configuration flow."""

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
                validated = await validate_input(self.hass, user_input)
            except CannotConnect:
                errors["base"] = "cannot_connect"
            except InvalidAuth:
                errors["base"] = "invalid_auth"
            except Exception:
                _LOGGER.exception("Unexpected exception")
                errors["base"] = "unknown"
            else:
                # # Create the config entry with the retrieved title
                # # The client itself will be created in async_setup_entry
                # return self.async_create_entry(
                #     title=validated["title"],
                #     data=user_input,
                # )
                # Use unique id to prevent duplicates
                if validated.get("unique_id"):
                    await self.async_set_unique_id(validated["unique_id"])
                    self._abort_if_unique_id_configured()

                return self.async_create_entry(
                    title=validated.get("title", user_input[CONF_USERNAME]),
                    data={**user_input, "account_id": validated.get("account_id")},
                )

        # Show the form to the user for username/password input
        return self.async_show_form(
            step_id="user", data_schema=STEP_USER_DATA_SCHEMA, errors=errors
        )

    @staticmethod
    @callback
    def async_get_options_flow(config_entry: ConfigEntry) -> ElicaConnectOptionsFlow:
        """Get the options flow for this handler."""
        return ElicaConnectOptionsFlow(config_entry)


class ElicaConnectOptionsFlow(OptionsFlow):
    """Handle options."""

    def __init__(self, config_entry: ConfigEntry) -> None:
        """Initialize."""
        self._config_entry = config_entry

    async def async_step_init(
        self, user_input: dict[str, Any] | None = None
    ) -> ConfigFlowResult:
        """Manage the options."""
        if user_input is not None:
            return self.async_create_entry(title="", data=user_input)

        options = {
            vol.Optional(
                "scan_interval",
                default=self._config_entry.options.get("scan_interval", 60),
            ): vol.All(vol.Coerce(int), vol.Range(min=30, max=300)),
            vol.Optional(
                "mqtt_updates",
                default=self._config_entry.options.get("mqtt_updates", True),
            ): bool,
            vol.Optional(
                "mqtt_debug",
                default=self._config_entry.options.get("mqtt_debug", False),
            ): bool,
            vol.Optional(
                "debug",
                default=self._config_entry.options.get("debug", False),
            ): bool,
        }

        return self.async_show_form(
            step_id="init",
            data_schema=vol.Schema(options),
        )


class CannotConnect(HomeAssistantError):
    """Error to indicate we cannot connect to the API."""


class InvalidAuth(HomeAssistantError):
    """Error to indicate invalid authentication credentials."""
