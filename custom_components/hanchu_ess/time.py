"""Time platform for Hanchu — charge/discharge time period entities."""

from __future__ import annotations

import datetime
from dataclasses import dataclass

from homeassistant.components.time import TimeEntity
from homeassistant.const import EntityCategory
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from . import HanchuConfigEntry
from .coordinator import HanchuSettingsCoordinator
from .sensor import _device_info


def _seconds_to_time(seconds: int) -> datetime.time:
    """Convert seconds-since-midnight to a datetime.time."""
    hours, remainder = divmod(int(seconds), 3600)
    minutes = remainder // 60
    return datetime.time(hours % 24, minutes)


def _time_to_seconds(t: datetime.time) -> int:
    """Convert a datetime.time to seconds-since-midnight."""
    return t.hour * 3600 + t.minute * 60


@dataclass(frozen=True)
class _TimeDef:
    key: str
    name: str
    icon: str


_TIME_DEFS: list[_TimeDef] = [
    _TimeDef("TCT_START_1", "Charge Period 1 Start",    "mdi:clock-start"),
    _TimeDef("TCT_END_1",   "Charge Period 1 End",      "mdi:clock-end"),
    _TimeDef("TDT_START_1", "Discharge Period 1 Start", "mdi:clock-start"),
    _TimeDef("TDT_END_1",   "Discharge Period 1 End",   "mdi:clock-end"),
    _TimeDef("TCT_START_2", "Charge Period 2 Start",    "mdi:clock-start"),
    _TimeDef("TCT_END_2",   "Charge Period 2 End",      "mdi:clock-end"),
    _TimeDef("TDT_START_2", "Discharge Period 2 Start", "mdi:clock-start"),
    _TimeDef("TDT_END_2",   "Discharge Period 2 End",   "mdi:clock-end"),
    _TimeDef("TCT_START_3", "Charge Period 3 Start",    "mdi:clock-start"),
    _TimeDef("TCT_END_3",   "Charge Period 3 End",      "mdi:clock-end"),
    _TimeDef("TDT_START_3", "Discharge Period 3 Start", "mdi:clock-start"),
    _TimeDef("TDT_END_3",   "Discharge Period 3 End",   "mdi:clock-end"),
]


async def async_setup_entry(
    hass: HomeAssistant,
    entry: HanchuConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up Hanchu time period entities."""
    coordinator = entry.runtime_data.settings_coordinator
    async_add_entities(
        HanchuTimePeriod(coordinator, entry, defn) for defn in _TIME_DEFS
    )


class HanchuTimePeriod(CoordinatorEntity[HanchuSettingsCoordinator], TimeEntity):
    """A single charge or discharge time boundary entity."""

    _attr_has_entity_name = True
    _attr_entity_category = EntityCategory.CONFIG

    def __init__(
        self,
        coordinator: HanchuSettingsCoordinator,
        entry: HanchuConfigEntry,
        defn: _TimeDef,
    ) -> None:
        super().__init__(coordinator)
        self._key = defn.key
        self._attr_name = defn.name
        self._attr_icon = defn.icon
        self._attr_unique_id = f"{entry.entry_id}_{defn.key.lower()}"
        self._attr_device_info = _device_info(entry)

    @property
    def native_value(self) -> datetime.time | None:
        """Return the current time value."""
        if not self.coordinator.data:
            return None
        raw = self.coordinator.data.get(self._key)
        if raw is None:
            return None
        return _seconds_to_time(int(raw))

    async def async_set_value(self, value: datetime.time) -> None:
        """Stage the new time value locally (press Write Settings to send to device)."""
        self.coordinator.async_update_local({self._key: _time_to_seconds(value)})
