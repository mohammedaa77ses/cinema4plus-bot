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

# --- سحب المفاتيح من Render ---
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

# الأي دي الخاص بك (تأكد منه لاحقاً)
ADMIN_ID = "1071477484" 

# --- واجهة FastAPI ---
app = FastAPI()

@app.get("/")
def home():
    return {"status": "Cinema For Yemen is Online!"}

# --- أوامر تيليجرام ---

@bot.message_handler(commands=["start"])
def welcome(message):
    # سيرد على الجميع الآن للتأكد من التشغيل
    bot.reply_to(message, f"🚀 يا هلا! البوت شغال يا وحش.\nرقم الأي دي حقك هو: {message.chat.id}")

@bot.message_handler(func=lambda message: True)
def ai_logic(message):
    # سيقوم بالرد بالذكاء الاصطناعي على أي مستخدم حالياً للتجربة
    try:
        response = gemini_model.generate_content(message.text)
        bot.reply_to(message, response.text)
    except:
        try:
            chat = client_groq.chat.completions.create(
                messages=[{"role": "user", "content": message.text}],
                model="mixtral-8x7b-32768",
            )
            bot.reply_to(message, chat.choices[0].message.content)
        except:
            bot.reply_to(message, "⚙️ السيرفرات مشغولة، جرب لاحقاً.")

# --- دالة تشغيل البوت ---
def run_bot():
    while True:
        try:
            print("🤖 Starting Telegram Bot...")
            bot.remove_webhook()
            bot.infinity_polling(timeout=20, long_polling_timeout=10)
        except Exception as e:
            print(f"❌ Bot crashed: {e}")
            time.sleep(5)

if __name__ == "__main__":
    # تشغيل البوت في Thread منفصل
    bot_thread = threading.Thread(target=run_bot, daemon=True)
    bot_thread.start()
    
    # تشغيل السيرفر الرئيسي
    port = int(os.environ.get("PORT", 10000))
    uvicorn.run(app, host="0.0.0.0", port=port)
