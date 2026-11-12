"""Elica Connect constants."""

APPLICATION_UUID = "0ba86de295087670"

API_BASE_URL = "https://cloudprod.elica.com/eiot-api/v1"
API_CLIENT_ID = "eiot-app"
# Public application credential used by the Elica mobile application.
API_CLIENT_SECRET = "VqwG1KTB77UeROu"

MQTT_HOST = "cloudprodmqtt.elica.com"
MQTT_PORT = 8883
MQTT_TLS = True
MQTT_KEEPALIVE = 60
MQTT_TOPIC_FORMAT = "v1/device/{CUID}/statusjson"
