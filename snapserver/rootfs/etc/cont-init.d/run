#!/usr/bin/with-contenv bashio
declare name
declare pipe
declare stream

if ! bashio::fs.directory_exists "/data/snapcast"; then
  mkdir -p /data/snapcast ||
    bashio::exit.nok "Could not create Snapcast config folder!"
fi

if bashio::config.true "create_tts_fifo_in_share"; then
  pipe=/share/snapfifo
  if [[ ! -p $pipe ]]; then
    mkfifo $pipe ||
      bashio::exit.nok "Could not create named pipe!"
    chmod 666 $pipe ||
      bashio::exit.nok "Could not set permissions on pipe!"
  fi
  echo "source = pipe:///${pipe}?name=TTS" >>/etc/snapserver.conf
  bashio::log.info "Created pipe at ${pipe}"
fi

if bashio::config.true "start_librespot"; then
  for librespot in $(bashio::config 'librespot_instances|keys'); do

    name=$(bashio::config "librespot_instances[${librespot}].name")
    pipe=$(bashio::config "librespot_instances[${librespot}].pipe")

    if [[ ! -p $pipe ]]; then
      mkfifo $pipe ||
        bashio::exit.nok "Could not create named pipe for ${name}!"
      chmod 666 $pipe ||
        bashio::exit.nok "Could not set permissions on pipe for ${name}!"
    fi

    stream="source = pipe:///${pipe}?name=${name}"
    echo ${stream} >>/etc/snapserver.conf
    bashio::log.info "Snapcast Conf: ${stream}"

    if bashio::config.true "create_tts_fifo_in_share"; then
      stream="source = meta:///TTS/${name}?name=${name} + TTS"
      echo ${stream} >>/etc/snapserver.conf
      bashio::log.info "Snapcast Conf: ${stream}"
    fi

  done
fi
