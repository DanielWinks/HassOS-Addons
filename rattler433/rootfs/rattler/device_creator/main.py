#!/usr/local/bin/python3
"""Get device config from Home Assistant Add-On configuration options and create devices in Home Assistant"""
import json
import logging
from json import JSONDecodeError
from typing import Any, Dict, List, Tuple

import paho.mqtt.publish as publish

_LOGGER = logging.getLogger("Main")
prefix = "rtl_433"
disc = "homeassistant"


def create_devices() -> None:

    with open("/data/options.json") as file:
        try:
            options_json: Dict[str, Any] = json.load(file)
        except JSONDecodeError as ex:
            _LOGGER.log(level=logging.ERROR, msg=ex)

    with open("/data/mqtt.json") as file:
        try:
            mqtt_json: Dict[str, Any] = json.load(file)
        except JSONDecodeError as ex:
            _LOGGER.log(level=logging.ERROR, msg=ex)

    global disc
    disc = options_json["ha_discovery_topic"]
    global prefix
    prefix = options_json["mqtt_prefix"]

    _LOGGER.info(f"Publishing to HA Discovery Topic: {disc}")

    devices: List[Dict] = options_json["devices"]
    msgs = []
    for device in devices:
        manu = device["manufacturer"]
        model = device["model"]
        name = device["name"]
        if "uid" in device.keys():
            uid = device["uid"]
        if "id" in device.keys():
            id = device["id"]
        if "channel" in device.keys():
            channel = device["channel"]
        _LOGGER.info(f"Creating device: {name}")
        if device["type"] == "motion":
            msgs.extend(create_motion(manu, model, uid, name))
        elif device["type"] == "contact":
            msgs.extend(create_contact(manu, model, uid, name))
        elif device["type"] == "glassbreak":
            msgs.extend(create_glassbreak(manu, model, uid, name))
        elif device["type"] == "temp_hum_f":
            msgs.extend(create_temp_hum_f(manu, model, channel, id, name))
        elif device["type"] == "temp_hum_c":
            msgs.extend(create_temp_hum_c(manu, model, channel, id, name))
        elif device["type"] == "temp_hum_f_to_c":
            msgs.extend(create_temp_hum_f_to_c(manu, model, channel, id, name))
        elif device["type"] == "temp_hum_c_to_f":
            msgs.extend(create_temp_hum_c_to_f(manu, model, channel, id, name))
        elif device["type"] == "sonoff_remote":
            msgs.extend(create_sonoff_remote(manu, model, uid, name))

    mqtt_user = mqtt_json["mqtt_user"]
    mqtt_pass = mqtt_json["mqtt_pass"]
    mqtt_host = mqtt_json["mqtt_host"]
    mqtt_port = mqtt_json["mqtt_port"]
    publish.multiple(
        msgs=msgs,
        hostname=mqtt_host,
        port=mqtt_port,
        client_id="rattler_mqtt_creator",
        auth={"username": mqtt_user, "password": mqtt_pass},
    )


def _lstr(input_str: str) -> str:
    return input_str.lower().replace("-", "_")


def _mstr(input_str: str) -> str:
    return _lstr(input_str).replace(" ", "_").replace("/", "_")


def _create_device(manufacturer, model, dev_name, uid):
    id = {"identifiers": [f"{_lstr(manufacturer)}_{_lstr(model)}_{_mstr(uid)}"]}
    manu = {"manufacturer": f"{manufacturer}"}
    mod = {"model": f"{model}"}
    name = {"name": f"{dev_name}"}
    device = {"device": {**id, **manu, **mod, **name}}
    return device


def _create_battery(dev_name, manufacturer, model, uid):
    payload = {**_create_device(manufacturer, model, dev_name, uid)}
    payload["name"] = dev_name + " Battery"
    payload["value_template"] = "{% if value|int == 1 %}100{% else %}10{% endif %}"
    payload["unit_of_measurement"] = "%"
    payload["device_class"] = "battery"
    payload["force_update"] = "true"
    payload["unique_id"] = f"{_lstr(manufacturer)}_{_lstr(model)}_{_mstr(uid)}_battery"
    payload["state_topic"] = f"{prefix}/{manufacturer}/{uid}/battery_ok"
    return str(json.dumps(payload))


