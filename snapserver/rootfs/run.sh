#!/usr/bin/with-contenv bashio
declare username
declare password
declare ip

if bashio::config.has_value "spotify_user"; then
  username=$(bashio::config 'spotify_user')
  if bashio::config.has_value "spotify_pw"; then
    password=$(bashio::config 'spotify_pw')

    ip=$(host 40817795-mopidy.local.hass.io | awk '{ print $4 }')

    echo "stream = tcp://${ip}?name=mopidy_tcp&mode=client"
    echo "stream = librespot:///librespot?name=Spotify &" >>/etc/snapserver.conf
    echo "dryout_ms=2000 &" >>/etc/snapserver.conf
    echo "username=${username} &" >>/etc/snapserver.conf
    echo "password=${password} &" >>/etc/snapserver.conf
    echo "devicename=Snapcast &" >>/etc/snapserver.conf
    echo "bitrate=320 &" >>/etc/snapserver.conf
    echo "wd_timeout=7800 &" >>/etc/snapserver.conf
    echo "volume=100 &" >>/etc/snapserver.conf
    echo "nomalize=true &" >>/etc/snapserver.conf
    echo "autoplay=false" >>/etc/snapserver.conf
    echo "stream = meta:///mopidy_tcp/Spotify?name=Meta" >>/etc/snapserver.conf
  fi
fi

snapserver
