"""Maestro Mobile integration."""
import os
import json
import logging
import homeassistant.helpers.device_registry as dr
import homeassistant.helpers.entity_registry as er
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant, callback
from homeassistant.helpers import entity_platform, service
from homeassistant.helpers.device_registry import DeviceEntry
from homeassistant.components import mqtt

DOMAIN = "maestro_mobile"
_LOGGER = logging.getLogger(__name__)

async def cleanup_orphaned_devices(hass: HomeAssistant, entry_id: str) -> None:
    """Remove devices for our domain that have no entities left."""
    device_registry = dr.async_get(hass)
    entity_registry = er.async_get(hass)

    # Get devices linked to this config entry
    entry_devices = device_registry.devices.get_devices_for_config_entry_id(entry_id)

    for device in entry_devices:
        # Get all entities currently linked to this device
        device_entities = er.async_entries_for_device(entity_registry, device.id)
        device_entity_ids = {e.entity_id for e in device_entities}

        # Get all entities linked to this config entry
        entry_entities = entity_registry.entities.get_entries_for_config_entry_id(entry_id)
        entry_entity_ids = {e.entity_id for e in entry_entities}

        remaining = entry_entity_ids & device_entity_ids

        if not remaining:
            if not device_entities:
                device_registry.async_remove_device(device.id)
                _LOGGER.info(f"Removed orphaned device: {device.id}")
            else:
                # No more entities from this entry on this device → unlink
                device_registry.async_update_device(device.id, remove_config_entry_id=entry_id)
                _LOGGER.info(f"Unlinked config entry {entry_id} from device {device.id} (no remaining entities)")

async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up Maestro Mobile from a config entry."""
    await hass.config_entries.async_forward_entry_setups(entry, ["sensor", "button"])

    # Clean up any orphans after setup
    await cleanup_orphaned_devices(hass, entry.entry_id)

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

            # Update sensor state
            entry.runtime_data["sensor"].update_state(status)
        except Exception as e:
            _LOGGER.error(f"Failed to parse status from {topic}: {e}")

    unsubscribe_func = await mqtt.async_subscribe(hass, f"maestro_mobile/run_flow/status/{entry.entry_id}", mqtt_status_listener)

    # Store the unsubscribe func for later cleanup
    hass.data.setdefault(DOMAIN, {})[entry.entry_id] = {"unsubscribe": unsubscribe_func}

    return True

async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload a config entry."""
    await hass.config_entries.async_unload_platforms(entry, ["button", "sensor"])

    # Unsubscribe from MQTT
    entry_data = hass.data.get(DOMAIN, {}).get(entry.entry_id)
    if entry_data and "unsubscribe" in entry_data:
        unsubscribe_func = entry_data["unsubscribe"]
        unsubscribe_func()  # Call it to unsubscribe
        _LOGGER.info(f"Unsubscribed from MQTT topic for entry {entry.entry_id}")

        # Clean up storage
        hass.data[DOMAIN].pop(entry.entry_id, None)

    # Clean up orphans after unload
    await cleanup_orphaned_devices(hass, entry.entry_id)

    return True

async def async_remove_config_entry_device(
    hass: HomeAssistant, config_entry: ConfigEntry, device_entry: DeviceEntry
) -> bool:
    return True