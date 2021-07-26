#!/usr/bin/with-contenv bashio

bashio::var.json \
  interface "$(bashio::addon.ip_address)" \
  entry "$(bashio::addon.ingress_entry)" |
  tempio \
    -template /etc/nginx/templates/ingress.gtpl \
    -out /etc/nginx/servers/ingress.conf
