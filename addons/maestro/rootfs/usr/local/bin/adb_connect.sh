#!/usr/bin/env bashio
set -e

# Function to connect and wait for authorization
connect_device() {
    local device_ip="$1"
    local retries=30
    local count=0

    set +e
    adb connect "$device_ip";
    set -e

    while true; do
        if [ $count -ge $retries ]; then
            bashio::log.error "Failed to authorize device $device_ip after $retries attempts."
            return 1
        fi

        # Check the device state
        set +e
        device_state=$(adb -s "$device_ip" get-state 2>&1);
        set -e

        if [ "$device_state" = "device" ]; then
            bashio::log.info "Device $device_ip connected and authorized."
            return 0
        elif [ "$device_state" = "unauthorized" ]; then
            bashio::log.info "Waiting for device $device_ip to be authorized... (Attempt $((count+1))/$retries)"
        else
            bashio::log.info "Attempting to connect to device $device_ip... (Attempt $((count+1))/$retries)"
            set +e
            adb connect "$device_ip" >/dev/null 2>&1;
            set -e
        fi

        sleep 2
        count=$((count+1))
    done
}

# Check if any arguments were provided
if [ $# -eq 0 ]; then
    bashio::log.info "Usage: $0 <device_ip1> [<device_ip2> ...]"
    exit 1
fi

# Iterate over all provided device IPs
for device_ip in "$@"; do
    connect_device "$device_ip";
done

# List all connected devices
bashio::log.info "Connected devices:"
adb devices -l
