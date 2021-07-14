#!/usr/local/bin/python3
"""Get device config from Home Assistant Add-On configuration options and create devices in Home Assistant"""
import json
import logging
import sys
from typing import Any, Dict, List

import paho.mqtt.client as mqtt
from ruamel.yaml import YAML as yaml
from ruamel.yaml import YAMLError

_LOGGER = logging.getLogger("Main")
handler = logging.StreamHandler(sys.stdout)
handler.setLevel(logging.DEBUG)
formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
handler.setFormatter(formatter)
_LOGGER.addHandler(handler)

_CLIENT = mqtt.Client()
YAML = yaml(typ="safe")


class DeviceCreator:
    """Create MQTT Devices in Home Assistant for rtl_433."""

    def __init__(self) -> None:
        """Initialize DeviceCreator class."""
        self._devices = None
        self._ha_disc = None
        self._mqtt_client_id = "rattler_mqtt_creator"
        self._mqtt_config = None
        self._mqtt_host = None
        self._mqtt_port = None
        self._mqtt_qos = 2
        self._mqtt_retain = True
        _LOGGER.info("MQTT Device Creator Initialized.")

    def create_devices(self) -> None:

        with open("/data/devices.yaml") as file:
            try:
                yaml_config: Dict[str, Any] = YAML.load(file)
            except YAMLError as ex:
                _LOGGER.log(level=logging.ERROR, msg=ex)

        self._mqtt_config: Dict[str, Any] = yaml_config["mqtt"]
        self._ha_disc: str = self._mqtt_config["ha_discovery_topic"]
        self._mqtt_host: str = self._mqtt_config["host"]
        self._mqtt_port: int = self._mqtt_config["port"]
        self._mqtt_qos: int = self._mqtt_config["qos"]
        self._mqtt_retain: bool = self._mqtt_config["retained"]
        self._mqtt_client_id: str = self._mqtt_config.get("client_id")
        _CLIENT.reinitialise(client_id=self._mqtt_client_id)
        username = self._mqtt_config.get("username")
        password = self._mqtt_config.get("password")
        if None not in (username, password):
            _CLIENT.username_pw_set(username=username, password=password)

        if not _CLIENT.is_connected():
            _CLIENT.connect(host=self._mqtt_host, port=self._mqtt_port, keepalive=60)

        self._devices: List[Dict] = yaml_config["devices"]
        for device in self._devices:
            if device["type"] == "motion":
                entities = yaml_config["mqtt_creator"]["motion"]
                create_motion_sensor(entities, self._ha_disc, _CLIENT)
            if device["type"] == "contact":
                entities = yaml_config["mqtt_creator"]["contact"]
                create_contact_sensor(entities, self._ha_disc, _CLIENT)
            if device["type"] == "glassbreak":
                entities = yaml_config["mqtt_creator"]["glassbreak"]
                create_glassbreak_sensor(entities, self._ha_disc, _CLIENT)
            if device["type"] == "temp_f_hum":
                entities = yaml_config["mqtt_creator"]["temp_f_hum"]
                create_temp_hum_f_sensor(entities, self._ha_disc, _CLIENT)
            if device["type"] == "temp_c_hum":
                entities = yaml_config["mqtt_creator"]["temp_c_hum"]
                create_temp_hum_c_sensor(entities, self._ha_disc, _CLIENT)
            if device["type"] == "sonoff_remote":
                entities = yaml_config["mqtt_creator"]["sonoff_remote"]
                create_temp_hum_c_sensor(entities, self._ha_disc, _CLIENT)


def mstr(string):
    return string.lower().replace("-", "_").replace(" ", "_").replace("/", "_")


def _create_device(manufacturer, model, dev_name, uid):
    id = {
        "identifiers": [
            f"{manufacturer.lower().replace('-','_')}_{model.lower().replace('-','_')}_{uid.replace('/','_')}"
        ]
    }
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
    payload[
        "unique_id"
    ] = f"{manufacturer.lower().replace('-','_')}_{model.lower().replace('-','_')}_{uid.replace('/','_')}_battery"
    payload["state_topic"] = f"rtl_433/{manufacturer}/{uid}/battery_ok"
    return str(json.dumps(payload))


