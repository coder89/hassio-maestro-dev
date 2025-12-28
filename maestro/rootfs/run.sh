#!/usr/bin/env bashio
set -e

# Setup persistent ADB keys
if [ ! -d /config/.android ]; then
  mkdir -p /config/.android
fi
ln -sf /config/.android /root/.android

# Get the configured ADB port
ADB_PORT=$(bashio::config 'adb_port' '5037')

# Start ADB server
adb -a -P "${ADB_PORT}" start-server
bashio::log.info "ADB server started on port ${ADB_PORT}"

# Auto-connect to configured devices
AUTO_CONNECT_DEVICES=$(bashio::config 'auto_connect_devices' '')
bashio::log.info "Devices to auto-connect: ${AUTO_CONNECT_DEVICES}"

if [ -n "${AUTO_CONNECT_DEVICES}" ]; then
    IFS=',' read -r -a devices <<< "${AUTO_CONNECT_DEVICES}"
    bashio::log.info "Attempting to connect to configured devices"
    /usr/local/bin/adb_connect.sh "${devices[@]}"
else
    bashio::log.info "No devices configured for auto-connect"
fi

# ── Check for connected devices ──────────────────────────────────────
# Count lines after header that contain "device" (not emulator/offline/etc.)
CONNECTED_COUNT=$(adb devices | awk 'NR>1 && $2 == "device" {count++} END {print count+0}')

# List connected devices
bashio::log.info "Connected devices:"
adb devices -l

# Start ttyd with writable mode and restricted shell
ttyd -p 7681 --writable /usr/local/bin/restricted-shell.sh &

# Start Maestro Studio if enabled
ENABLE_STUDIO=$(bashio::config 'enable_studio' 'false')
if [ "${ENABLE_STUDIO}" = "true" ]; then
    if [ "${CONNECTED_COUNT}" -gt 0 ]; then
        bashio::log.info "Starting Maestro Studio..."
        maestro studio --no-window 2>&1 &
    else
        bashio::log.warning "No devices connected via ADB → skipping Maestro Studio startup"
        bashio::log.info "Tip: Check 'adb devices' or add auto_connect_devices in config"
    fi
fi

/usr/local/bin/maestro_service.sh &

# Keep the add-on running
tail -f /dev/null
