#!/usr/bin/with-contenv bashio
silence=""
name="{{ .name }}"
pipe="{{ .pipe }}"
device_type="{{ .device_type }}"
bitrate="{{ .bitrate }}"
additional_opts="{{ .additional_opts }}"

if bashio::config.true "silence_librespot"; then
  silence=">/dev/null 2>&1"
  bashio::log.info "Silencing Librespot"
fi

bashio::log.info "Starting ${name} Librespot at ${pipe}"
exec /usr/bin/librespot \
  --name "${name}" \
  --device-type ${device_type} \
  --backend pipe \
  --device ${pipe} \
  --bitrate ${bitrate} \
  --disable-audio-cache \
  --enable-volume-normalisation \
  --volume-ctrl linear \
  --initial-volume=100 \
  ${additional_opts} \
  ${silence}
