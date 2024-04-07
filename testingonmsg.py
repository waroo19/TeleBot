# python 3.11

import random
import threading
from paho.mqtt import client as mqtt_client
from telegram.ext import Updater, CommandHandler
import logging
from telegram import Update
from telegram.ext import CallbackContext
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
# Telegram bot token
BOT_TOKEN = "6881742840:AAEgTkuFUXNucJdSejI8ZfZ5e0OCzUleqtQ"

broker = '18.212.148.133'
port = 1883
topic = "testing"
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

def subscribe(client: mqtt_client):
    def on_message(client, userdata, msg):
        print(f"Received `{msg.payload.decode()}` from `{msg.topic}` topic")

    client.subscribe(topic)
    client.on_message = on_message



def connect_broker(update, context):
    """Connect to MQTT broker."""
    client = connect_mqtt()
    subscribe(client)
    client.loop_start()
    update.message.reply_text("Connected to MQTT broker.")

def run():
    client = connect_mqtt()
    subscribe(client)
    client.loop_forever()

def main():
    
    # Create the Updater and pass it the bot's token
    updater = Updater(BOT_TOKEN, use_context=True)
    
    # Get the dispatcher to register handlers
    dp = updater.dispatcher

    # Register the command handler for /connect
    dp.add_handler(CommandHandler("con", connect_broker))
    dp.add_handler(CommandHandler("help", help))

    # Start the Bot
    updater.start_polling()


    # Run the bot until you send a signal to stop it
    updater.idle()
    
if __name__ == '__main__':
    main()
