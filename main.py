import os
import subprocess
import threading
import uvicorn
from fastapi import FastAPI
from supabase import create_client
import telebot
from groq import Groq
import google.generativeai as genai

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

ADMIN_ID = 1071477484  # الأي دي الخاص بك

# --- أوامر تيليجرام ---
@bot.message_handler(commands=["start"])
def welcome(message):
    if message.chat.id == ADMIN_ID:
        bot.reply_to(message, "🚀 البوت شغال ياوحش!")

@bot.message_handler(commands=["install"])
def install_lib(message):
    if message.chat.id == ADMIN_ID:
        try:
            lib = message.text.split(maxsplit=1)[1]
            res = subprocess.run(f"pip install {lib}", shell=True, capture_output=True, text=True)
            bot.reply_to(message, f"✅ تم تثبيت: {lib}\n{res.stdout[:500]}")
        except:
            bot.reply_to(message, "⚠️ لازم تكتب اسم المكتبة بعد الأمر.")

@bot.message_handler(commands=["exec"])
def execute_command(message):
    if message.chat.id == ADMIN_ID:
        try:
            cmd = message.text.split(maxsplit=1)[1]
            res = subprocess.run(cmd, shell=True, capture_output=True, text=True)
            output = res.stdout if res.stdout else res.stderr
            bot.reply_to(message, f"📤 النتيجة:\n{output[:1000]}")
        except Exception as e:
            bot.reply_to(message, f"❌ خطأ: {str(e)}")

@bot.message_handler(commands=["add"])
def add_movie(message):
    if message.chat.id == ADMIN_ID:
        try:
            movie_name = message.text.split(maxsplit=1)[1]
            db.table("movies").insert({"name": movie_name}).execute()
            bot.reply_to(message, f"🎬 تم رفع الفيلم: {movie_name}")
        except:
            bot.reply_to(message, "⚠️ لازم تكتب اسم الفيلم بعد الأمر.")

@bot.message_handler(func=lambda message: True)
def ai_logic(message):
    if message.chat.id == ADMIN_ID:
        try:
            response = gemini_model.generate_content(message.text)
            bot.reply_to(message, response.text)
        except:
            try:
                chat_completion = client_groq.chat.completions.create(
                    messages=[{"role": "user", "content": message.text}],
                    model="mixtral-8x7b-32768",
                )
                bot.reply_to(message, chat_completion.choices[0].message.content)
            except:
                bot.reply_to(message, "🛠 السيرفرات مشغولة، حاول لاحقاً.")

# --- واجهة ويب FastAPI ---
app = FastAPI()

@app.get("/")
def home():
    return {"status": "Bot + Web Service running!"}

@app.get("/movies")
def list_movies():
    data = db.table("movies").select("*").execute()
    return {"movies": data.data}

# --- تشغيل البوت + السيرفر مع بعض ---
def run_bot():
    bot.polling()

if __name__ == "__main__":
    threading.Thread(target=run_bot).start()
    uvicorn.run(app, host="0.0.0.0", port=10000)