def _create_button(dev_name, manufacturer, model, uid, type, subtype, button_payload):
    payload = {**_create_device(manufacturer, model, dev_name, uid)}
    payload["type"] = f"{type}"
    payload["subtype"] = f"{subtype}"
    payload["payload"] = f"{button_payload}"
    payload["topic"] = f"rtl_433/{manufacturer}/{uid}/button"
    payload["automation_type"] = "trigger"
    return str(json.dumps(payload))


def _create_tamper(dev_name, manufacturer, model, uid):
    payload = {**_create_device(manufacturer, model, dev_name, uid)}
    payload["name"] = dev_name + " Tamper"
    payload["device_class"] = "problem"
    payload["payload_on"] = 1
    payload["payload_off"] = 0
    payload["force_update"] = "true"
    payload[
        "unique_id"
    ] = f"{manufacturer.lower().replace('-','_')}_{model.lower().replace('-','_')}_{uid.replace('/','_')}_tamper"
    payload["state_topic"] = f"rtl_433/{manufacturer}/{uid}/tamper"
    return str(json.dumps(payload))


def _create_time(dev_name, manufacturer, model, uid):
    payload = {**_create_device(manufacturer, model, dev_name, uid)}
    payload["name"] = dev_name + " Time"
    payload["device_class"] = "timestamp"
    payload[
        "unique_id"
    ] = f"{manufacturer.lower().replace('-','_')}_{model.lower().replace('-','_')}_{uid.replace('/','_')}_time"
    payload["state_topic"] = f"rtl_433/{manufacturer}/{uid}/time"
    return str(json.dumps(payload))


def _create_motion_event(dev_name, manufacturer, model, uid):
    payload = {**_create_device(manufacturer, model, dev_name, uid)}
    payload["name"] = dev_name + " Event"
    payload["device_class"] = "motion"
    payload["payload_on"] = 1
    payload["payload_off"] = 0
    payload["off_delay"] = 15
    payload[
        "unique_id"
    ] = f"{manufacturer.lower().replace('-','_')}_{model.lower().replace('-','_')}_{uid.replace('/','_')}_event"
    payload["state_topic"] = f"rtl_433/{manufacturer}/{uid}/event"
    return str(json.dumps(payload))


def _create_contact(dev_name, manufacturer, model, uid):
    payload = {**_create_device(manufacturer, model, dev_name, uid)}
    payload["name"] = dev_name + " Contact"
    payload["device_class"] = "door"
    payload["payload_on"] = 0
    payload["payload_off"] = 1
    payload[
        "unique_id"
    ] = f"{manufacturer.lower().replace('-','_')}_{model.lower().replace('-','_')}_{uid.replace('/','_')}_closed"
    payload["state_topic"] = f"rtl_433/{manufacturer}/{uid}/closed"
    return str(json.dumps(payload))


def _create_contact2(dev_name, manufacturer, model, uid):
    payload = {**_create_device(manufacturer, model, dev_name, uid)}
    payload["name"] = dev_name + " Contact"
    payload["device_class"] = "door"
    payload["payload_on"] = 1
    payload["payload_off"] = 0
    payload[
        "unique_id"
    ] = f"{manufacturer.lower().replace('-','_')}_{model.lower().replace('-','_')}_{uid.replace('/','_')}_opened"
    payload["state_topic"] = f"rtl_433/{manufacturer}/{uid}/opened"
    return str(json.dumps(payload))


def _create_glassbreak_event(dev_name, manufacturer, model, uid):
    payload = {**_create_device(manufacturer, model, dev_name, uid)}
    payload["name"] = dev_name + " Event"
    payload["device_class"] = "sound"
    payload["payload_on"] = 1
    payload["payload_off"] = 0
    payload["off_delay"] = 1
    payload[
        "unique_id"
    ] = f"{manufacturer.lower().replace('-','_')}_{model.lower().replace('-','_')}_{uid.replace('/','_')}_event"
    payload["state_topic"] = f"rtl_433/{manufacturer}/{uid}/event"
    return str(json.dumps(payload))


def _create_humidity(dev_name, manufacturer, model, uid):
    payload = {**_create_device(manufacturer, model, dev_name, uid)}
    payload["name"] = dev_name + " Humidity"
    payload["device_class"] = "humidity"
    payload["force_update"] = "true"
    payload["unit_of_measurement"] = "%"
    payload["value_template"] = "{{value|int}}"
    payload[
        "unique_id"
    ] = f"{manufacturer.lower().replace('-','_')}_{model.lower().replace('-','_')}_{uid.replace('/','_')}_humidity"
    payload["state_topic"] = f"rtl_433/{manufacturer}/{uid}/humidity"
    return str(json.dumps(payload))


