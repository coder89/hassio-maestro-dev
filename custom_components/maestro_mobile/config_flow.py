from homeassistant import config_entries
from homeassistant.data_entry_flow import FlowResult
from homeassistant.helpers import selector

class MaestroConfigFlow(config_entries.ConfigFlow, domain="maestro_dev"):
    """Handle config flow for Maestro DEV."""

    VERSION = 1

    async def async_step_user(self, user_input=None) -> FlowResult:
        """Handle the initial step."""
        if user_input is not None:
            # Save user input (e.g., flows path)
            await self.async_set_unique_id("maestro_dev_unique")
            return self.async_create_entry(title="Maestro DEV", data=user_input)

        # Show form in UI
        return self.async_show_form(
            step_id="user",
            data_schema=vol.Schema({
                vol.Optional("flows_path", default="/config/maestro_flows"): str,
                vol.Optional("mqtt_topic", default="maestro/run_flow"): str,
            })
        )