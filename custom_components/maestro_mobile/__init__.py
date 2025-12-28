from .button import MaestroRunButton

async def async_setup_entry(hass, entry):
    # Get config from entry
    flows_path = entry.data.get("flows_path", "/config/maestro_flows")
    mqtt_topic = entry.data.get("mqtt_topic", "maestro/run_flow")

    # Discover flows (list .yaml files)
    flows = [f for f in os.listdir(flows_path) if f.endswith('.yaml')]

    # Add buttons for each flow
    async_add_entities([MaestroRunButton(hass, f, flows_path, mqtt_topic) for f in flows])

    flows_path = entry.data["flows_path"]
    def create_flow(call):
        flow_name = call.data["flow_name"]
        flow_content = call.data["flow_content"]
        device = call.data.get("device")

        file_path = os.path.join(flows_path, flow_name)
        with open(file_path, 'w') as f:
            f.write(flow_content)

        # Optional: trigger run
        hass.services.async_call("mqtt", "publish", {
            "topic": entry.data["mqtt_topic"],
            "payload": f'{{"flow_file": "{flow_name}", "device": "{device}"}}'
        })

    hass.services.async_register("maestro_dev", "create_flow", create_flow)