import os
import subprocess
import threading
import uvicorn
from fastapi import FastAPI
from supabase import create_client
import telebot
from groq import Groq
import google.generativeai as genai
import time
import logging

# تفعيل سجلات الأخطاء لتظهر في Render Logs
logging.basicConfig(level=logging.INFO)

# --- سحب المفاتيح ---
TOKEN = os.environ.get("TELEGRAM_TOKEN")
SUPABASE_URL = os.environ.get("SUPABASE_URL")
SUPABASE_KEY = os.environ.get("SUPABASE_KEY")
GROQ_KEY = os.environ.get("GROQ_API_KEY")
GEMINI_KEY = os.environ.get("GEMINI_API_KEY")

# --- إعداد المحركات ---
bot = telebot.TeleBot(TOKEN)
db = create_client(SUPABASE_URL, SUPABASE_KEY)
client_groq = Groq(api_key=GROQ_KEY)
genai.configure(api_key=GEMINI_KEY)
gemini_model = genai.GenerativeModel("gemini-1.5-flash")

ADMIN_ID = "1071477484" 

app = FastAPI()

@app.get("/")
def home():
    return {"status": "Cinema For Yemen is Online!"}

@bot.message_handler(commands=["start"])
def welcome(message):
    bot.reply_to(message, "🚀 أهلاً بك! البوت شغال الآن على Render.")

@bot.message_handler(func=lambda message: True)
def ai_logic(message):
    if str(message.chat.id) == ADMIN_ID:
        try:
            response = gemini_model.generate_content(message.text)
            bot.reply_to(message, response.text)
        except Exception as e:
            logging.error(f"AI Error: {e}")
            bot.reply_to(message, "🛠 عذراً، المحرك مشغول حالياً.")

def run_bot():
    while True:
        try:
            logging.info("🤖 Starting Telegram Bot Polling...")
            bot.remove_webhook()
            bot.infinity_polling(timeout=60, long_polling_timeout=30)
        except Exception as e:
            logging.error(f"Bot Crashed: {e}")
            time.sleep(10)

if __name__ == "__main__":
    # تشغيل البوت في الخلفية
    bot_thread = threading.Thread(target=run_bot, daemon=True)
    bot_thread.start()
    
    # تشغيل السيرفر
    port = int(os.environ.get("PORT", 10000))
    uvicorn.run(app, host="0.0.0.0", port=port)
