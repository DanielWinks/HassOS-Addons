#!/usr/bin/with-contenv bashio
declare name
declare pipe
declare device_type
declare bitrate
declare additional_opts
declare json_values

if bashio::config.true "start_librespot"; then
  for librespot in $(bashio::config 'librespot_instances|keys'); do

    name=$(bashio::config "librespot_instances[${librespot}].name")
    pipe=$(bashio::config "librespot_instances[${librespot}].pipe")
    bashio::log.info "Processing ${name} at ${pipe}"

    if bashio::config.has_value 'device_type'; then
      device_type=$(bashio::config 'device_type')
    else
      device_type="speaker"
    fi
    bashio::log.info "Device Type: ${device_type}"

    if bashio::config.has_value 'bitrate'; then
      bitrate=$(bashio::config 'bitrate')
    else
      bitrate="320"
    fi
    bashio::log.info "Bitrate: ${bitrate}"

    if bashio::config.has_value 'additional_opts'; then
      additional_opts=$(bashio::config 'additional_opts')
      bashio::log.info "Addional Options: ${additional_opts}"
    fi

    path=$(echo ${name} | sed -f /etc/url_escape.sed)
    mkdir /etc/services.d/${path}

    if bashio::config.has_value 'additional_opts'; then
      json_values="{
        \"name\":\"${name}\",
        \"pipe\":\"${pipe}\",
        \"device_type\":\"${device_type}\",
        \"bitrate\":\"${bitrate}\",
        \"additional_opts\":\"${additional_opts}\"
      }"
    else
      json_values="{
        \"name\":\"${name}\",
        \"pipe\":\"${pipe}\",
        \"device_type\":\"${device_type}\",
        \"bitrate\":\"${bitrate}\",
        \"additional_opts\":\"\"
      }"
    fi

    echo ${json_values} |
      tempio \
        -template /etc/librespot/template.gtpl \
        -out /etc/services.d/${path}/run

    cp /etc/librespot/finish /etc/services.d/${path}/finish
  done
fi