def _create_button(dev_name, manufacturer, model, uid, type, subtype, button_payload):
    payload = {**_create_device(manufacturer, model, dev_name, uid)}
    payload["type"] = f"{type}"
    payload["subtype"] = f"{subtype}"
    payload["payload"] = f"{button_payload}"
    payload["topic"] = f"{prefix}/{manufacturer}/{uid}/button"
    payload["automation_type"] = "trigger"
    return str(json.dumps(payload))


def _create_tamper(dev_name, manufacturer, model, uid):
    payload = {**_create_device(manufacturer, model, dev_name, uid)}
    payload["name"] = dev_name + " Tamper"
    payload["device_class"] = "problem"
    payload["payload_on"] = 1
    payload["payload_off"] = 0
    payload["force_update"] = "true"
    payload["unique_id"] = f"{_lstr(manufacturer)}_{_lstr(model)}_{_mstr(uid)}_tamper"
    payload["state_topic"] = f"{prefix}/{manufacturer}/{uid}/tamper"
    return str(json.dumps(payload))


def _create_time(dev_name, manufacturer, model, uid):
    payload = {**_create_device(manufacturer, model, dev_name, uid)}
    payload["name"] = dev_name + " Time"
    payload["device_class"] = "timestamp"
    payload["unique_id"] = f"{_lstr(manufacturer)}_{_lstr(model)}_{_mstr(uid)}_time"
    payload["state_topic"] = f"{prefix}/{manufacturer}/{uid}/time"
    return str(json.dumps(payload))


def _create_motion_event(dev_name, manufacturer, model, uid):
    payload = {**_create_device(manufacturer, model, dev_name, uid)}
    payload["name"] = dev_name + " Event"
    payload["device_class"] = "motion"
    payload["payload_on"] = 1
    payload["payload_off"] = 0
    payload["off_delay"] = 15
    payload["unique_id"] = f"{_lstr(manufacturer)}_{_lstr(model)}_{_mstr(uid)}_event"
    payload["state_topic"] = f"{prefix}/{manufacturer}/{uid}/event"
    return str(json.dumps(payload))


def _create_contact(dev_name, manufacturer, model, uid):
    payload = {**_create_device(manufacturer, model, dev_name, uid)}
    payload["name"] = dev_name + " Contact"
    payload["device_class"] = "door"
    payload["payload_on"] = 0
    payload["payload_off"] = 1
    payload["unique_id"] = f"{_lstr(manufacturer)}_{_lstr(model)}_{_mstr(uid)}_closed"
    payload["state_topic"] = f"{prefix}/{manufacturer}/{uid}/closed"
    return str(json.dumps(payload))


def _create_contact2(dev_name, manufacturer, model, uid):
    payload = {**_create_device(manufacturer, model, dev_name, uid)}
    payload["name"] = dev_name + " Contact"
    payload["device_class"] = "door"
    payload["payload_on"] = 1
    payload["payload_off"] = 0
    payload["unique_id"] = f"{_lstr(manufacturer)}_{_lstr(model)}_{_mstr(uid)}_opened"
    payload["state_topic"] = f"{prefix}/{manufacturer}/{uid}/opened"
    return str(json.dumps(payload))


def _create_glassbreak_event(dev_name, manufacturer, model, uid):
    payload = {**_create_device(manufacturer, model, dev_name, uid)}
    payload["name"] = dev_name + " Event"
    payload["device_class"] = "sound"
    payload["payload_on"] = 1
    payload["payload_off"] = 0
    payload["off_delay"] = 1
    payload["unique_id"] = f"{_lstr(manufacturer)}_{_lstr(model)}_{_mstr(uid)}_event"
    payload["state_topic"] = f"{prefix}/{manufacturer}/{uid}/event"
    return str(json.dumps(payload))


