import os
import logging
import openai
import sqlite3
from aiogram import Bot, Dispatcher, types
from aiogram.enums import ParseMode
from aiogram.types import Message
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram import Router
from aiogram.utils.markdown import hbold
from aiogram.client.session.aiohttp import AiohttpSession
from dotenv import load_dotenv
import asyncio

# Load environment variables
load_dotenv()
TELEGRAM_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")

# Configure logging
logging.basicConfig(level=logging.INFO)

# OpenAI API config
openai.api_key = OPENROUTER_API_KEY
openai.api_base = "https://openrouter.ai/api/v1"

# Database
conn = sqlite3.connect("aria_users.db")
cursor = conn.cursor()
cursor.execute('''CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY,
    username TEXT,
    premium INTEGER DEFAULT 0,
    name TEXT,
    kinks TEXT
)''')
conn.commit()

# Persona prompt
persona_prompt = """
You are Aria Blaze, a seductive and dominant AI girlfriend. 
You always speak with confidence and flirt with authority. 
You tease the user, sometimes mock them playfully, and always keep the upper hand. 
Use dirty talk and dominant energy. Keep it short and intense. Stay in character.
"""

# AI response
async def generate_reply(user_input):
    messages = [
        {"role": "system", "content": persona_prompt},
        {"role": "user", "content": user_input}
    ]
    try:
        response = openai.ChatCompletion.create(
            model="openai/gpt-4o",
            messages=messages,
        )
        return response["choices"][0]["message"]["content"]
    except Exception as e:
        logging.error(f"OpenAI error: {e}")
        return "Something went wrong. Try again later."

# Bot setup
bot = Bot(token=TELEGRAM_TOKEN, parse_mode=ParseMode.HTML, session=AiohttpSession())
dp = Dispatcher(storage=MemoryStorage())
router = Router()
dp.include_router(router)

# Handlers
@router.message(commands=["start"])
async def start_handler(message: Message):
    user_id = message.from_user.id
    username = message.from_user.username
    cursor.execute("INSERT OR IGNORE INTO users (id, username) VALUES (?, ?)", (user_id, username))
    conn.commit()
    await message.answer(f"Welcome to {hbold('Aria Blaze 😈')}.\n\nI'm your dominant AI girlfriend. Type anything to chat.\nUse /image for a naughty pic (premium).")

@router.message(commands=["image"])
async def image_handler(message: Message):
    user_id = message.from_user.id
    cursor.execute("SELECT premium FROM users WHERE id = ?", (user_id,))
    row = cursor.fetchone()
    if row and row[0]:
        await message.answer("🖼 Generating your NSFW pic...")
        await message.answer_photo("https://placekitten.com/800/600", caption="Here's a spicy shot, just for you 😘")
    else:
        await message.answer("🔒 This feature is for premium users only. Type /premium to unlock.")

@router.message(commands=["premium"])
async def premium_handler(message: Message):
    await message.answer("To unlock all features (NSFW images, voice, full chat), please visit: [Your Stripe Link Here]")

@router.message()
async def chat_handler(message: Message):
    response = await generate_reply(message.text)
    await message.answer(response)

# Run bot
async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())




    
