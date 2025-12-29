#!/usr/bin/env bashio

set +e

FLOW_DIR="/homeassistant/maestro_flows"

bashio::log.info "Listening for run_flow service calls..."

MQTT_HOST=$(bashio::services mqtt "host")
MQTT_PORT=$(bashio::services mqtt "port")
MQTT_USER=$(bashio::services mqtt "username")
MQTT_PASS=$(bashio::services mqtt "password")

notify_state() {
    local flowId="$1"
    local state="$2"
    local auto_disable="$3"

    mosquitto_pub \
      -h "$MQTT_HOST" \
      -p "$MQTT_PORT" \
      -u "$MQTT_USER" \
      -P "$MQTT_PASS" \
      -t "maestro_mobile/run_flow/status/${flowId}" \
      -m "{\"status\": \"${state}\",\"disable\":${auto_disable}}";
}

# Subscribe to trigger topic
while true; do
    payload=$(
      mosquitto_sub \
        -h "$MQTT_HOST" \
        -p "$MQTT_PORT" \
        -u "$MQTT_USER" \
        -P "$MQTT_PASS" \
        -t "maestro_mobile/run_flow" \
        -C 1 \
        -R \
        -N
    );

    bashio::log.info "Received payload: $payload"

    FLOW_ID=$(echo "$payload" | jq -r '.id')
    FLOW_FILE=$(echo "$payload" | jq -r '.flow_file')
    DEVICE=$(echo "$payload" | jq -r '.device // ""')
    AUTO_DISABLE=$(bashio::config 'auto_disable_triggers' false)

    bashio::log.info "Service called for flow id $FLOW_ID"

    if [ -n "$DEVICE" ]; then
        if ! adb -s "$DEVICE" devices | grep -q "$DEVICE"; then
            bashio::log.error "Device $DEVICE not connected/authorized - skipping Maestro run"
            continue
        fi
        export ADB_SERIAL="$DEVICE"
    else
        unset ADB_SERIAL
    fi

    if [ -n "$DEVICE" ]; then
        bashio::log.info "Running flow '$FLOW_FILE' on default device"
    else
        bashio::log.info "Running flow '$FLOW_FILE' on device '$DEVICE'"
    fi

    (
        notify_state "$FLOW_ID" "running" "$AUTO_DISABLE"

        FLOW_PATH="${FLOW_DIR}/${FLOW_FILE}"
        maestro test "$FLOW_PATH" 2>&1

        if [ $? -eq 0 ]; then
            notify_state "$FLOW_ID" "success" "$AUTO_DISABLE"
        else
            notify_state "$FLOW_ID" "failed" "$AUTO_DISABLE"
        fi
    ) &
done
