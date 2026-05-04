import os
import subprocess
import telebot
from supabase import create_client
from groq import Groq

# سحب المفاتيح الأساسية
TOKEN = os.environ.get('TELEGRAM_TOKEN')
SUPABASE_URL = os.environ.get('SUPABASE_URL')
SUPABASE_KEY = os.environ.get('SUPABASE_KEY')
GROQ_KEY = os.environ.get('GROQ_API_KEY')

# مفاتيح المواقع الأخرى (اختياري - ضفها في ريندر لو احتجت)
CLOUDFLARE_API = os.environ.get('CLOUDFLARE_API')
HF_TOKEN = os.environ.get('HF_TOKEN') # Hugging Face

ADMIN_ID = 1071477484  # تأكد إنه الأي دي حقك

bot = telebot.TeleBot(TOKEN)
db = create_client(SUPABASE_URL, SUPABASE_KEY)
client_groq = Groq(api_key=GROQ_KEY)

@bot.message_handler(commands=['start'])
def welcome(message):
    if message.chat.id == ADMIN_ID:
        menu = (
            "🚀 **مرحباً بالقائد محمد الريمي**\n\n"
            "لوحة السيطرة جاهزة:\n"
            "🔹 `/install [اسم]` : لتثبيت مكتبات بايثون.\n"
            "🔹 `/exec [أمر]` : لتنفيذ أوامر Linux مباشرة (Bash).\n"
            "🔹 `/db` : لفحص مخزن سوباباس.\n"
            "🔹 أو أرسل أي سؤال وسيجيبك الذكاء الاصطناعي."
        )
        bot.reply_to(message, menu, parse_mode='Markdown')

# 1. ميزة تثبيت المكتبات (pip install)
@bot.message_handler(commands=['install'])
def install_lib(message):
    if message.chat.id == ADMIN_ID:
        try:
            lib = message.text.split(maxsplit=1)[1]
            bot.reply_to(message, f"⚙️ جاري تثبيت: {lib}")
            res = subprocess.run(f"pip install {lib}", shell=True, capture_output=True, text=True)
            bot.reply_to(message, f"✅ النتيجة:\n`{res.stdout[:1000]}`", parse_mode='Markdown')
        except: bot.reply_to(message, "⚠️ حدد اسم المكتبة.")

# 2. ميزة السيطرة الشاملة (Terminal Access)
# عبر هذا الأمر تقدر تتحكم في Cloudflare أو Hugging Face لو مثبت أدواتهم
@bot.message_handler(commands=['exec'])
def execute_command(message):
    if message.chat.id == ADMIN_ID:
        try:
            cmd = message.text.split(maxsplit=1)[1]
            bot.reply_to(message, f"💻 جاري تنفيذ الأمر: `{cmd}`", parse_mode='Markdown')
            res = subprocess.run(cmd, shell=True, capture_output=True, text=True)
            output = res.stdout if res.stdout else res.stderr
            bot.reply_to(message, f"📤 النتيجة:\n`{output[:3000]}`", parse_mode='Markdown')
        except Exception as e:
            bot.reply_to(message, f"❌ خطأ تنفيذ: {str(e)}")

# 3. محرك الذكاء الاصطناعي للرد الشامل
@bot.message_handler(func=lambda message: True)
def ai_logic(message):
    if message.chat.id == ADMIN_ID:
        try:
            chat_completion = client_groq.chat.completions.create(
                messages=[{"role": "user", "content": message.text}],
                model="mixtral-8x7b-32768",
            )
            bot.reply_to(message, chat_completion.choices[0].message.content)
        except Exception as e:
            bot.reply_to(message, "🛠 السيرفر مشغول، جرب لاحقاً.")

print("🔥 لوحة تحكم الريمي قيد التشغيل...")
bot.polling()
