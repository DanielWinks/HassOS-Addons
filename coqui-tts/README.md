# Home Assistant Add-on: Coqui TTS

Coqui TTS (Coqui TTS for Home Assistant)

![Supports amd64 Architecture][amd64-shield]

## About

This add-on provides `Coqui TTS` set up for use with Snapcast. The primary REST endpoint expects a JSON object similar to this example:

```json
{
  "text": "Warning! Unruly children will be jettisoned from the nearest airlock.", //required
  "fifo": "/share/snapfifo", //required
  "prepend_wav": "alertklaxon_clean.wav" //optional
}
```

This endpoint is available at http://6172d6c4-coqui-tts-hassio:5002/tts

A properly formatted JSON object, like the example above, will result in the text message being played to the fifo specified. In normal use, this would be a fifo being used by Snapcast, such as provided by the Snapcast add-on available in this repo.

[amd64-shield]: https://img.shields.io/badge/amd64-yes-green.svg
