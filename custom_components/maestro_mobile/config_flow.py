import os
import yaml
import logging
import voluptuous as vol
from homeassistant import config_entries
from homeassistant.core import HomeAssistant
from homeassistant.data_entry_flow import FlowResult
from homeassistant.exceptions import HomeAssistantError
from homeassistant.helpers import selector

DOMAIN = "maestro_mobile"
FLOWS_DIR = "/config/maestro_flows"
_LOGGER = logging.getLogger(__name__)

class MaestroMobileFlow(config_entries.ConfigFlow, domain=DOMAIN):
    VERSION = 1

    def __init__(self):
        """Initialize the config flow."""
        self.entry_id = None
        self.flow_name = None
        self.flow_content = None
        self.device = None

    async def async_step_user(self, user_input=None) -> FlowResult:
        """Handle initial setup (create new flow)."""
        errors = {}

        if user_input is not None:
            self.flow_name = user_input["flow_name"]
            self.flow_content = user_input["flow_content"]
            self.device = user_input.get("device")

            # Validate YAML
            try:
                yaml.safe_load(self.flow_content)
            except yaml.YAMLError:
                errors["flow_content"] = "invalid_yaml"

            if not errors:
                # Save to file
                file_path = os.path.join(FLOWS_DIR, f"{self.flow_name}.yaml")
                os.makedirs(FLOWS_DIR, exist_ok=True)
                with open(file_path, "w") as f:
                    f.write(self.flow_content)

                # Unique ID = flow_name
                await self.async_set_unique_id(self.flow_name.lower().replace(" ", "_"))
                self._abort_if_unique_id_configured()

                return self.async_create_entry(
                    title=self.flow_name,
                    data={
                        "flow_name": self.flow_name,
                        "flow_file": f"{self.flow_name}.yaml",
                        "device": self.device
                    }
                )

        return self.async_show_form(
            step_id="user",
            data_schema=vol.Schema({
                vol.Required("flow_name"): selector.TextSelector(),
                vol.Required("flow_content"): selector.TextSelector(selector.TextSelectorConfig(multiline=True)),
                vol.Optional("device"): selector.TextSelector(),
            }),
            errors=errors
        )

    async def async_step_reconfigure(self, user_input=None) -> FlowResult:
        """Handle reconfigure (edit existing flow)."""
        entry = self._get_reconfigure_entry()
        errors = {}

        if user_input is not None:
            flow_name = user_input["flow_name"]
            flow_content = user_input["flow_content"]
            device = user_input.get("device", None)

            if not errors:
                old_flow_name = entry.data["flow_name"]
                old_file_path = os.path.join(FLOWS_DIR, f"{old_flow_name}.yaml")
                file_path = os.path.join(FLOWS_DIR, f"{flow_name}.yaml")

                if flow_name != old_flow_name and os.path.exists(old_file_path):
                    try:
                        os.remove(old_file_path)
                    except OSError as e:
                        _LOGGER.error(f"Failed to delete old file {old_file_path}: {e}")

                try:
                    with open(file_path, "w") as f:
                        f.write(flow_content)
                except OSError as e:
                    errors["base"] = f"Failed to save file: {e}"
                    return self.async_show_form(
                        step_id="reconfigure",
                        data_schema=vol.Schema({
                            vol.Required("flow_name", default=flow_name): selector.TextSelector(),
                            vol.Required("flow_content", default=flow_content): selector.TextSelector(selector.TextSelectorConfig(multiline=True)),
                            vol.Optional("device", description={ "suggested_value": device }): selector.TextSelector(),
                        }),
                        errors=errors
                    )

                self.hass.config_entries.async_update_entry(
                    entry,
                    title=flow_name,
                    data={
                        "flow_name": flow_name,
                        "flow_file": f"{flow_name}.yaml",
                        "device": device
                    }
                )

                # Reload the integration to refresh buttons/entities
                await self.hass.config_entries.async_reload(entry.entry_id)

                # Abort with success message (HA shows "Configuration updated")
                return self.async_abort(reason="reconfigure_successful")

        # Pre-fill with current values
        current = entry.data

        flow_name = current["flow_name"]
        file_path = os.path.join(FLOWS_DIR, f"{flow_name}.yaml")
        flow_content = ""
        if os.path.exists(file_path):
            try:
                with open(file_path, "r") as f:
                    flow_content = f.read()
            except Exception as e:
                _LOGGER.error(f"Failed to read flow file {file_path}: {e}")
                errors["flow_content"] = "file_read_error"
        else:
            _LOGGER.warning(f"Flow file missing: {file_path}")

        return self.async_show_form(
            step_id="reconfigure",
            data_schema=vol.Schema({
                vol.Required("flow_name", default=flow_name): selector.TextSelector(),
                vol.Required("flow_content", default=flow_content): selector.TextSelector(selector.TextSelectorConfig(multiline=True)),
                vol.Optional("device", description={ "suggested_value": current.get("device", "") }): selector.TextSelector(),
            }),
            errors=errors
        )