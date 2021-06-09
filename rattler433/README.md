# Home Assistant Add-on: Rattler 433

Rattler 433 (rtl_433 for Home Assistant)

![Supports aarch64 Architecture][aarch64-shield] ![Supports amd64 Architecture][amd64-shield] ![Supports armhf Architecture][armhf-shield] ![Supports armv7 Architecture][armv7-shield] ![Supports i386 Architecture][i386-shield]

## About

This add-on provides `rtl_433` preconfigured for easy integration into Home Assistant. The default configuration should cover most use cases, and comes with support for the Sonoff RM433 8 button remote.

This add-on requires that Mosquitto MQTT broker be installed, as it is required.

The default configuration creates MQTT messages on topics formatted as: `prefix/model/channel/id`, which makes creating MQTT entities in Home Assistant easier.

[aarch64-shield]: https://img.shields.io/badge/aarch64-yes-green.svg
[amd64-shield]: https://img.shields.io/badge/amd64-yes-green.svg
[armhf-shield]: https://img.shields.io/badge/armhf-yes-green.svg
[armv7-shield]: https://img.shields.io/badge/armv7-yes-green.svg
[i386-shield]: https://img.shields.io/badge/i386-yes-green.svg