def _create_humidity(dev_name, manufacturer, model, uid):
    payload = {**_create_device(manufacturer, model, dev_name, uid)}
    payload["name"] = dev_name + " Humidity"
    payload["device_class"] = "humidity"
    payload["force_update"] = "true"
    payload["unit_of_measurement"] = "%"
    payload["value_template"] = "{{value|int}}"
    payload["unique_id"] = f"{_lstr(manufacturer)}_{_lstr(model)}_{_mstr(uid)}_humidity"
    payload["state_topic"] = f"{prefix}/{manufacturer}/{uid}/humidity"
    return str(json.dumps(payload))


def _create_temp(dev_name, manufacturer, model, uid):
    payload = {**_create_device(manufacturer, model, dev_name, uid)}
    payload["name"] = dev_name + " Temperature"
    payload["device_class"] = "temperature"
    payload["force_update"] = "true"
    return payload


def _create_temp_f(dev_name, manufacturer, model, uid):
    payload = _create_temp(dev_name, manufacturer, model, uid)
    payload["unit_of_measurement"] = "°F"
    payload["value_template"] = "{{value|float|round(1)}}"
    payload["unique_id"] = f"{_lstr(manufacturer)}_{_lstr(model)}_{_mstr(uid)}_temp_f"
    payload["state_topic"] = f"{prefix}/{manufacturer}/{uid}/temperature_F"
    return str(json.dumps(payload))


def _create_temp_c(dev_name, manufacturer, model, uid):
    payload = _create_temp(dev_name, manufacturer, model, uid)
    payload["unit_of_measurement"] = "°C"
    payload["value_template"] = "{{value|float|round(1)}}"
    payload["unique_id"] = f"{_lstr(manufacturer)}_{_lstr(model)}_{_mstr(uid)}_temp_c"
    payload["state_topic"] = f"{prefix}/{manufacturer}/{uid}/temperature_C"
    return str(json.dumps(payload))


def _create_temp_c_to_f(dev_name, manufacturer, model, uid):
    payload = _create_temp(dev_name, manufacturer, model, uid)
    payload["unit_of_measurement"] = "°F"
    payload["value_template"] = "{{(value|float * 1.8 + 32)|round(1)}}"
    payload["unique_id"] = f"{_lstr(manufacturer)}_{_lstr(model)}_{_mstr(uid)}_temp_c"
    payload["state_topic"] = f"{prefix}/{manufacturer}/{uid}/temperature_C"
    return str(json.dumps(payload))


def _create_temp_f_to_c(dev_name, manufacturer, model, uid):
    payload = _create_temp(dev_name, manufacturer, model, uid)
    payload["unit_of_measurement"] = "°C"
    payload["value_template"] = "{{((value|float - 32) * (5/9))|round(1)}}"
    payload["unique_id"] = f"{_lstr(manufacturer)}_{_lstr(model)}_{_mstr(uid)}_temp_c"
    payload["state_topic"] = f"{prefix}/{manufacturer}/{uid}/temperature_C"
    return str(json.dumps(payload))


def create_motion(manu: str, model: str, uid: str, nm: str) -> List[Tuple]:

    msgs = []
    # Create battery:
    payload = _create_battery(manufacturer=manu, model=model, dev_name=nm, uid=uid)
    topic = f"{disc}/sensor/{_mstr(manu)}_{_mstr(model)}_{_mstr(uid)}/battery/config"
    msgs.append((topic, payload, 2, True))

    # Create tamper:
    payload = _create_tamper(manufacturer=manu, model=model, dev_name=nm, uid=uid)
    topic = f"{disc}/binary_sensor/{_mstr(manu)}_{_mstr(model)}_{_mstr(uid)}/tamper/config"
    msgs.append((topic, payload, 2, True))

    # Create time:
    payload = _create_time(manufacturer=manu, model=model, dev_name=nm, uid=uid)
    topic = f"{disc}/sensor/{_mstr(manu)}_{_mstr(model)}_{_mstr(uid)}/time/config"
    msgs.append((topic, payload, 2, True))

    # Create event:
    payload = _create_motion_event(manufacturer=manu, model=model, dev_name=nm, uid=uid)
    topic = f"{disc}/binary_sensor/{_mstr(manu)}_{_mstr(model)}_{_mstr(uid)}/event/config"
    msgs.append((topic, payload, 2, True))
    return msgs


