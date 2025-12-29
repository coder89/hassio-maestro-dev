from homeassistant.components.sensor import SensorEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.device_registry import DeviceEntryType
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from . import DOMAIN

async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up sensor for flow status."""
    async_add_entities([MaestroStatusSensor(hass, entry)])

class MaestroStatusSensor(SensorEntity):
    """Sensor showing last run status of a Maestro flow."""

    def __init__(self, hass: HomeAssistant, entry: ConfigEntry):
        self._hass = hass
        self._entry = entry
        self._attr_name = f"{self._entry.data['flow_name']} Status"
        self._attr_device_name = self._entry.data.get("device", "default")
        self._attr_unique_id = f"maestro_mobile_run_{entry.entry_id}_status"
        self._attr_icon = "mdi:clock-outline"
        self._attr_device_info = {
            "identifiers": {(DOMAIN, self._attr_device_name)},
            "name": f"Maestro Mobile Flows {self._attr_device_name}",
            "manufacturer": "coder89",
            "model": "Flow Runner",
            "serial_number": self._attr_device_name,
            "entry_type": DeviceEntryType.SERVICE,
        }
        self._attr_native_value = "idle"

    @property
    def state(self) -> str:
        return self._attr_native_value