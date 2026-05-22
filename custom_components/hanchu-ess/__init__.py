"""The Hanchu integration."""

from __future__ import annotations

import asyncio
from dataclasses import dataclass

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import Platform
from homeassistant.core import HomeAssistant

from .coordinator import (
    HanchuAuthCoordinator,
    HanchuDataCoordinator,
    HanchuPowerCoordinator,
    HanchuSettingsCoordinator,
)

PLATFORMS: list[Platform] = [Platform.SENSOR, Platform.SELECT, Platform.NUMBER, Platform.TIME, Platform.BUTTON]


@dataclass
class HanchuRuntimeData:
    auth_coordinator: HanchuAuthCoordinator
    data_coordinator: HanchuDataCoordinator
    power_coordinator: HanchuPowerCoordinator
    settings_coordinator: HanchuSettingsCoordinator


type HanchuConfigEntry = ConfigEntry[HanchuRuntimeData]


async def async_setup_entry(hass: HomeAssistant, entry: HanchuConfigEntry) -> bool:
    """Set up Hanchu from a config entry."""
    auth_coordinator = HanchuAuthCoordinator(hass, entry)
    await auth_coordinator.async_config_entry_first_refresh()

    data_coordinator = HanchuDataCoordinator(hass, entry, auth_coordinator)
    power_coordinator = HanchuPowerCoordinator(hass, entry, auth_coordinator)
    settings_coordinator = HanchuSettingsCoordinator(hass, entry, auth_coordinator)
    await asyncio.gather(
        data_coordinator.async_config_entry_first_refresh(),
        power_coordinator.async_config_entry_first_refresh(),
    )

    entry.runtime_data = HanchuRuntimeData(
        auth_coordinator=auth_coordinator,
        data_coordinator=data_coordinator,
        power_coordinator=power_coordinator,
        settings_coordinator=settings_coordinator,
    )

    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)
    return True


async def async_unload_entry(hass: HomeAssistant, entry: HanchuConfigEntry) -> bool:
    """Unload a config entry."""
    return await hass.config_entries.async_unload_platforms(entry, PLATFORMS)
