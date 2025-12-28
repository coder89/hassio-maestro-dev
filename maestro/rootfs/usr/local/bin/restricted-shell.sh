#!/usr/bin/env bashio

bashio::log.info "Welcome to the ADB Server restricted shell. Only 'adb', 'wget', 'curl' and 'maestro' commands are allowed."

while true; do
    # Use read -ra to properly split cmd and args into an array
    read -r -p "# " -a input

    cmd="${input[0]}"
    args=("${input[@]:1}")

    if [[ "$cmd" == "adb" && "${args[0]}" == "connect" ]]; then
        # Handle adb connect command separately
        /usr/local/bin/adb_connect.sh "${args[@]:1}"
    elif [[ "$cmd" == "adb" ]]; then
        # Pass all arguments to adb safely
        adb "${args[@]}"
    elif [[ "$cmd" == "maestro" ]]; then
        # Pass all arguments to maestro safely
        maestro "${args[@]}"
    elif [[ "$cmd" == "curl" || "$cmd" == "wget" ]]; then
        if [[ "${args[-1]}" == *.apk ]]; then
            # Allow only .apk file downloads
            "$cmd" "${args[@]}"
        else
            bashio::log.info "Only .apk files are allowed"
        fi
    elif [[ "$cmd" == "exit" || "$cmd" == "quit" ]]; then
        bashio::log.info "Exiting restricted shell."
        exit 0
    else
        bashio::log.info "Only 'adb', 'wget', 'curl' and 'maestro' commands are allowed."
    fi
done
