import paho.mqtt.client as mqtt
from telegram.ext import Updater, CommandHandler
import logging
import random

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
# Generate a Client ID with the subscribe prefix.
client_id = f'subscribe-{random.randint(0, 100)}'
# MQTT broker details
MQTT_BROKER = "18.212.125.214"
MQTT_PORT = 1883

# Telegram bot token
BOT_TOKEN = "6881742840:AAEgTkuFUXNucJdSejI8ZfZ5e0OCzUleqtQ"

# MQTT client instance
mqtt_client = mqtt.Client(client_id)

help_info = {
    "/con": "Connect to MQTT broker.",
    "/stop": "Stop the bot.",
    "/sub": "Subscribe to receive updates.",
    "pub": "Publish to Riot",
    "/help": "Display help information."
}

def subscribe(client: mqtt.Client, topic: str):
    """Subscribe to an MQTT topic."""
    def on_message(client, userdata, msg):
        print(f"Received `{msg.payload.decode()}` from `{msg.topic}` topic")

    
    client.on_message = on_message
    client.subscribe(topic)

def connect_broker(update, context):
    """Connect to MQTT broker."""
    try:
        mqtt_client.connect(MQTT_BROKER, MQTT_PORT)
        update.message.reply_text("Connected to MQTT broker.")
    except Exception as e:
        update.message.reply_text(f"Failed to connect to MQTT broker: {e}")

def help(update, context):
    
    help_message = "\n".join([f"{cmd}: {info}" for cmd, info in help_info.items()])
    update.message.reply_text(f"Here are the available commands:\n{help_message}")

def sub(update, context):
    topic = context.args[0] 
    subscribe(mqtt_client, topic)
    update.message.reply_text(f"Subscribed to topic: {topic}")



def main():
    # Create the Updater and pass it the bot's token
    updater = Updater(BOT_TOKEN, use_context=True)

    # Get the dispatcher to register handlers
    dp = updater.dispatcher

    # Register the command handler for /connect
    dp.add_handler(CommandHandler("con", connect_broker))
    dp.add_handler(CommandHandler("help", help))
    dp.add_handler(CommandHandler("sub", sub))
    # Start the Bot
    updater.start_polling()


    # Run the bot until you send a signal to stop it
    updater.idle()
    
if __name__ == '__main__':
    main()