def create_contact(manu: str, model: str, uid: str, nm: str) -> List[Tuple]:

    msgs = []
    # Create battery:
    payload = _create_battery(manufacturer=manu, model=model, dev_name=nm, uid=uid)
    topic = f"{disc}/sensor/{_mstr(manu)}_{_mstr(model)}_{_mstr(uid)}/battery/config"
    msgs.append((topic, payload, 2, True))

    # Create tamper:
    payload = _create_tamper(manufacturer=manu, model=model, dev_name=nm, uid=uid)
    topic = f"{disc}/binary_sensor/{_mstr(manu)}_{_mstr(model)}_{_mstr(uid)}/tamper/config"
    msgs.append((topic, payload, 2, True))

    # Create time:
    payload = _create_time(manufacturer=manu, model=model, dev_name=nm, uid=uid)
    topic = f"{disc}/sensor/{_mstr(manu)}_{_mstr(model)}_{_mstr(uid)}/time/config"
    msgs.append((topic, payload, 2, True))

    # Create closed:
    payload = _create_contact(manufacturer=manu, model=model, dev_name=nm, uid=uid)
    topic = f"{disc}/binary_sensor/{_mstr(manu)}_{_mstr(model)}_{_mstr(uid)}/door/config"
    msgs.append((topic, payload, 2, True))
    return msgs


def create_contact_sensor2(manu: str, model: str, uid: str, nm: str) -> List[Tuple]:

    msgs = []
    # # Create battery:
    # payload = create_battery(manufacturer=manu, model=model, dev_name=nm, uid=uid)
    # topic = f"{disc}/sensor/{mstr(manu)}_{mstr(model)}_{mstr(uid)}/battery/config"
    # msgs.append((topic, payload, 2, True))

    # # Create tamper:
    # payload = create_tamper(manufacturer=manu, model=model, dev_name=nm, uid=uid)
    # topic = (
    #     f"{disc}/binary_sensor/{mstr(manu)}_{mstr(model)}_{mstr(uid)}/tamper/config"
    # )
    # msgs.append((topic, payload, 2, True))

    # Create time:
    payload = _create_time(manufacturer=manu, model=model, dev_name=nm, uid=uid)
    topic = f"{disc}/sensor/{_mstr(manu)}_{_mstr(model)}_{_mstr(uid)}/time/config"
    msgs.append((topic, payload, 2, True))

    # Create closed:
    payload = _create_contact2(manufacturer=manu, model=model, dev_name=nm, uid=uid)
    topic = f"{disc}/binary_sensor/{_mstr(manu)}_{_mstr(model)}_{_mstr(uid)}/door/config"
    msgs.append((topic, payload, 2, True))
    return msgs


def create_glassbreak(manu: str, model: str, uid: str, nm: str):

    msgs = []
    # Create battery:
    payload = _create_battery(manufacturer=manu, model=model, dev_name=nm, uid=uid)
    topic = f"{disc}/sensor/{_mstr(manu)}_{_mstr(model)}_{_mstr(uid)}/battery/config"
    msgs.append((topic, payload, 2, True))

    # Create tamper:
    payload = _create_tamper(manufacturer=manu, model=model, dev_name=nm, uid=uid)
    topic = f"{disc}/binary_sensor/{_mstr(manu)}_{_mstr(model)}_{_mstr(uid)}/tamper/config"
    msgs.append((topic, payload, 2, True))

    # Create time:
    payload = _create_time(manufacturer=manu, model=model, dev_name=nm, uid=uid)
    topic = f"{disc}/sensor/{_mstr(manu)}_{_mstr(model)}_{_mstr(uid)}/time/config"
    msgs.append((topic, payload, 2, True))

    # Create event:
    payload = _create_glassbreak_event(manufacturer=manu, model=model, dev_name=nm, uid=uid)
    topic = f"{disc}/binary_sensor/{_mstr(manu)}_{_mstr(model)}_{_mstr(uid)}/event/config"
    msgs.append((topic, payload, 2, True))
    return msgs


