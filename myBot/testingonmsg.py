# python 3.11

import random
import time
from paho.mqtt import client as mqtt_client
from telegram.ext import Updater, CommandHandler, Filters, MessageHandler
import logging
from telegram import Update
from telegram.ext import CallbackContext
from telegram import Bot
import threading
import spacy
from spacy.matcher import Matcher
from handler import identify_intent
from telegram import ReplyKeyboardMarkup, ReplyKeyboardRemove

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
# Telegram bot token
#BOT_TOKEN = "6493593340:AAH0js-v0fL0QC-lvTBH4ts4ifpj8wPaN3M"
BOT_TOKEN = "6881742840:AAEgTkuFUXNucJdSejI8ZfZ5e0OCzUleqtQ"

broker = '34.229.115.212'
port = 1883
topics = ["sensors/temperature","sensors/motion", "sensors/light"]
# Generate a Client ID with the subscribe prefix.
client_id = f'subscribe-{random.randint(0, 100)}'


nlp = spacy.load('en_core_web_sm')
help_message = """
    Tired of fumbling for light switches? I'm your friendly lighting assistant!  
    Let's brighten things up. Starting with light control. 
    Say something like, 'Turn on the kitchen light'
    """
start_message = """"
    👋 Welcome to the My Home Guardian bot!  
    My sense of humor may be a bit glitchy, but my security protocols are rock-solid. 
    Please press /start to spark things up!
    """
redirect_message =  """
    I might not be able to help with that directly. 
    However, I excel at controlling your lights, alarm, and thermostat with MQTT.  
    Could I assist with one of those tasks instead?

    """
temp_message =  """
    I sense a temperature disturbance! 
    Perhaps your trusty AC unit and I should team up. 
    Would you like it on or off to restore comfort?

    """
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

def publish_cmd(update, context):
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


""" 
def identify_intent(text):
    
    matcher = Matcher(nlp.vocab)

    doc = nlp(text.lower())
    pattern_light1 = [
        {"LEMMA": "turn"}, 
        {"LEMMA": "on"}, 
        {"POS": "DET", "OP": "?"},
        {"POS": "NOUN", "OP": "?"},
        {"TEXT": "light"},
        {"OP": "?"}
    ]
 
    pattern_light2 = [
        {"LEMMA": "turn"},  
        {"POS": "DET", "OP": "?"},
        {"POS": "NOUN", "OP": "?"},
        {"TEXT": "light"},
        {"LEMMA": "on"},
        {"OP": "?"}
    ]
    # Add the pattern to the matcher
    matcher.add("TURN_ON_LIGHT_PATTERN", [pattern_light1,pattern_light2])
    
    # Apply the matcher to the doc
    matches = matcher(doc)
    for match_id, start, end in matches:
        matched_pattern_id = match_id  
        if matched_pattern_id == matcher.vocab.strings["TURN_ON_LIGHT_PATTERN"]:
            print("Turn the light on pattern detected!")
            return "turn_on_light"
        else:
             return "help"

 """
def start(update: Update, context: CallbackContext) -> None:
    global chat_id
    chat_id = update.effective_chat.id
    
    print(f"Chat ID is: {chat_id}")
    context.bot.send_message(chat_id=chat_id, text=help_message)

    client = connect_mqtt()
    context.bot_data['mqtt_broker'] = client
    subscribe_topic(client)
    client.loop_start()

def handle_telegram_message(update, context):
    print("handler is being called")
    user_message = update.message.text
    intent = identify_intent(user_message)

    if intent == "turn_on_light":
        client = context.bot_data.get('mqtt_broker')  
        publish(client, "sensors/light", "on")  
        update.message.reply_text("Turning the light on!")
    elif intent == "turn_off_light":
        client = context.bot_data.get('mqtt_broker')  
        publish(client, "sensors/light", "off")  
        update.message.reply_text("Turning the light off!")
    elif intent == "turn_on_alarm":
        client = context.bot_data.get('mqtt_broker')  
        publish(client, "sensors/motion", "on")  
        update.message.reply_text("Turning the alarm on!")
    elif intent == "turn_on_ac":
        client = context.bot_data.get('mqtt_broker')  
        publish(client, "sensors/temperature", "30")  
        update.message.reply_text("Turning the AC on!")
    elif intent == "turn_off_ac":
        client = context.bot_data.get('mqtt_broker')  
        publish(client, "sensors/temperature", "18")  
        update.message.reply_text("Turning the AC off!")
    elif intent == "help":
        client = context.bot_data.get('mqtt_broker')  
        update.message.reply_text(help_message)
    elif intent == "start":
        client = context.bot_data.get('mqtt_broker')  
        update.message.reply_text(start_message)
    elif intent == "temperature":
        client = context.bot_data.get('mqtt_broker')  
        update.message.reply_text(temp_message)
    else:
        update.message.reply_text(redirect_message)
        

def main():
    
    # Create the Updater and pass it the bot's token
    updater = Updater(BOT_TOKEN,use_context=True)
    
    # Get the dispatcher to register handlers
    dp = updater.dispatcher
    
    # Register the command handler for /connect
    dp.add_handler(CommandHandler("con", connect_broker))
    dp.add_handler(CommandHandler("help", help))
    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(CommandHandler("pub", publish_cmd))
    updater.dispatcher.add_handler(MessageHandler(Filters.text, handle_telegram_message)) 
    # Start the Bot
    #polling_thread = threading.Thread(target=updater.start_polling)
    updater.start_polling()
    #polling_thread.start()
    #polling_thread.join()
    # Run the bot until you send a signal to stop it
    updater.idle()
    
if __name__ == '__main__':
    main()
