import re
from collections import defaultdict
from dotenv import load_dotenv
from telethon import TelegramClient, events
import os

# Load environment variables from .env file
load_dotenv()

# Get variables from .env
api_id = os.getenv('API_ID')
api_hash = os.getenv('API_HASH')
phone_number = os.getenv('PHONE_NUMBER')
notification_chat_id = int(os.getenv('NOTIFICATION_CHAT_ID'))

print(f"API_ID: {api_id}")
print(f"API_HASH: {api_hash}")
print(f"PHONE_NUMBER: {phone_number}")
print(f"NOTIFICATION_CHAT_ID: {notification_chat_id}")

# Validate environment variables
if not api_id or not api_hash or not phone_number or not notification_chat_id:
    raise ValueError("One or more environment variables are missing in the .env file")

# Create the Telegram client
client = TelegramClient('session_name', api_id, api_hash)

# Dictionary to store tokens and their associated chat counts
tokens = defaultdict(set)  # {token: {chat_ids}}

def extract_tokens(message):
    pattern = r'\b[A-Za-z0-9]{44}\b'
    return re.findall(pattern, message)

# Function to send a notification message
async def send_notification(token):
    notification_message = f"🚨 Token detected in 3 or more chats: {token}"
    print(f"Sending notification: {notification_message}")
    await client.send_message(notification_chat_id, notification_message)

# Define a handler for new messages
@client.on(events.NewMessage)
async def handle_new_message(event):
    chat_id = event.chat_id
    message_text = event.raw_text

    # Extract tokens from the message
    detected_tokens = extract_tokens(message_text)

    for token in detected_tokens:
        # Add the chat ID to the set of chats where the token has appeared
        tokens[token].add(chat_id)

        # If the token appears in 3 or more unique chats, send a notification
        if len(tokens[token]) >= 3:
            print(f"New token from chat {token}: {chat_id}")
            await send_notification(token)

# Start the client
async def main():
    print("Connecting to Telegram...")
    await client.start(phone_number)
    print("Connected to Telegram!")
    print("Listening for new messages...")
    await client.run_until_disconnected()

# Run the event loop
if __name__ == '__main__':
    import asyncio
    asyncio.run(main())
