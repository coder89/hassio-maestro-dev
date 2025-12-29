#!/usr/bin/env bashio

set +e

FLOW_DIR="/homeassistant/maestro_flows"

bashio::log.info "Listening for run_flow service calls..."

MQTT_HOST=$(bashio::services mqtt "host")
MQTT_PORT=$(bashio::services mqtt "port")
MQTT_USER=$(bashio::services mqtt "username")
MQTT_PASS=$(bashio::services mqtt "password")

bashio::log.info "$MQTT_HOST"
bashio::log.info "$MQTT_PORT"
bashio::log.info "$MQTT_USER"
bashio::log.info "$MQTT_PASS"

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
        mosquitto_pub \
          -h "$MQTT_HOST" \
          -p "$MQTT_PORT" \
          -u "$MQTT_USER" \
          -P "$MQTT_PASS" \
          -t "maestro_mobile/run_flow/status/${FLOW_ID}" \
          -m '{"status": "running"}';

        FLOW_PATH="${FLOW_DIR}/${FLOW_FILE}"
        maestro test "$FLOW_PATH" 2>&1

        if [ $? -eq 0 ]; then
            mosquitto_pub \
              -h "$MQTT_HOST" \
              -p "$MQTT_PORT" \
              -u "$MQTT_USER" \
              -P "$MQTT_PASS" \
              -t "maestro_mobile/run_flow/status/${FLOW_ID}" \
              -m '{"status": "success"}';
        else
            mosquitto_pub \
              -h "$MQTT_HOST" \
              -p "$MQTT_PORT" \
              -u "$MQTT_USER" \
              -P "$MQTT_PASS" \
              -t "maestro_mobile/run_flow/status/${FLOW_ID}" \
              -m '{"status": "failed"}';
        fi
    ) &
done
