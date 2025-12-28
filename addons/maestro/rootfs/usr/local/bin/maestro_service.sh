#!/usr/bin/env bashio

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
        -t "maestro/run_flow" \
        -C 1 \
        -R \
        -N
    );

    FLOW_NAME=$(echo "$payload" | jq -r '.name' 2> /dev/null)
    FLOW_DATA=$(echo "$payload" | jq -r '.flow' 2> /dev/null)
    DEVICE=$(echo "$payload" | jq -r '.device' 2> /dev/null)
    bashio::log.info "Service called! Running flow '$FLOW_NAME' on device '$DEVICE'"
    bashio::log.info "Flow data: $FLOW_DATA"
        # maestro run "$FLOW_NAME" &
done
