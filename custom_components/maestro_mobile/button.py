from homeassistant.components.button import ButtonEntity

class MaestroRunButton(ButtonEntity):
    def __init__(self, hass, flow_file, flows_path, mqtt_topic):
        self._hass = hass
        self._flow_file = flow_file
        self._flows_path = flows_path
        self._mqtt_topic = mqtt_topic
        self._attr_name = f"Run Maestro {flow_file.replace('.yaml', '')}"
        self._attr_unique_id = f"maestro_run_{flow_file}"
        self._attr_icon = "mdi:play-circle"

    async def async_press(self):
        # Trigger add-on via MQTT (or HTTP if preferred)
        await self._hass.services.async_call(
            "mqtt", "publish",
            {"topic": self._mqtt_topic, "payload": f'{{"flow_file": "{self._flow_file}"}}'}
        )