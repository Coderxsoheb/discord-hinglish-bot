import discord
from discord.ext import commands
import os
import random
import requests
import asyncio # For asynchronous operations with requests

from keep_alive import keep_alive  # For Render or Replit

# --- Configuration ---
# Load API keys from environment variables
# IMPORTANT: Make sure you set 'GEMINI_API_KEY' and 'DISCORD_BOT_TOKEN'
# in your Render environment variables exactly as these names are spelled.
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
discord_token = os.getenv("DISCORD_BOT_TOKEN") # Changed to match common naming convention

print("🔑 GEMINI_API_KEY loaded:", "Yes" if GEMINI_API_KEY else "No")
print("🔑 DISCORD_BOT_TOKEN loaded:", "Yes" if discord_token else "No")

# Gemini API endpoint (using gemini-2.0-flash as requested)
GEMINI_API_URL = "https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent"

# Set up intents
intents = discord.Intents.default()
intents.message_content = True # Required to read message content
intents.messages = True # Required for message events

# Create bot
bot = commands.Bot(command_prefix="!", intents=intents)

# Hinglish fallback replies if API fails
fallback_replies = [
    "Arey bhai, thoda ruk ja... server gaya lol..",
    "API ne resign de diya yaar 😭",
    "Internet slow chal raha hai, jaise school ki WiFi 😅",
    "GPT abhi chai peene gaya hai ☕", # You might want to change this to "Gemini" now!
    "Mujhe mat bol, Google ka server hi off hai 😂",
    "Bhai, thoda ruk ja... sochta hoon 🤔",
    "Tu mast banda hai, sachi!",
    "Kya baat hai! Ye to badiya bola tune!",
    "Mujhe thoda aur bol, fir mai reply deta hoon 😉",
    "Arey wah, tu to intelligent nikla! 🧠"
]

# --- Event Handlers ---

@bot.event
async def on_ready():
    """
    Called when the bot successfully connects to Discord.
    """
    print(f'✅ Bot is live as {bot.user}')
    if not discord_token:
        print("WARNING: DISCORD_BOT_TOKEN environment variable not found. Bot may not function correctly.")
    if not GEMINI_API_KEY:
        print("WARNING: GEMINI_API_KEY environment variable not found. Gemini API calls will fail.")

# Gemini API logic
async def get_gemini_reply(user_message):
    """
    Makes an asynchronous call to the Gemini API to get a chat response.
    """
    # If API key is not loaded, immediately return a fallback
    if not GEMINI_API_KEY:
        print("❌ Gemini API Key is missing. Using fallback.")
        return random.choice(fallback_replies)

    # Prepare the payload for the Gemini API request
    chat_history = []
    chat_history.append({"role": "user", "parts": [{"text": user_message}]})

    payload = {"contents": chat_history}

    # The API key is passed as a query parameter for the Gemini API
    api_url_with_key = f"{GEMINI_API_URL}?key={GEMINI_API_KEY}"

    try:
        print(f"Attempting to call Gemini API for message: '{user_message[:50]}...'")
        # Use asyncio.to_thread to run the synchronous requests.post in a separate thread
        # This prevents blocking the Discord bot's event loop.
        response = await asyncio.to_thread(
            requests.post,
            api_url_with_key,
            headers={'Content-Type': 'application/json'},
            json=payload,
            timeout=20 # Set a generous timeout for the API call
        )

        response.raise_for_status() # Raise an HTTPError for bad responses (4xx or 5xx)

        result = response.json()
        print(f"✅ Gemini API Raw Response: {result}")

        # Parse the response to extract the text content
        if result.get('candidates') and len(result['candidates']) > 0 and \
           result['candidates'][0].get('content') and \
           result['candidates'][0]['content'].get('parts') and \
           len(result['candidates'][0]['content']['parts']) > 0:
            text = result['candidates'][0]['content']['parts'][0].get('text')
            if text:
                print(f"✅ Gemini API Reply: {text}")
                return text
            else:
                print("❌ Gemini API response did not contain text content.")
                return random.choice(fallback_replies)
        else:
            print("❌ Gemini API response structure unexpected or empty.")
            return random.choice(fallback_replies)

    except requests.exceptions.HTTPError as e:
        # Handle HTTP errors (e.g., 400 Bad Request, 401 Unauthorized, 403 Forbidden, 429 Rate Limit, 500 Internal Server Error)
        print(f"❌ HTTP Error during Gemini API call: {e.response.status_code} - {e.response.text}")
        if e.response.status_code == 400:
            print("Hint: Check your API key or the request payload format.")
        elif e.response.status_code == 401 or e.response.status_code == 403:
            print("Hint: API key might be invalid or unauthorized.")
        elif e.response.status_code == 429:
            print("Hint: Rate limit exceeded. Try again later.")
        return random.choice(fallback_replies)
    except requests.exceptions.ConnectionError as e:
        # Handle network-related errors (e.g., DNS failure, refused connection)
        print(f"❌ Connection Error during Gemini API call: {e}")
        print("Hint: Check internet connectivity or API endpoint URL.")
        return random.choice(fallback_replies)
    except requests.exceptions.Timeout as e:
        # Handle request timeout errors
        print(f"❌ Timeout Error during Gemini API call: {e}")
        print("Hint: API is taking too long to respond. Could be network latency or API server load.")
        return random.choice(fallback_replies)
    except requests.exceptions.RequestException as e:
        # Catch any other general requests library exceptions
        print(f"❌ General Request Error during Gemini API call: {e}")
        return random.choice(fallback_replies)
    except ValueError as e:
        # Handle JSON decoding errors if response.json() fails
        print(f"❌ JSON Decoding Error from Gemini API: {e}")
        print("Hint: API might be returning non-JSON or malformed JSON.")
        return random.choice(fallback_replies)
    except Exception as e:
        # Catch any other unexpected errors
        print(f"❌ An unexpected error occurred during Gemini API call: {e}")
        return random.choice(fallback_replies)


# When someone sends message
@bot.event
async def on_message(message):
    """
    Processes incoming messages from Discord.
    """
    if message.author == bot.user:
        return

    # If message starts with '!bot', use Gemini API
    if message.content.lower().startswith("!bot"):
        prompt = message.content[len("!bot"):].strip() # Remove '!bot' prefix
        if not prompt:
            prompt = "Tu kaun hai?" # Default prompt if user just types '!bot'

        print(f"User '{message.author}' sent prompt: '{prompt}'")
        # Await the asynchronous API call
        reply = await get_gemini_reply(prompt)
        await message.channel.send(reply)

    # Process other commands if any (e.g., if you add more commands later)
    await bot.process_commands(message)

# Keep server alive (important for Render)
keep_alive()

# Run the bot
if discord_token:
    print("Starting Discord bot...")
    bot.run(discord_token)
else:
    print("Error: DISCORD_BOT_TOKEN not found. Bot cannot start.")

