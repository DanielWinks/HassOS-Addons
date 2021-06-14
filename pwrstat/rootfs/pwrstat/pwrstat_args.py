import argparse

parser = argparse.ArgumentParser()

parser.add_argument("-mb", "--mqtt_broker", help="MQTT Broker IP Address/DNS Name")
parser.add_argument("-mp", "--mqtt_port", help="MQTT Port")
parser.add_argument("-mc", "--mqtt_clientid", help="MQTT Client ID")
parser.add_argument("-mt", "--mqtt_topic", help="MQTT Topic")
parser.add_argument("-mf", "--mqtt_refresh", help="MQTT Refresh Interval (seconds)")
parser.add_argument("-mq", "--mqtt_qos", help="MQTT QOS")
parser.add_argument("-mr", "--mqtt_retained", help="MQTT Retained Flag")
parser.add_argument("-mu", "--mqtt_username", help="MQTT Username")
parser.add_argument("-mw", "--mqtt_password", help="MQTT Password")

parser.add_argument("-rp", "--rest_port", help="REST Endpoint Port")
parser.add_argument("-rb", "--rest_bind_address", help="REST Bind Address")

parser.add_argument("-pp", "--prom_port", help="Prometheus Port")
parser.add_argument("-pb", "--prom_bind_address", help="Prometheus Bind Address")
parser.add_argument("-pl", "--prom_labels", help="Prometheus Labels")

args = parser.parse_args()

# if __name__ == "__main__":
#     pass
