import json
from homeassistant.components.button import ButtonEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from . import DOMAIN

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
        self._attr_name = f"Run {entry.data['flow_name']}"
        self._attr_unique_id = f"maestro_mobile_run_{entry.entry_id}"
        self._attr_icon = "mdi:play-circle"

    async def async_press(self) -> None:
        """Handle the button press."""
        flow_file = self._entry.data["flow_file"]
        device = self._entry.data.get("device")

        payload = {"flow_file": flow_file}
        if device:
            payload["device"] = device

        payload_json = json.dumps(payload)
        await self._hass.services.async_call(
            "mqtt",
            "publish",
            {"topic": "maestro_mobile/run_flow", "payload": payload_json, "qos": 0}
        )