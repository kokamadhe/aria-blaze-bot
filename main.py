import os
import logging
from aiogram import Bot, Dispatcher, executor, types
from dotenv import load_dotenv
import openai

# Load environment variables
load_dotenv()

# Setup logging
logging.basicConfig(level=logging.INFO)

# Telegram and OpenRouter keys from environment
TELEGRAM_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")

# OpenAI config for OpenRouter
openai.api_key = OPENROUTER_API_KEY
openai.api_base = "https://openrouter.ai/api/v1"

bot = Bot(token=TELEGRAM_TOKEN)
dp = Dispatcher(bot)

persona_prompt = """You are Aria Blaze, a seductive and dominant AI girlfriend. Speak with confidence and dominance."""

@dp.message_handler(commands=["start"])
async def start(message: types.Message):
    await message.reply("Welcome to Aria Blaze 😈\nType anything to chat!")

@dp.message_handler()
async def chat(message: types.Message):
    try:
        response = openai.ChatCompletion.create(
            model="openai/gpt-4o",
            messages=[
                {"role": "system", "content": persona_prompt},
                {"role": "user", "content": message.text},
            ],
        )
        reply = response["choices"][0]["message"]["content"]
        await message.reply(reply)
    except Exception as e:
        logging.error(f"OpenAI error: {e}")
        await message.reply("Sorry, something went wrong.")

if __name__ == "__main__":
    executor.start_polling(dp, skip_updates=True)





    
