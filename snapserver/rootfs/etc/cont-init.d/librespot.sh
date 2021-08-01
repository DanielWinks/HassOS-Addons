#!/usr/bin/with-contenv bashio
declare name
declare pipe
declare silence
declare device_type
declare bitrate
declare additional_opts

silence=""
if bashio::config.true "silence_librespot"; then
  silence=">/dev/null 2>&1"
  bashio::log.info "Silencing Librespot"
fi

if bashio::config.true "start_librespot"; then
  for librespot in $(bashio::config 'librespot_instances|keys'); do

    name=$(bashio::config "librespot_instances[${librespot}].name")
    pipe=$(bashio::config "librespot_instances[${librespot}].pipe")

    if bashio::config.has_value 'device_type'; then
      device_type=$(bashio::config 'device_type')
    else
      device_type="speaker"
    fi

    if bashio::config.has_value 'bitrate'; then
      bitrate=$(bashio::config 'bitrate')
    else
      bitrate="320"
    fi

    if bashio::config.has_value 'additional_opts'; then
      additional_opts=$(bashio::config 'additional_opts')
    else
      additional_opts=""
    fi

    path=$(echo ${name} | sed -f /etc/cont-init.d/url_escape.sed)
    mkdir /etc/services.d/${path}

    bashio::var.json \
      name ${name} \
      pipe ${pipe} \
      device_type ${device_type} \
      bitrate ${bitrate} \
      additional_opts ${additional_opts} |
      tempio \
        -template /etc/librespot/template.gtpl \
        -out /etc/services.d/${path}/run

    cp /etc/librespot/finish /etc/services.d/${path}/finish
  done
fi
