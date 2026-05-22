"""Button platform for Hanchu — read/write PCS settings."""

from __future__ import annotations

from homeassistant.components.button import ButtonEntity
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from . import HanchuConfigEntry
from .coordinator import HanchuSettingsCoordinator
from .sensor import _device_info


async def async_setup_entry(
    hass: HomeAssistant,
    entry: HanchuConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up Hanchu read/write settings button entities."""
    coordinator = entry.runtime_data.settings_coordinator
    async_add_entities([
        HanchuReadSettingsButton(coordinator, entry),
        HanchuWriteSettingsButton(coordinator, entry),
    ])


class _HanchuSettingsButton(ButtonEntity):
    _attr_has_entity_name = True

    def __init__(self, coordinator: HanchuSettingsCoordinator, entry: HanchuConfigEntry) -> None:
        self._coordinator = coordinator
        self._attr_device_info = _device_info(entry)


class HanchuReadSettingsButton(_HanchuSettingsButton):
    """Button that fetches current PCS settings from the device via iotGet."""

    _attr_name = "Read Settings"
    _attr_icon = "mdi:download"

    def __init__(self, coordinator: HanchuSettingsCoordinator, entry: HanchuConfigEntry) -> None:
        super().__init__(coordinator, entry)
        self._attr_unique_id = f"{entry.entry_id}_read_settings"

    async def async_press(self) -> None:
        await self._coordinator.async_refresh()


class HanchuWriteSettingsButton(_HanchuSettingsButton):
    """Button that sends all staged settings to the device via iotSet."""

    _attr_name = "Write Settings"
    _attr_icon = "mdi:upload"

    def __init__(self, coordinator: HanchuSettingsCoordinator, entry: HanchuConfigEntry) -> None:
        super().__init__(coordinator, entry)
        self._attr_unique_id = f"{entry.entry_id}_write_settings"

    async def async_press(self) -> None:
        await self._coordinator.async_write_pending()
