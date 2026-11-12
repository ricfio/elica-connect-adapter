"""Substructures for extended Device fields.

Contains small dataclasses to represent complex sub-objects that may
appear in the API JSON payload (owner, groups, shares, media, snapTimer, temperature).
"""

from dataclasses import dataclass
from typing import Any


@dataclass
class Owner:
    """Device owner information."""

    id: str | None = None
    fullname: str | None = None

    @staticmethod
    def from_json(data: dict[str, Any] | None) -> "Owner | None":
        if not data:
            return None
        return Owner(
            id=data.get("id"),
            fullname=data.get("fullName"),
        )


@dataclass
class Group:
    """Representation of a group the device belongs to."""

    id: str | None = None
    name: str | None = None

    @staticmethod
    def from_json(data: dict[str, Any] | None) -> "Group | None":
        if not data:
            return None
        return Group(
            id=data.get("id"),
            name=data.get("name"),
        )


@dataclass
class Share:
    """Representation of a share entry for the device."""

    id: str | None = None
    user_id: str | None = None
    permission: str | None = None

    @staticmethod
    def from_json(data: dict[str, Any] | None) -> "Share | None":
        if not data:
            return None
        return Share(
            id=data.get("id"),
            user_id=data.get("userId") or data.get("user_id"),
            permission=data.get("permission"),
        )


@dataclass
class Media:
    """Media reference attached to device (if any)."""

    type: str | None = None
    url: str | None = None

    @staticmethod
    def from_json(data: dict[str, Any] | None) -> "Media | None":
        if not data:
            return None
        return Media(
            type=data.get("type"),
            url=data.get("url"),
        )


@dataclass
class SnapTimer:
    """Snapshot timer configuration for device (if present)."""

    enabled: bool | None = None
    interval: int | None = None

    @staticmethod
    def from_json(data: dict[str, Any] | None) -> "SnapTimer | None":
        if not data:
            return None
        return SnapTimer(
            enabled=data.get("enabled"),
            interval=data.get("interval"),
        )


@dataclass
class Temperature:
    """Temperature reading with unit."""

    value: float | None = None
    unit: str | None = None

    @staticmethod
    def from_json(value: Any, unit: Any) -> "Temperature | None":
        if value is None:
            return None
        try:
            # try to normalize numeric values
            val = float(value)
        except Exception:
            val = None
        return Temperature(value=val, unit=unit)
