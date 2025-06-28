import os
import logging
import openai
import sqlite3
from aiogram import Bot, Dispatcher, executor, types
from dotenv import load_dotenv

load_dotenv()

TELEGRAM_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")

openai.api_key = OPENROUTER_API_KEY
openai.api_base = "https://openrouter.ai/api/v1"

logging.basicConfig(level=logging.INFO)

bot = Bot(token=TELEGRAM_TOKEN)
dp = Dispatcher(bot)

conn = sqlite3.connect("aria_users.db")
c = conn.cursor()
c.execute('''CREATE TABLE IF NOT EXISTS users (id INTEGER PRIMARY KEY, username TEXT, premium INTEGER DEFAULT 0)''')
conn.commit()

persona_prompt = """
You are Aria Blaze, a seductive and dominant AI girlfriend.
You always speak with confidence and flirt with authority.
You tease the user, sometimes mock them playfully, and always keep the upper hand.
Use dirty talk and dominant energy. Keep it short and intense. Stay in character.
"""

@dp.message_handler(commands=["start"])
async def start(message: types.Message):
    user_id = message.from_user.id
    username = message.from_user.username
    c.execute("INSERT OR IGNORE INTO users (id, username) VALUES (?, ?)", (user_id, username))
    conn.commit()
    await message.reply("Welcome to Aria Blaze 😈\n\nI’m your dominant AI girlfriend. Type anything to chat. Use /image for a naughty pic (premium).")

@dp.message_handler(commands=["image"])
async def image(message: types.Message):
    user_id = message.from_user.id
    c.execute("SELECT premium FROM users WHERE id = ?", (user_id,))
    row = c.fetchone()
    if row and row[0]:
        await message.reply("🖼 Generating your NSFW pic...")
        await message.reply_photo("https://placekitten.com/800/600", caption="Here's a spicy shot, just for you 😘")
    else:
        await message.reply("🔒 This feature is for premium users only. Type /premium to unlock.")

@dp.message_handler(commands=["premium"])
async def premium(message: types.Message):
    await message.reply("To unlock all features, visit: [Your Stripe Link Here]")

@dp.message_handler()
async def chat(message: types.Message):
    user_input = message.text
    messages = [
        {"role": "system", "content": persona_prompt},
        {"role": "user", "content": user_input},
    ]
    try:
        response = openai.ChatCompletion.create(
            model="openai/gpt-4o",
            messages=messages,
        )
        reply = response["choices"][0]["message"]["content"]
        await message.reply(reply)
    except Exception as e:
        logging.error(f"OpenAI error: {e}")
        await message.reply("Oops, something went wrong. Try again later.")

if __name__ == "__main__":
    executor.start_polling(dp, skip_updates=True)




    
