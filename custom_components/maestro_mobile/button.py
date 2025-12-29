import json
import logging
from homeassistant.components.button import ButtonEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.device_registry import DeviceEntryType
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from . import DOMAIN

_LOGGER = logging.getLogger(__name__)

async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up button for this flow."""
    async_add_entities([MaestroMobileRunButton(hass, entry)])


class MaestroMobileRunButton(ButtonEntity):
    """Button entity to run a Maestro flow."""

    _attr_has_entity_name = True

    def __init__(self, hass: HomeAssistant, entry: ConfigEntry):
        """Initialize the button."""
        self._hass = hass
        self._entry = entry
        self._attr_name = f"Run {self._entry.data['flow_name']}"
        self._attr_device_name = self._entry.data.get("device", None)
        if self._attr_device_name == None:
            self._attr_device_name = "Default"
        self._attr_unique_id = f"maestro_mobile_run_{entry.entry_id}"
        self._attr_icon = "mdi:play-circle"
        self._attr_device_info = {
            "identifiers": {(DOMAIN, self._attr_device_name)},
            "name": f"Maestro Mobile {self._attr_device_name} Device",
            "manufacturer": "coder89",
            "model": "Flow Runner",
            "serial_number": self._attr_device_name,
            "entry_type": DeviceEntryType.SERVICE,
        }

    async def async_press(self) -> None:
        """Handle the button press."""
        flow_file = self._entry.data["flow_file"]
        device = self._entry.data.get("device")

        payload = {
          "id": self._entry.entry_id,
          "flow_file": flow_file,
        }
        if device:
            payload["device"] = device

        await self._hass.services.async_call(
            "mqtt",
            "publish",
            {"topic": "maestro_mobile/run_flow", "payload": json.dumps(payload), "qos": 0}
        )

    @property
    def disabled(self) -> bool:
        """Disable button while test is running."""
        return self._entry.runtime_data["sensor"].state == "running"

    @property
    def icon(self) -> str:
        """Dynamic icon based on status."""
        status = self._entry.runtime_data["sensor"].state
        if status == "running":
            return "mdi:progress-clock"
        return "mdi:play-circle"