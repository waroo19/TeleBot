
import random

from paho.mqtt import client as mqtt_client
from telegram import Update
from telegram.ext import Updater, CommandHandler, CallbackContext


broker = 'localhost'
port = 1883
topic = "test"
# Generate a Client ID with the subscribe prefix.
client_id = f'subscribe-{random.randint(0, 100)}'


def connect_mqtt() -> mqtt_client:
    def on_connect(client, userdata, flags, rc):
        if rc == 0:
            print("Connected to MQTT Broker!")
        else:
            print("Failed to connect, return code %d\n", rc)

    client = mqtt_client.Client(client_id)
    client.on_connect = on_connect
    client.connect(broker, port)
    return client


""" def subscribe(client: mqtt_client):
    def on_message(client, userdata, msg):
        print(f"Received `{msg.payload.decode()}` from `{msg.topic}` topic")

    client.subscribe(topic)
    client.on_message = on_message  """
def subscribe(client: mqtt_client, topics: set):
    def on_message(client, userdata, msg):
        print(f"Received `{msg.payload.decode()}` from `{msg.topic}` topic")


    for topic in topics:
        _, rc = client.subscribe(topic)
        if rc == mqtt_client.MQTT_ERR_SUCCESS:
            print(f"Subscribed to topic: {topic}")
        else:
            print(f"Failed to subscribe to topic: {topic}, Return code: {rc}")

    client.on_message = on_message


def run():
    client = connect_mqtt()
    #subscribe(client)
    client.loop_start()    
"""  
if __name__ == '__main__':
    run() """
 