import logging
from homeassistant.components.sensor import SensorEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.device_registry import DeviceEntryType
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.restore_state import RestoreEntity

from . import DOMAIN

_LOGGER = logging.getLogger(__name__)

async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up sensor for flow status."""
    async_add_entities([MaestroStatusSensor(hass, entry)])

class MaestroStatusSensor(RestoreEntity, SensorEntity):
    """Sensor showing last run status of a Maestro flow."""

    def __init__(self, hass: HomeAssistant, entry: ConfigEntry):
        self._hass = hass
        self._entry = entry
        self._attr_name = f"{self._entry.data['flow_name']} Status"
        self._attr_device_name = self._entry.data.get("device", None)
        if self._attr_device_name == None:
            self._attr_device_name = "Default"
        self._attr_unique_id = f"maestro_mobile_run_{entry.entry_id}_status"
        self._attr_icon = "mdi:clock-outline"
        self._attr_device_info = {
            "identifiers": {(DOMAIN, self._attr_device_name)},
            "name": f"Maestro Mobile {self._attr_device_name} Device",
            "manufacturer": "coder89",
            "model": "Flow Runner",
            "serial_number": self._attr_device_name,
            "entry_type": DeviceEntryType.SERVICE,
        }
        self._attr_native_value = "idle"
        self._entry.runtime_data["sensor"] = self

    async def async_added_to_hass(self) -> None:
        """Handle entity addition to hass."""
        await super().async_added_to_hass()

        # Restore previous state if it exists
        last_state = await self.async_get_last_state()
        if last_state:
            self._attr_native_value = last_state.state
            _LOGGER.debug(f"Restored state for {self.entity_id}: {self._attr_native_value}")

    @property
    def state(self) -> str:
        return self._attr_native_value

    def update_state(self, new_status: str) -> None:
        self._attr_native_value = new_status
        self.async_write_ha_state()
