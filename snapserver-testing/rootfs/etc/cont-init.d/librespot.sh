#!/usr/bin/with-contenv bashio
declare name
declare pipe
declare device_type
declare bitrate
declare additional_opts

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
    else
      additional_opts=""
    fi
    bashio::log.info "Addional Options: ${additional_opts}"

    path=$(echo ${name} | sed -f /etc/url_escape.sed)
    mkdir /etc/services.d/${path}

    json=bashio::var.json \
      name ${name} \
      pipe ${pipe} \
      device_type ${device_type} \
      bitrate ${bitrate} \
      additional_opts ${additional_opts}
    echo ${json} |
      tempio \
        -template /etc/librespot/template.gtpl \
        -out /etc/services.d/${path}/run

    cp /etc/librespot/finish /etc/services.d/${path}/finish
  done
fi