def create_temp_hum_f(manu: str, model: str, channel: str, id: str, nm: str) -> List[Tuple]:

    uid = channel + "/" + id
    msgs = []
    # Create battery:
    payload = _create_battery(manufacturer=manu, model=model, dev_name=nm, uid=uid)
    topic = f"{disc}/sensor/{_mstr(manu)}_{_mstr(model)}_{_mstr(uid)}/battery/config"
    msgs.append((topic, payload, 2, True))

    # Create temp:
    payload = _create_temp_f(manufacturer=manu, model=model, dev_name=nm, channel=channel, uid=uid)
    topic = f"{disc}/sensor/{_mstr(manu)}_{_mstr(model)}_{_mstr(uid)}/temp/config"
    msgs.append((topic, payload, 2, True))

    # Create time:
    payload = _create_time(manufacturer=manu, model=model, dev_name=nm, uid=uid)
    topic = f"{disc}/sensor/{_mstr(manu)}_{_mstr(model)}_{_mstr(uid)}/time/config"
    msgs.append((topic, payload, 2, True))

    # Create humidity:
    payload = _create_humidity(manufacturer=manu, model=model, dev_name=nm, uid=uid)
    topic = f"{disc}/sensor/{_mstr(manu)}_{_mstr(model)}_{_mstr(uid)}/humidity/config"
    msgs.append((topic, payload, 2, True))
    return msgs


def create_temp_hum_c(manu: str, model: str, channel: str, id: str, nm: str) -> List[Tuple]:

    uid = channel + "/" + id
    msgs = []
    # Create battery:
    payload = _create_battery(manufacturer=manu, model=model, dev_name=nm, uid=uid)
    topic = f"{disc}/sensor/{_mstr(manu)}_{_mstr(model)}_{_mstr(uid)}/battery/config"
    msgs.append((topic, payload, 2, True))

    # Create temp:
    payload = _create_temp_c(manufacturer=manu, model=model, dev_name=nm, uid=uid)
    topic = f"{disc}/sensor/{_mstr(manu)}_{_mstr(model)}_{_mstr(uid)}/temp/config"
    msgs.append((topic, payload, 2, True))

    # Create time:
    payload = _create_time(manufacturer=manu, model=model, dev_name=nm, uid=uid)
    topic = f"{disc}/sensor/{_mstr(manu)}_{_mstr(model)}_{_mstr(uid)}/time/config"
    msgs.append((topic, payload, 2, True))

    # Create humidity:
    payload = _create_humidity(manufacturer=manu, model=model, dev_name=nm, uid=uid)
    topic = f"{disc}/sensor/{_mstr(manu)}_{_mstr(model)}_{_mstr(uid)}/humidity/config"
    msgs.append((topic, payload, 2, True))
    return msgs


def create_temp_hum_f_to_c(manu: str, model: str, channel: str, id: str, nm: str) -> List[Tuple]:

    uid = channel + "/" + id
    msgs = []
    # Create battery:
    payload = _create_battery(manufacturer=manu, model=model, dev_name=nm, uid=uid)
    topic = f"{disc}/sensor/{_mstr(manu)}_{_mstr(model)}_{_mstr(uid)}/battery/config"
    msgs.append((topic, payload, 2, True))

    # Create temp:
    payload = _create_temp_f_to_c(manufacturer=manu, model=model, dev_name=nm, uid=uid)
    topic = f"{disc}/sensor/{_mstr(manu)}_{_mstr(model)}_{_mstr(uid)}/temp/config"
    msgs.append((topic, payload, 2, True))

    # Create time:
    payload = _create_time(manufacturer=manu, model=model, dev_name=nm, uid=uid)
    topic = f"{disc}/sensor/{_mstr(manu)}_{_mstr(model)}_{_mstr(uid)}/time/config"
    msgs.append((topic, payload, 2, True))

    # Create humidity:
    payload = _create_humidity(manufacturer=manu, model=model, dev_name=nm, uid=uid)
    topic = f"{disc}/sensor/{_mstr(manu)}_{_mstr(model)}_{_mstr(uid)}/humidity/config"
    msgs.append((topic, payload, 2, True))
    return msgs