def _create_temp_f(dev_name, manufacturer, model, uid):
    payload = {**_create_device(manufacturer, model, dev_name, uid)}
    payload["name"] = dev_name + " Temperature"
    payload["device_class"] = "temperature"
    payload["force_update"] = "true"
    payload["unit_of_measurement"] = "°F"
    payload["value_template"] = "{{value|float|round(1)}}"
    payload[
        "unique_id"
    ] = f"{manufacturer.lower().replace('-','_')}_{model.lower().replace('-','_')}_{uid.replace('/','_')}_temp_f"
    payload["state_topic"] = f"rtl_433/{manufacturer}/{uid}/temperature_F"
    return str(json.dumps(payload))


def _create_temp_c(dev_name, manufacturer, model, uid):
    payload = {**_create_device(manufacturer, model, dev_name, uid)}
    payload["name"] = dev_name + " Temperature"
    payload["device_class"] = "temperature"
    payload["force_update"] = "true"
    payload["unit_of_measurement"] = "°F"
    payload["value_template"] = "{{(value|int * 1.8 + 32)|round(0)}}"
    payload[
        "unique_id"
    ] = f"{manufacturer.lower().replace('-','_')}_{model.lower().replace('-','_')}_{uid.replace('/','_')}_temp_f"
    payload["state_topic"] = f"rtl_433/{manufacturer}/{uid}/temperature_C"
    return str(json.dumps(payload))


def create_motion_sensor(entities: List, disc: str, mqtt_client: _CLIENT):
    for entity in entities:
        manu = entity["manufacturer"]
        model = entity["model"]
        uid = entity["uid"]
        nm = entity["name"]

        # Create battery:
        payload = _create_battery(manufacturer=manu, model=model, dev_name=nm, uid=uid)
        topic = f"{disc}/sensor/{mstr(manu)}_{mstr(model)}_{mstr(uid)}/battery/config"
        mqtt_client.publish(topic=topic, payload=payload, qos=2, retain=True)

        # Create tamper:
        payload = _create_tamper(manufacturer=manu, model=model, dev_name=nm, uid=uid)
        topic = (
            f"{disc}/binary_sensor/{mstr(manu)}_{mstr(model)}_{mstr(uid)}/tamper/config"
        )
        mqtt_client.publish(topic=topic, payload=payload, qos=2, retain=True)

        # Create time:
        payload = _create_time(manufacturer=manu, model=model, dev_name=nm, uid=uid)
        topic = f"{disc}/sensor/{mstr(manu)}_{mstr(model)}_{mstr(uid)}/time/config"
        mqtt_client.publish(topic=topic, payload=payload, qos=2, retain=True)

        # Create event:
        payload = _create_motion_event(
            manufacturer=manu, model=model, dev_name=nm, uid=uid
        )
        topic = (
            f"{disc}/binary_sensor/{mstr(manu)}_{mstr(model)}_{mstr(uid)}/event/config"
        )
        mqtt_client.publish(topic=topic, payload=payload, qos=2, retain=True)


def create_contact_sensor(entities: List, disc: str, mqtt_client: _CLIENT):
    for entity in entities:
        manu = entity["manufacturer"]
        model = entity["model"]
        uid = entity["uid"]
        nm = entity["name"]

        # Create battery:
        payload = _create_battery(manufacturer=manu, model=model, dev_name=nm, uid=uid)
        topic = f"{disc}/sensor/{mstr(manu)}_{mstr(model)}_{mstr(uid)}/battery/config"
        mqtt_client.publish(topic=topic, payload=payload, qos=2, retain=True)

        # Create tamper:
        payload = _create_tamper(manufacturer=manu, model=model, dev_name=nm, uid=uid)
        topic = (
            f"{disc}/binary_sensor/{mstr(manu)}_{mstr(model)}_{mstr(uid)}/tamper/config"
        )
        mqtt_client.publish(topic=topic, payload=payload, qos=2, retain=True)

        # Create time:
        payload = _create_time(manufacturer=manu, model=model, dev_name=nm, uid=uid)
        topic = f"{disc}/sensor/{mstr(manu)}_{mstr(model)}_{mstr(uid)}/time/config"
        mqtt_client.publish(topic=topic, payload=payload, qos=2, retain=True)

        # Create closed:
        payload = _create_contact(manufacturer=manu, model=model, dev_name=nm, uid=uid)
        topic = (
            f"{disc}/binary_sensor/{mstr(manu)}_{mstr(model)}_{mstr(uid)}/door/config"
        )
        mqtt_client.publish(topic=topic, payload=payload, qos=2, retain=True)


