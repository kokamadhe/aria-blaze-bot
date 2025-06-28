from flask import Flask, request
import requests
import os
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")

# Replace with your Telegram ID(s)
PREMIUM_USERS = ["1985536979"]

def send_message(chat_id, text):
    requests.post(f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage", json={
        "chat_id": chat_id,
        "text": text
    })

def send_photo(chat_id, photo_url, caption=""):
    requests.post(f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendPhoto", json={
        "chat_id": chat_id,
        "photo": photo_url,
        "caption": caption
    })

def generate_ai_reply(prompt):
    headers = {
        "Authorization": f"Bearer {OPENROUTER_API_KEY}",
        "HTTP-Referer": "https://aria-blaze-bot",
        "Content-Type": "application/json"
    }
    payload = {
        "model": "openai/gpt-4o",
        "messages": [
            {"role": "system", "content": "You are Aria Blaze, a seductive AI girlfriend who flirts and teases."},
            {"role": "user", "content": prompt}
        ]
    }
    try:
        res = requests.post("https://openrouter.ai/api/v1/chat/completions", headers=headers, json=payload)
        res.raise_for_status()
        return res.json()["choices"][0]["message"]["content"]
    except Exception as e:
        print("Chat error:", e)
        return "❌ Chat generation failed."

def generate_image(prompt):
    headers = {
        "Authorization": f"Bearer {OPENROUTER_API_KEY}",
        "HTTP-Referer": "https://aria-blaze-bot",
        "Content-Type": "application/json"
    }
    payload = {
        "model": "stability-ai/sdxl",
        "prompt": prompt
    }
    try:
        res = requests.post("https://openrouter.ai/api/v1/images/generate", headers=headers, json=payload)
        res.raise_for_status()
        data = res.json()
        return data["data"][0]["url"]
    except Exception as e:
        print("Image error:", e)
        return None

@app.route(f"/{TELEGRAM_TOKEN}", methods=["POST"])
def webhook():
    data = request.json
    message = data.get("message", {})
    chat_id = str(message.get("chat", {}).get("id"))
    text = message.get("text", "")

    if not chat_id or not text:
        return {"ok": True}

    if text.startswith("/flirt"):
        send_message(chat_id, "You're so addictive 🔥")

    elif text.startswith("/moan"):
        send_message(chat_id, "Ahhh... don’t stop 😩")

    elif text.startswith("/chat "):
        if chat_id in PREMIUM_USERS:
            prompt = text[6:]
            reply = generate_ai_reply(prompt)
            send_message(chat_id, reply)
        else:
            send_message(chat_id, "🚫 This command is for premium users only.")

    elif text.startswith("/image "):
        if chat_id in PREMIUM_USERS:
            prompt = text[7:]
            image_url = generate_image(prompt)
            if image_url:
                send_photo(chat_id, image_url, f"Here's what I imagined for: {prompt}")
            else:
                send_message(chat_id, "❌ Failed to generate image.")
        else:
            send_message(chat_id, "🚫 This command is for premium users only.")

    else:
        send_message(chat_id, "Hey it's Aria 😘\nTry /flirt, /moan, /chat or /image")

    return {"ok": True}

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=3000)

    
