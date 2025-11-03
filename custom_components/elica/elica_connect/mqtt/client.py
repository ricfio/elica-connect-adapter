"""Elica Connect API - MQTT client module (subscribe-only)."""

import time
import json
import paho.mqtt.client as mqtt

from elica_connect.mqtt.constants import (
    MQTT_BROKER,
    MQTT_PORT,
    MQTT_KEEPALIVE,
    MQTT_TOPIC_SUB,
    #
    CLIENT_ID,
    USERNAME,
    PASSWORD,
    CUID,
)


# --- CALLBACK ---
def on_connect(client, userdata, flags, rc):
    print(f"[MQTT] Connected with result code {rc}")
    topic = MQTT_TOPIC_SUB.format(CUID=CUID)
    client.subscribe(topic, qos=1)
    print(f"[MQTT] Subscribed to {topic}")


def on_message(client, userdata, msg):
    try:
        payload = msg.payload.decode("utf-8")
        data = json.loads(payload)
    except Exception:
        data = payload
    print(f"[MQTT] {msg.topic} -> {data}")


# --- CLIENT SETUP ---
client = mqtt.Client(client_id=CLIENT_ID, clean_session=True)
client.username_pw_set(USERNAME, PASSWORD)
client.on_connect = on_connect
client.on_message = on_message

# --- CONNECT ---
client.connect(MQTT_BROKER, MQTT_PORT, keepalive=MQTT_KEEPALIVE)
client.loop_start()

# --- LOOP PER RICEVERE MESSAGGI ---
try:
    while True:
        time.sleep(1)
except KeyboardInterrupt:
    print("Exiting...")
finally:
    client.loop_stop()
    client.disconnect()
