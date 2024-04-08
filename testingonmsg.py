# python 3.11

import random
import threading
from paho.mqtt import client as mqtt_client
from telegram.ext import Updater, CommandHandler
import logging
from telegram import Update
from telegram.ext import CallbackContext
from telegram import Bot

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
# Telegram bot token
BOT_TOKEN = "6881742840:AAEgTkuFUXNucJdSejI8ZfZ5e0OCzUleqtQ"

broker = '54.85.61.173'
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

def on_message(client, userdata, msg):
    message = f"Received `{msg.payload.decode()}` from `{msg.topic}` topic"
    # Initialize the Telegram bot
    bot = Bot(token=BOT_TOKEN)

    # Send the message to the Telegram chat
    bot.send_message(chat_id=chat_id, text=message)






def subscribe_topic(client: mqtt_client):
    

    client.subscribe(topic)
    client.on_message = on_message



def connect_broker(update, context):
    """Connect to MQTT broker."""
    client = connect_mqtt()
    subscribe_topic(client)
    client.loop_start()
    update.message.reply_text("Connected to MQTT broker.")
    update.message.reply_text(f"Subscribed to topic: {topic}")

def start(update: Update, context: CallbackContext) -> None:
    global chat_id
    chat_id = update.effective_chat.id
    
    print(f"Chat ID is: {chat_id}")
    context.bot.send_message(chat_id=chat_id, text="Welcome")


def main():
    
    # Create the Updater and pass it the bot's token
    updater = Updater(BOT_TOKEN, use_context=True)
    
    # Get the dispatcher to register handlers
    dp = updater.dispatcher

    # Register the command handler for /connect
    dp.add_handler(CommandHandler("con", connect_broker))
    dp.add_handler(CommandHandler("help", help))
    dp.add_handler(CommandHandler("start", start))
    # Start the Bot
    updater.start_polling()


    # Run the bot until you send a signal to stop it
    updater.idle()
    
if __name__ == '__main__':
    main()
