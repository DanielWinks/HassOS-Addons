"""Configuration for Pwrstat API."""



MQTT_CONFIG = vol.Schema(
    {
        vol.Optional("broker", default="192.168.1.100"): str,
        vol.Optional("port", default=1883): vol.All(
            int, vol.Range(min=1025, max=65535)
        ),
        vol.Optional("client_id", default="pwrstat_mqtt"): str,
        vol.Optional("topic", default="sensors/basement/power/ups"): str,
        vol.Optional("refresh", default=30): int,
        vol.Optional("qos", default=0): int,
        vol.Optional("retained", default=True): bool,
        vol.Optional("username"): str,
        vol.Optional("password"): str,
    }
)