"""Maestro Mobile integration."""
import os
import json
import logging
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant, callback
from homeassistant.helpers import entity_platform, service
from homeassistant.components import mqtt

DOMAIN = "maestro_mobile"
_LOGGER = logging.getLogger(__name__)

async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up Maestro Mobile from a config entry."""
    await hass.config_entries.async_forward_entry_setups(entry, ["button", "sensor"])

    # Listen for MQTT status messages from add-on
    @callback
    async def mqtt_status_listener(message):
        topic = message.topic
        payload = message.payload

        _LOGGER.error(f"Got stuff {topic}: {payload} {entry.entry_id}")

        if not topic.startswith("maestro_mobile/run_flow/status/"):
            return

        try:
            data = json.loads(payload)
            status = data.get("status")
            if status not in ("running", "success", "failed"):
                return

            flow_file = topic.split("/")[-1].replace(".yaml", "")
            entity_id = f"sensor.maestro_mobile_run_{flow_file}_status"

            # Update sensor state
            hass.states.async_set(entity_id, status)
        except Exception as e:
            _LOGGER.error(f"Failed to parse status from {topic}: {e}")

    await mqtt.async_subscribe(hass, "maestro_mobile/run_flow/status/#", mqtt_status_listener)

    return True

async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload a config entry."""
    await hass.config_entries.async_unload_platforms(entry, ["button", "sensor"])
    return True