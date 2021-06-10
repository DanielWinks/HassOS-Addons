#!/usr/bin/with-contenv bashio
declare host
declare password
declare port
declare username
declare retain
declare qos
declare refresh
declare output
declare client_id
declare prefix
declare topic
declare log_level
declare rest_port
declare prometheus_port


if ! bashio::services.available "mqtt"; then
    bashio::log.info "No internal MQTT service found"
    if bashio::config.has_value "mqtt_host"; then
        host=$(bashio::config 'mqtt_host')
    else
        bashio::log.info "No external MQTT service defined"
    fi
    if bashio::config.has_value "mqtt_port"; then
        port=$(bashio::config 'mqtt_port')
    else
        bashio::log.info "No external MQTT service defined"
    fi
    if bashio::config.has_value "mqtt_user"; then
        username=$(bashio::config 'mqtt_user')
    else
        bashio::log.info "No external MQTT service defined"
    fi
    if bashio::config.has_value "mqtt_pass"; then
        password=$(bashio::config 'mqtt_pass')
    else
        bashio::log.info "No external MQTT service defined"
    fi
else
    host=$(bashio::services "mqtt" "host")
    password=$(bashio::services "mqtt" "password")
    port=$(bashio::services "mqtt" "port")
    username=$(bashio::services "mqtt" "username")
fi

if bashio::config.true 'mqtt_retain'; then
    retain="1"
else
    retain="0"
fi

if bashio::config.has_value 'mqtt_refresh'; then
    refresh=$(bashio::config 'mqtt_refresh')
else
    refresh="30"
fi

if bashio::config.has_value 'rest_port'; then
    rest_port=$(bashio::config 'rest_port')
else
    rest_port="5003"
fi

if bashio::config.has_value 'prometheus_port'; then
    prometheus_port=$(bashio::config 'prometheus_port')
else
    prometheus_port="9222"
fi

client_id=$(bashio::config 'mqtt_prefix')
prefix=$(bashio::config 'mqtt_prefix')
topic=$(bashio::config 'mqtt_topic')
# Remove leading slash if there is one.
[[ $topic =~ ^/(.*)$ ]] && topic=${BASH_REMATCH[1]}
qos=$(bashio::config 'mqtt_qos')

log_level=$(bashio::config 'log_level')

read -r -d '' output << EOM
pwrstat_api:
  log_level: ${log_level}
mqtt:
  broker: "\"${host}\""
  port: ${port}
  client_id: ${client_id}
  topic: "${prefix}/${topic}"
  refresh: ${refresh}
  qos: ${qos}
  retained: ${retain}
  username: "${username}"
  password: "${password}"
rest:
  port: ${rest_port}
  bind_address: "0.0.0.0"
prometheus:
  port: ${prometheus_port}
  bind_address: "0.0.0.0"
  labels:
    rack: "0"
EOM

echo ${output} >/pwrstat.yaml

/pwrstat_api.py