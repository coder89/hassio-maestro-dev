from homeassistant.components.frontend import add_extra_js_url
from homeassistant.components import panel_custom

async def async_setup_entry(hass, entry):
    # ... existing code ...

    # Register custom panel (e.g. a simple form to list/edit flows)
    hass.components.frontend.async_register_built_in_panel(
        component_name="custom",
        sidebar_title="Maestro Flows",
        sidebar_icon="mdi:file-document-edit",
        frontend_url_path="maestro_flows",
        config={
            "js_url": "/local/maestro_flows.js",  # Custom JS for form if needed
            "embed_iframe": true,
        }
    )