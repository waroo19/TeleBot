# python 3.11

import random
import time
from paho.mqtt import client as mqtt_client
from telegram.ext import Updater, CommandHandler, Filters, MessageHandler
import logging
from telegram import Update
from telegram.ext import CallbackContext
from telegram import Bot
import requests




logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
# Telegram bot token
BOT_TOKEN = "6881742840:AAEgTkuFUXNucJdSejI8ZfZ5e0OCzUleqtQ"

broker = '3.87.254.59'
port = 1883
topics = ["sensors/temperature","sensors/motion", "sensors/light"]
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


def on_publish(client,userdata,mid):             #create function for callback
    print(f"Data on published with mid value: {mid}")


def publish(client,topic, msg):
    client.on_publish = on_publish
    client.publish(topic,msg)
def subscribe_topic(client: mqtt_client):
    for topic in topics:
        client.subscribe(topic)
    client.on_message = on_message


def connect_broker(update, context):
    """Connect to MQTT broker."""
    client = connect_mqtt()
    context.bot_data['mqtt_broker'] = client
    subscribe_topic(client)
    client.loop_start()
    update.message.reply_text("Connected to MQTT broker.")
    update.message.reply_text(f"Subscribed to following topics: {', '.join(topics)}")

def publish_command(update, context):
    client = context.bot_data.get('mqtt_broker') 
    
    topic = context.args[0]
    msg = context.args[1]
    publish(client, topic, msg)
    update.message.reply_text("Messages published successfully.")
    
def unknown_text(update,context):
    welcome_message = """
    Hi there!  I'm the Home Guardian bot, keeping an eye on your environment. 

    Type these commands to get started:
    /start - I hope you know what you do 
    /help - See a list of all available commands.
    """
    update.message.reply_text(welcome_message)

def help(update,context):
    help_message = """
    Hi there!  I'm the Home Guardian bot, keeping an eye on your environment. 

    Here are all the available commands:
    /help - See a list of all available commands.
    /start - Warming up before you can connect to the broker
    /con - Connect to the MQTT Broker
    /pub topic/name message - Publish message to topic
    """
    update.message.reply_text(help_message)



def start(update: Update, context: CallbackContext) -> None:
    global chat_id
    chat_id = update.effective_chat.id
    
    print(f"Chat ID is: {chat_id}")
    context.bot.send_message(chat_id=chat_id, text="Welcome")
    

def main():
    
    # Create the Updater and pass it the bot's token
    updater = Updater(BOT_TOKEN,use_context=True)
    
    # Get the dispatcher to register handlers
    dp = updater.dispatcher
    
    # Register the command handler for /connect
    dp.add_handler(CommandHandler("con", connect_broker))
    dp.add_handler(CommandHandler("help", help))
    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(CommandHandler("pub", publish_command))
    updater.dispatcher.add_handler(MessageHandler(Filters.text, unknown_text)) 
    # Start the Bot
    updater.start_polling()


    # Run the bot until you send a signal to stop it
    updater.idle()
    
if __name__ == '__main__':
    main()
