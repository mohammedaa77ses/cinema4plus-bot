import os
import subprocess
import threading
import uvicorn
from fastapi import FastAPI
from supabase import create_client
import telebot
from groq import Groq
import google.generativeai as genai

# --- سحب المفاتيح من Render (Environment Variables) ---
TOKEN = os.environ.get("TELEGRAM_TOKEN")
SUPABASE_URL = os.environ.get("SUPABASE_URL")
SUPABASE_KEY = os.environ.get("SUPABASE_KEY")
GROQ_KEY = os.environ.get("GROQ_API_KEY")
GEMINI_KEY = os.environ.get("GEMINI_API_KEY")

# --- إعداد المحركات ---
bot = telebot.TeleBot(TOKEN)
db = create_client(SUPABASE_URL, SUPABASE_KEY)
client_groq = Groq(api_key=GROQ_KEY)

# إعداد Gemini
genai.configure(api_key=GEMINI_KEY)
gemini_model = genai.GenerativeModel("gemini-1.5-flash")

ADMIN_ID = 1071477484  # الأي دي الخاص بك

# --- أوامر تيليجرام ---

@bot.message_handler(commands=["start"])
def welcome(message):
    if message.chat.id == ADMIN_ID:
        bot.reply_to(message, "🚀 البوت شغال يا وحش! Cinema For Yemen جاهز.")

@bot.message_handler(commands=["install"])
def install_lib(message):
    if message.chat.id == ADMIN_ID:
        try:
            lib = message.text.split(maxsplit=1)[1]
            bot.reply_to(message, f"⏳ جاري تثبيت {lib}...")
            res = subprocess.run(f"pip install {lib}", shell=True, capture_output=True, text=True)
            output = res.stdout if res.stdout else res.stderr
            bot.reply_to(message, f"✅ النتيجة:\n{output[:500]}")
        except IndexError:
            bot.reply_to(message, "⚠️ يرجى كتابة اسم المكتبة بعد الأمر، مثال: /install requests")

@bot.message_handler(commands=["exec"])
def execute_command(message):
    if message.chat.id == ADMIN_ID:
        try:
            cmd = message.text.split(maxsplit=1)[1]
            res = subprocess.run(cmd, shell=True, capture_output=True, text=True)
            output = res.stdout if res.stdout else res.stderr
            bot.reply_to(message, f"📤 النتيجة:\n{output[:1000]}")
        except Exception as e:
            bot.reply_to(message, f"❌ خطأ في التنفيذ: {str(e)}")

@bot.message_handler(commands=["add"])
def add_movie(message):
    if message.chat.id == ADMIN_ID:
        try:
            movie_name = message.text.split(maxsplit=1)[1]
            # التأكد من الإضافة لجدول movies في Supabase
            response = db.table("movies").insert({"name": movie_name}).execute()
            bot.reply_to(message, f"🎬 تم بنجاح إضافة الفيلم: {movie_name}")
        except Exception as e:
            bot.reply_to(message, f"⚠️ خطأ أثناء الإضافة: {str(e)}")

@bot.message_handler(func=lambda message: True)
def ai_logic(message):
    if message.chat.id == ADMIN_ID:
        # المحاولة الأولى: Gemini
        try:
            response = gemini_model.generate_content(message.text)
            if response.text:
                bot.reply_to(message, response.text)
                return
        except Exception:
            pass # ننتقل لـ Groq في حال فشل Gemini
        
        # المحاولة الثانية: Groq
        try:
            chat_completion = client_groq.chat.completions.create(
                messages=[{"role": "user", "content": message.text}],
                model="mixtral-8x7b-32768",
            )
            bot.reply_to(message, chat_completion.choices[0].message.content)
        except Exception:
            bot.reply_to(message, "🛠 المعذرة، جميع المحركات (Gemini & Groq) مشغولة حالياً.")

# --- واجهة ويب FastAPI لضمان استمرار عمل الخدمة ---
app = FastAPI()

@app.get("/")
def home():
    return {"status": "Cinema For Yemen Service is Online"}

@app.get("/movies")
def list_movies():
    try:
        data = db.table("movies").select("*").execute()
        return {"movies": data.data}
    except Exception as e:
        return {"error": str(e)}

# --- دالة تشغيل البوت في Thread منفصل ---
def run_bot():
    print("🤖 Telegram Bot is starting...")
    bot.infinity_polling()

if __name__ == "__main__":
    # تشغيل البوت في الخلفية
    bot_thread = threading.Thread(target=run_bot)
    bot_thread.daemon = True
    bot_thread.start()
    
    # تشغيل سيرفر الويب (الذي يحتاجه Render)
    port = int(os.environ.get("PORT", 10000))
    print(f"🌐 FastAPI is running on port {port}")
    uvicorn.run(app, host="0.0.0.0", port=port)
