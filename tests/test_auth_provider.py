"""Tests for the Home Assistant authentication provider."""

from unittest.mock import MagicMock

from custom_components.elica_connect_adapter.api.adapters.ha.auth_provider import (
    HaAuthProvider,
)
from custom_components.elica_connect_adapter.api.core.auth.auth_service import (
    AuthService,
)


def test_auth_storage_is_isolated_per_entry() -> None:
    """Keep authentication data isolated between config entries."""
    hass = MagicMock()
    hass.data = {}
    auth_service = AuthService("https://example.test", "app", "id", "secret")

    first = HaAuthProvider(
        hass, auth_service, "first", "password", storage_key="elica_auth_first"
    )
    second = HaAuthProvider(
        hass, auth_service, "second", "password", storage_key="elica_auth_second"
    )

    first._store_auth({"access_token": "first-token"})
    second._store_auth({"access_token": "second-token"})

    assert hass.data["elica_auth_first"]["access_token"] == "first-token"
    assert hass.data["elica_auth_second"]["access_token"] == "second-token"