def create_temp_hum_c_to_f(manu: str, model: str, channel: str, id: str, nm: str) -> List[Tuple]:

    uid = channel + "/" + id
    msgs = []
    # Create battery:
    payload = _create_battery(manufacturer=manu, model=model, dev_name=nm, uid=uid)
    topic = f"{disc}/sensor/{_mstr(manu)}_{_mstr(model)}_{_mstr(uid)}/battery/config"
    msgs.append((topic, payload, 2, True))

    # Create temp:
    payload = _create_temp_c_to_f(manufacturer=manu, model=model, dev_name=nm, uid=uid)
    topic = f"{disc}/sensor/{_mstr(manu)}_{_mstr(model)}_{_mstr(uid)}/temp/config"
    msgs.append((topic, payload, 2, True))

    # Create time:
    payload = _create_time(manufacturer=manu, model=model, dev_name=nm, uid=uid)
    topic = f"{disc}/sensor/{_mstr(manu)}_{_mstr(model)}_{_mstr(uid)}/time/config"
    msgs.append((topic, payload, 2, True))

    # Create humidity:
    payload = _create_humidity(manufacturer=manu, model=model, dev_name=nm, uid=uid)
    topic = f"{disc}/sensor/{_mstr(manu)}_{_mstr(model)}_{_mstr(uid)}/humidity/config"
    msgs.append((topic, payload, 2, True))
    return msgs


def create_sonoff_remote(manu: str, model: str, uid: str, nm: str) -> List[Tuple]:

    disco_prefix = f"{disc}/device_automation/{_mstr(manu)}_{_mstr(model)}_{_mstr(uid)}"
    msgs = []
    # Create time:
    payload = _create_time(manufacturer=manu, model=model, dev_name=nm, uid=uid)
    topic = f"{disc}/sensor/{_mstr(manu)}_{_mstr(model)}_{_mstr(uid)}/time/config"
    msgs.append((topic, payload, 2, True))

    # Create button a short press:
    payload = _create_button(
        nm,
        manu,
        model,
        uid,
        "button_short_press",
        "Button A",
        "A",
    )
    topic = disco_prefix + "/button_a/config"
    msgs.append((topic, payload, 2, True))

    # Create button b short press:
    payload = _create_button(
        nm,
        manu,
        model,
        uid,
        "button_short_press",
        "Button B",
        "B",
    )
    topic = disco_prefix + "/button_b/config"
    msgs.append((topic, payload, 2, True))

    # Create button c short press:
    payload = _create_button(
        nm,
        manu,
        model,
        uid,
        "button_short_press",
        "Button C",
        "C",
    )
    topic = disco_prefix + "/button_c/config"
    msgs.append((topic, payload, 2, True))

    # Create button d short press:
    payload = _create_button(
        nm,
        manu,
        model,
        uid,
        "button_short_press",
        "Button D",
        "D",
    )
    topic = disco_prefix + "/button_d/config"
    msgs.append((topic, payload, 2, True))

    # Create button e short press:
    payload = _create_button(
        nm,
        manu,
        model,
        uid,
        "button_short_press",
        "Button E",
        "E",
    )
    topic = disco_prefix + "/button_e/config"
    msgs.append((topic, payload, 2, True))

    # Create button f short press:
    payload = _create_button(
        nm,
        manu,
        model,
        uid,
        "button_short_press",
        "Button F",
        "F",
    )
    topic = disco_prefix + "/button_f/config"
    msgs.append((topic, payload, 2, True))

    # Create button g short press:
    payload = _create_button(
        nm,
        manu,
        model,
        uid,
        "button_short_press",
        "Button G",
        "G",
    )
    topic = disco_prefix + "/button_g/config"
    msgs.append((topic, payload, 2, True))

    # Create button h short press:
    payload = _create_button(
        nm,
        manu,
        model,
        uid,
        "button_short_press",
        "Button H",
        "H",
    )
    topic = disco_prefix + "/button_h/config"
    msgs.append((topic, payload, 2, True))
    return msgs


if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG, format="%(message)s")
    _LOGGER.info("Starting Rattler MQTT Device Creator...")
    create_devices()
