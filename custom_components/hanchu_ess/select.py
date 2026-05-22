"""Select platform for Hanchu — work mode selection."""

from __future__ import annotations

from homeassistant.components.select import SelectEntity
from homeassistant.const import EntityCategory
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from . import HanchuConfigEntry
from .const import (
    IOT_WORK_MODE,
    WORK_MODE_SELF_CONSUMPTION,
    WORK_MODE_USER_DEFINED,
)
from .coordinator import HanchuSettingsCoordinator
from .sensor import _device_info

WORK_MODE_OPTIONS: dict[str, int] = {
    "User-defined": WORK_MODE_USER_DEFINED,
    "Self-consumption mode": WORK_MODE_SELF_CONSUMPTION,
}
_OPTION_BY_VALUE: dict[int, str] = {v: k for k, v in WORK_MODE_OPTIONS.items()}


async def async_setup_entry(
    hass: HomeAssistant,
    entry: HanchuConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up Hanchu work mode select entity."""
    async_add_entities([HanchuWorkModeSelect(entry.runtime_data.settings_coordinator, entry)])


class HanchuWorkModeSelect(CoordinatorEntity[HanchuSettingsCoordinator], SelectEntity):
    """Select entity representing the Hanchu PCS work mode."""

    _attr_has_entity_name = True
    _attr_name = "Work Mode"
    _attr_icon = "mdi:cog-transfer"
    _attr_options = list(WORK_MODE_OPTIONS.keys())
    _attr_entity_category = EntityCategory.CONFIG

    def __init__(self, coordinator: HanchuSettingsCoordinator, entry: HanchuConfigEntry) -> None:
        super().__init__(coordinator)
        self._attr_unique_id = f"{entry.entry_id}_work_mode"
        self._attr_device_info = _device_info(entry)

    @property
    def current_option(self) -> str | None:
        """Return the currently selected work mode label."""
        if not self.coordinator.data:
            return None
        raw = self.coordinator.data.get(IOT_WORK_MODE)
        if raw is None:
            return None
        return _OPTION_BY_VALUE.get(int(raw))

    async def async_select_option(self, option: str) -> None:
        """Stage the new work mode locally (press Write Settings to send to device)."""
        value = WORK_MODE_OPTIONS[option]
        self.coordinator.async_update_local({IOT_WORK_MODE: value})
