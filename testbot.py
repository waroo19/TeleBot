import logging
import threading
from telegram import Update
from telegram.ext import Updater, CommandHandler, CallbackContext
import paho.mqtt.publish as publish
# Set up logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)

# URL for the MQTT script 
MQTT_BROKER = 'localhost'
MQTT_PORT = 1883
MQTT_SCRIPT_TOPIC = 'mqtt_script_topic'

# Set of subscribed topics
subscribed_topics = set()

# Replace 'YOUR_BOT_TOKEN' with your actual bot token
BOT_TOKEN = "6881742840:AAEgTkuFUXNucJdSejI8ZfZ5e0OCzUleqtQ"

def start(update: Update, context: CallbackContext) -> None:
    update.message.reply_text('Hello! I am your MQTT bot.')

def stop_bot():
    updater.stop()
    updater.is_idle = False  # Terminate the updater's idle loop

def stop(update: Update, context: CallbackContext) -> None:
    update.message.reply_text('Stopping the bot...')
    threading.Thread(target=stop_bot).start()

#Function to subscribe to an MQTT topics
def subscribe(update: Update, context: CallbackContext) -> None:

    #Get chat ID and the topic from the user's message
    chat_id = update.message.chat.id
    command_parts = update.message.text.split(' ', 1)

    # Check if the command is "/subscribe" and there is a topic provided
    if len(command_parts) > 1 and command_parts[0].lower() == "/subscribe":
        topic = command_parts[1].strip()
        # Now 'topic' contains the extracted topic
        update.message.reply_text(f"Subscribing to topic: {topic}")
        # Publish a message to the MQTT script topic
        publish.single(MQTT_SCRIPT_TOPIC, payload=f'{chat_id},{topic}', hostname=MQTT_BROKER)

        # Respond to the user
        update.message.reply_text(f"Subscribed to MQTT topic: {topic}")

    else:
        update.message.reply_text("Invalid /subscribe command. Please provide a topic.")

    # Add the topic to the set of subscribed topics
    subscribed_topics.add(topic)

    # Inform the user about the subscription
    update.message.reply_text(f"Subscribed MQTT topics: {topic}")




def main() -> None:
    global updater
    # Create the Updater and pass it the bot's token
    updater = Updater(BOT_TOKEN)

    # Get the dispatcher to register handlers
    dp = updater.dispatcher

    # Register the  commands
    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(CommandHandler("stop", stop))
    dp.add_handler(CommandHandler("subscribe", subscribe))
    # Start the Bot
    updater.start_polling()

    # Run the bot until you send a signal to stop it
    updater.idle()

if __name__ == '__main__':
    main()
