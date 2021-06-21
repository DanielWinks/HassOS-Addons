import argparse
from typing import Any, Dict

_parser = argparse.ArgumentParser()

_parser.add_argument("-pl", "--pwrstat_api_log_level", help="Pwrstat API Logging Level")

_parser.add_argument("-mb", "--mqtt_broker", help="MQTT Broker IP Address/DNS Name")
_parser.add_argument("-mp", "--mqtt_port", help="MQTT Port")
_parser.add_argument("-mc", "--mqtt_clientid", help="MQTT Client ID")
_parser.add_argument("-mt", "--mqtt_topic", help="MQTT Topic")
_parser.add_argument("-mf", "--mqtt_refresh", help="MQTT Refresh Interval (seconds)")
_parser.add_argument("-mq", "--mqtt_qos", help="MQTT QOS")
_parser.add_argument("-mr", "--mqtt_retained", help="MQTT Retained Flag")
_parser.add_argument("-mu", "--mqtt_username", help="MQTT Username")
_parser.add_argument("-mw", "--mqtt_password", help="MQTT Password")

_parser.add_argument("-rp", "--rest_port", help="REST Endpoint Port")
_parser.add_argument("-rb", "--rest_bind_address", help="REST Bind Address")

_parser.add_argument("-pp", "--prom_port", help="Prometheus Port")
_parser.add_argument("-pb", "--prom_bind_address", help="Prometheus Bind Address")
_parser.add_argument("-pl", "--prom_labels", help="Prometheus Labels")

_args = vars(_parser.parse_args())

_pwrstat_api_config: Dict[str, Any] = {}
_mqtt_config: Dict[str, Any] = {}
_rest_config: Dict[str, str] = {}
_prometheus_config: Dict[str, Any] = {}

_pwrstat_api_config["log_level"] = _args["pwrstat_api_log_level"]

_mqtt_config["broker"] = _args["mqtt_broker"]
_mqtt_config["port"] = int(_args["mqtt_port"])
_mqtt_config["client_id"] = _args["mqtt_clientid"]
_mqtt_config["topic"] = _args["mqtt_topic"]
_mqtt_config["refresh"] = int(_args["mqtt_refresh"])
_mqtt_config["qos"] = int(_args["mqtt_qos"])
_mqtt_config["retained"] = _args["mqtt_retained"]
_mqtt_config["username"] = _args["mqtt_username"]
_mqtt_config["password"] = _args["mqtt_password"]

_rest_config["port"] = int(_args["rest_port"])
_rest_config["bind_address"] = _args["rest_bind_address"]

_prometheus_config["port"] = int(_args["prom_port"])
_prometheus_config["bind_address"] = _args["prom_bind_address"]
_prometheus_config["labels"] = _args["prom_labels"]

config: Dict[str, Any]= {}
config["pwrstat_api"] = _pwrstat_api_config
config["mqtt"] = _mqtt_config
config["rest"] = _rest_config
config["prometheus"] = _prometheus_config