def create_contact_sensor2(entities: List, disc: str, mqtt_client: _CLIENT):
    for entity in entities:
        manu = entity["manufacturer"]
        model = entity["model"]
        uid = entity["uid"]
        nm = entity["name"]

        # # Create battery:
        # payload = create_battery(manufacturer=manu, model=model, dev_name=nm, uid=uid)
        # topic = f"{disc}/sensor/{mstr(manu)}_{mstr(model)}_{mstr(uid)}/battery/config"
        # mqtt.publish(topic=topic, payload=payload, qos=2, retain=True)

        # # Create tamper:
        # payload = create_tamper(manufacturer=manu, model=model, dev_name=nm, uid=uid)
        # topic = (
        #     f"{disc}/binary_sensor/{mstr(manu)}_{mstr(model)}_{mstr(uid)}/tamper/config"
        # )
        # mqtt.publish(topic=topic, payload=payload, qos=2, retain=True)

        # Create time:
        payload = _create_time(manufacturer=manu, model=model, dev_name=nm, uid=uid)
        topic = f"{disc}/sensor/{mstr(manu)}_{mstr(model)}_{mstr(uid)}/time/config"
        mqtt_client.publish(topic=topic, payload=payload, qos=2, retain=True)

        # Create closed:
        payload = _create_contact2(manufacturer=manu, model=model, dev_name=nm, uid=uid)
        topic = (
            f"{disc}/binary_sensor/{mstr(manu)}_{mstr(model)}_{mstr(uid)}/door/config"
        )
        mqtt_client.publish(topic=topic, payload=payload, qos=2, retain=True)


def create_glassbreak_sensor(entities: List, disc: str, mqtt_client: _CLIENT):
    for entity in entities:
        manu = entity["manufacturer"]
        model = entity["model"]
        uid = entity["uid"]
        nm = entity["name"]

        # Create battery:
        payload = _create_battery(manufacturer=manu, model=model, dev_name=nm, uid=uid)
        topic = f"{disc}/sensor/{mstr(manu)}_{mstr(model)}_{mstr(uid)}/battery/config"
        mqtt_client.publish(topic=topic, payload=payload, qos=2, retain=True)

        # Create tamper:
        payload = _create_tamper(manufacturer=manu, model=model, dev_name=nm, uid=uid)
        topic = (
            f"{disc}/binary_sensor/{mstr(manu)}_{mstr(model)}_{mstr(uid)}/tamper/config"
        )
        mqtt_client.publish(topic=topic, payload=payload, qos=2, retain=True)

        # Create time:
        payload = _create_time(manufacturer=manu, model=model, dev_name=nm, uid=uid)
        topic = f"{disc}/sensor/{mstr(manu)}_{mstr(model)}_{mstr(uid)}/time/config"
        mqtt_client.publish(topic=topic, payload=payload, qos=2, retain=True)

        # Create event:
        payload = _create_glassbreak_event(
            manufacturer=manu, model=model, dev_name=nm, uid=uid
        )
        topic = (
            f"{disc}/binary_sensor/{mstr(manu)}_{mstr(model)}_{mstr(uid)}/event/config"
        )
        mqtt_client.publish(topic=topic, payload=payload, qos=2, retain=True)


