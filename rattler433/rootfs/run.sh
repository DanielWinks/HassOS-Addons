#!/usr/bin/with-contenv bashio
declare host
declare password
declare port
declare username
declare retain
declare output
declare prefix
declare customize_dir


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

if bashio::config.true 'retain'; then
    retain="1"
else
    retain="0"
fi

prefix=$(bashio::config 'mqtt_prefix')

output="output mqtt://${host}:${port},user=${username},pass=${password},retain=${retain},devices=${prefix}[/model][/channel][/id]"

echo ${output} >/rattler/output.conf

if bashio::config.true 'customize.active'; then
    customize_dir=$(bashio::config 'customize.folder')
    if [ -d "/share/${customize_dir}" ]; then
        cat /share/${customize_dir}/*.conf >> /rattler/rtl_433.conf
    fi
fi

rtl_433 -c /rattler/rtl_433.conf -c /rattler/sonoff_rm433.conf -c /rattler/output.conf
