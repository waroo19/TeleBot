import os
import telebot

import paho.mqtt.client as mqtt
from telegram import Update
from telegram.ext import Updater, CommandHandler, CallbackContext

import submqtt 

BOT_TOKEN = "6881742840:AAEgTkuFUXNucJdSejI8ZfZ5e0OCzUleqtQ"

# Initialize the Telegram bot
bot = telebot.TeleBot(BOT_TOKEN)

#subscribed topics
subscribed_topics = set()


@bot.message_handler(commands=['start', 'hello'])
def send_welcome(message):
    bot.reply_to(message, "Vy, how are you doing?")

# Connect client to MQTT Broker
@bot.message_handler(commands=['connect'])
def connect_mqtt(message):
    submqtt.run()

@bot.message_handler(commands=['subscribe'])
def subscribe_topic(message):
    # Get the chat ID and the topic from the command
    chat_id = message.chat.id
    topic = message.text.split(' ', 1)[1].strip() if len(message.text.split(' ', 1)) > 1 else None

    
    # Check if a topic is provided
    if not topic:
        bot.reply_to(message, "Please provide a topic to subscribe to.")
        return

    # Check if the topic is already subscribed
    if topic in subscribed_topics:
        bot.reply_to(message, "You are already subscribed to the topic: {topic}")
        return

    # Add the topic to the set of subscribed topics
    subscribed_topics.add(topic)

    
    client = submqtt.connect_mqtt()

    
    client.loop_forever()

    # Inform the user about the subscription
    bot.reply_to(message, f"Subscribed to MQTT topic: {topic}")
    
     # Print all subscribed topics
    print("All Subscribed Topics:", subscribed_topics)

bot.infinity_polling()