def create_temp_hum_f_sensor(entities: List, disc: str, mqtt_client: _CLIENT):
    for entity in entities:
        manu = entity["manufacturer"]
        model = entity["model"]
        channel = entity["channel"]
        id = entity["id"]
        uid = channel + "/" + id
        nm = entity["name"]

        # Create battery:
        payload = _create_battery(manufacturer=manu, model=model, dev_name=nm, uid=uid)
        topic = f"{disc}/sensor/{mstr(manu)}_{mstr(model)}_{mstr(uid)}/battery/config"
        mqtt_client.publish(topic=topic, payload=payload, qos=2, retain=True)

        # Create temp:
        payload = _create_temp_f(
            manufacturer=manu, model=model, dev_name=nm, channel=channel, uid=uid
        )
        topic = f"{disc}/sensor/{mstr(manu)}_{mstr(model)}_{mstr(uid)}/temp/config"
        mqtt_client.publish(topic=topic, payload=payload, qos=2, retain=True)

        # Create time:
        payload = _create_time(manufacturer=manu, model=model, dev_name=nm, uid=uid)
        topic = f"{disc}/sensor/{mstr(manu)}_{mstr(model)}_{mstr(uid)}/time/config"
        mqtt_client.publish(topic=topic, payload=payload, qos=2, retain=True)

        # Create humidity:
        payload = _create_humidity(manufacturer=manu, model=model, dev_name=nm, uid=uid)
        topic = f"{disc}/sensor/{mstr(manu)}_{mstr(model)}_{mstr(uid)}/humidity/config"
        mqtt_client.publish(topic=topic, payload=payload, qos=2, retain=True)


def create_temp_hum_c_sensor(entities: List, disc: str, mqtt_client: _CLIENT):
    for entity in entities:
        manu = entity["manufacturer"]
        model = entity["model"]
        channel = entity["channel"]
        id = entity["id"]
        uid = channel + "/" + id
        nm = entity["name"]

        # Create battery:
        payload = _create_battery(manufacturer=manu, model=model, dev_name=nm, uid=uid)
        topic = f"{disc}/sensor/{mstr(manu)}_{mstr(model)}_{mstr(uid)}/battery/config"
        mqtt_client.publish(topic=topic, payload=payload, qos=2, retain=True)

        # Create temp:
        payload = _create_temp_c(manufacturer=manu, model=model, dev_name=nm, uid=uid)
        topic = f"{disc}/sensor/{mstr(manu)}_{mstr(model)}_{mstr(uid)}/temp/config"
        mqtt_client.publish(topic=topic, payload=payload, qos=2, retain=True)

        # Create time:
        payload = _create_time(manufacturer=manu, model=model, dev_name=nm, uid=uid)
        topic = f"{disc}/sensor/{mstr(manu)}_{mstr(model)}_{mstr(uid)}/time/config"
        mqtt_client.publish(topic=topic, payload=payload, qos=2, retain=True)

        # Create humidity:
        payload = _create_humidity(manufacturer=manu, model=model, dev_name=nm, uid=uid)
        topic = f"{disc}/sensor/{mstr(manu)}_{mstr(model)}_{mstr(uid)}/humidity/config"
        mqtt_client.publish(topic=topic, payload=payload, qos=2, retain=True)


def create_sonoff_remote(entities: List, disc: str, mqtt_client: _CLIENT):
    for entity in entities:
        manu = entity["manufacturer"]
        model = entity["model"]
        uid = entity["uid"]
        nm = entity["name"]
        disco_prefix = (
            f"{disc}/device_automation/{mstr(manu)}_{mstr(model)}_{mstr(uid)}"
        )

        # Create time:
        payload = _create_time(manufacturer=manu, model=model, dev_name=nm, uid=uid)
        topic = f"{disc}/sensor/{mstr(manu)}_{mstr(model)}_{mstr(uid)}/time/config"
        mqtt_client.publish(topic=topic, payload=payload, qos=2, retain=True)

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
        mqtt_client.publish(topic=topic, payload=payload, qos=2, retain=True)

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
        mqtt_client.publish(topic=topic, payload=payload, qos=2, retain=True)

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
        mqtt_client.publish(topic=topic, payload=payload, qos=2, retain=True)

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
        mqtt_client.publish(topic=topic, payload=payload, qos=2, retain=True)

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
        mqtt_client.publish(topic=topic, payload=payload, qos=2, retain=True)

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
        mqtt_client.publish(topic=topic, payload=payload, qos=2, retain=True)

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
        mqtt_client.publish(topic=topic, payload=payload, qos=2, retain=True)

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
        mqtt_client.publish(topic=topic, payload=payload, qos=2, retain=True)


if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG, format="%(message)s")
    _LOGGER.info("Starting Rattler MQTT Device Creator...")
    dc = DeviceCreator()
    dc.create_devices()
