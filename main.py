import discord
from discord.ext import commands
import openai
import random
import os

from keep_alive import keep_alive  # For Render or Replit

# Load API keys from environment variables
openai.api_key = os.getenv("OPENAI_API_KEY")
discord_token = os.getenv("discord_token")

# Set up intents
intents = discord.Intents.default()
intents.message_content = True
intents.messages = True

# Create bot
bot = commands.Bot(command_prefix="!", intents=intents)

# Hinglish fallback replies if OpenAI fails
fallback_replies = [
    "Arey bhai, thoda ruk ja... server gaya lol..",
    "API ne resign de diya yaar 😭",
    "Internet slow chal raha hai, jaise school ki WiFi 😅",
    "GPT abhi chai peene gaya hai ☕",
    "Mujhe mat bol, OpenAI ka server hi off hai 😂",
    "Bhai, thoda ruk ja... sochta hoon 🤔",
    "Tu mast banda hai, sachi!",
    "Kya baat hai! Ye to badiya bola tune!",
    "Mujhe thoda aur bol, fir mai reply deta hoon 😉",
    "Arey wah, tu to intelligent nikla! 🧠"
]

# Called when bot is online
@bot.event
async def on_ready():
    print(f'✅ Bot is live as {bot.user}')

# ChatGPT logic
def get_ai_reply(user_message):
    try:
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {
                    "role": "system",
                    "content": "Tu ek friendly Discord bot hai jo Hinglish mein baat karta hai. Funny, chill aur thoda witty tone mein reply karta hai."
                },
                {
                    "role": "user",
                    "content": user_message
                }
            ]
        )
        return response.choices[0].message.content
    except Exception as e:
        print(f"❌ OpenAI error: {e}")
        return random.choice(fallback_replies)

# When someone sends message
@bot.event
async def on_message(message):
    if message.author == bot.user:
        return

    if message.content.startswith("!bot"):
        prompt = message.content.replace("!bot", "").strip()
        if not prompt:
            prompt = "Tu kaun hai?"
        reply = get_ai_reply(prompt)
        await message.channel.send(reply)

    await bot.process_commands(message)

# Keep server alive (important for Render)
keep_alive()

# Run the bot
bot.run(discord_token)
