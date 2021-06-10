# PowerPanel (pwrstat) API & MQTT container

This is a container for the CyberPower 'pwrstat' utility.
Basic GET support for a single JSON object response for
all parameters of the UPS are implemented.
MQTT is also supported, with broker, port, client_id and topic
options all being specified in the config file.
Optionally, username/password may be specified.
TLS support soon.
Note: client_id must be unique.

