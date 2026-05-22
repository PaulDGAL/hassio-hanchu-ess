"""Number platform for Hanchu — numeric PCS setting entities."""

from __future__ import annotations

from dataclasses import dataclass

from homeassistant.components.number import NumberDeviceClass, NumberEntity, NumberMode
from homeassistant.const import PERCENTAGE, EntityCategory, UnitOfPower
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from . import HanchuConfigEntry
from .const import (
    IOT_CHG_PWR,
    IOT_DSCHG_PWR,
    IOT_GRID_CHG_SOC,
    IOT_MAX_CHG_SOC,
    IOT_MIN_DSCHG_SOC,
    IOT_MIN_OFF_GRID_SOC,
)
from .coordinator import HanchuSettingsCoordinator
from .sensor import _device_info


@dataclass(frozen=True)
class _NumberDef:
    key: str
    name: str
    icon: str
    unit: str
    device_class: NumberDeviceClass | None
    native_min: float
    native_max: float
    native_step: float


_NUMBER_DEFS: list[_NumberDef] = [
    _NumberDef(IOT_CHG_PWR,         "Charging Power Maximum",            "mdi:battery-charging",          UnitOfPower.WATT, NumberDeviceClass.POWER, 0, 5000, 1),
    _NumberDef(IOT_DSCHG_PWR,       "Discharge Power Maximum",           "mdi:battery-minus",             UnitOfPower.WATT, NumberDeviceClass.POWER, 0, 5000, 1),
    _NumberDef(IOT_GRID_CHG_SOC,    "Grid to Battery Charge Maximum",    "mdi:transmission-tower-import", PERCENTAGE,       None,                    0,   100, 1),
    _NumberDef(IOT_MAX_CHG_SOC,     "Maximum Charge SOC",                "mdi:battery-high",              PERCENTAGE,       None,                    0,   100, 1),
    _NumberDef(IOT_MIN_DSCHG_SOC,   "On-Grid Battery Discharge Minimum", "mdi:battery-low",               PERCENTAGE,       None,                    0,   100, 1),
    _NumberDef(IOT_MIN_OFF_GRID_SOC,"Off-Grid Battery Discharge Minimum","mdi:transmission-tower",        PERCENTAGE,       None,                    0,   100, 1),
]


async def async_setup_entry(
    hass: HomeAssistant,
    entry: HanchuConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up Hanchu numeric setting entities."""
    coordinator = entry.runtime_data.settings_coordinator
    async_add_entities(
        HanchuSettingNumber(coordinator, entry, defn) for defn in _NUMBER_DEFS
    )


class HanchuSettingNumber(CoordinatorEntity[HanchuSettingsCoordinator], NumberEntity):
    """A single writable numeric PCS setting."""

    _attr_has_entity_name = True
    _attr_mode = NumberMode.BOX
    _attr_entity_category = EntityCategory.CONFIG

    def __init__(
        self,
        coordinator: HanchuSettingsCoordinator,
        entry: HanchuConfigEntry,
        defn: _NumberDef,
    ) -> None:
        super().__init__(coordinator)
        self._key = defn.key
        self._attr_name = defn.name
        self._attr_icon = defn.icon
        self._attr_native_unit_of_measurement = defn.unit
        self._attr_device_class = defn.device_class
        self._attr_native_min_value = defn.native_min
        self._attr_native_max_value = defn.native_max
        self._attr_native_step = defn.native_step
        self._attr_unique_id = f"{entry.entry_id}_{defn.key.lower()}"
        self._attr_device_info = _device_info(entry)

    @property
    def native_value(self) -> float | None:
        """Return the current setting value."""
        if not self.coordinator.data:
            return None
        raw = self.coordinator.data.get(self._key)
        if raw is None:
            return None
        return float(raw)

    async def async_set_native_value(self, value: float) -> None:
        """Stage the new value locally (press Write Settings to send to device)."""
        self.coordinator.async_update_local({self._key: int(value)})
