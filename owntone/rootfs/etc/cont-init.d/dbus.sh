#!/usr/bin/with-contenv bash

mkdir -p \
  /var/run/dbus

[[ -e /var/run/dbus.pid ]] &&
  rm -f /var/run/dbus.pid

dbus-uuidgen --ensure
sleep 1
