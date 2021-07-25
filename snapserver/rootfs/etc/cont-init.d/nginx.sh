#!/usr/bin/with-contenv bashio
# ==============================================================================
# Home Assistant Community Add-on: Mopidy
# Configures NGINX
# ==============================================================================

# Generate Ingress configuration
bashio::var.json \
    interface "$(bashio::addon.ip_address)" \
    entry "$(bashio::addon.ingress_entry)" \
    | tempio \
        -template /etc/nginx/templates/ingress.gtpl \
        -out /etc/nginx/servers/ingress.conf

