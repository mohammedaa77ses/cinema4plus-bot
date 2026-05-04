import os
import telebot
from supabase import create_client
from groq import Groq

# سحب المفاتيح من Render (الخزنة)
TOKEN = os.environ.get('TELEGRAM_TOKEN')
SUPABASE_URL = os.environ.get('SUPABASE_URL')
SUPABASE_KEY = os.environ.get('SUPABASE_KEY')
GROQ_KEY = os.environ.get('GROQ_API_KEY')

# إعداد البوت والقواعد
bot = telebot.TeleBot(TOKEN)
db = create_client(SUPABASE_URL, SUPABASE_KEY)
client_groq = Groq(api_key=GROQ_KEY)

@bot.message_handler(commands=['start'])
def send_welcome(message):
    bot.reply_to(message, "أهلاً بك في بوت سينما فور بلس! أنا المهندس الذكي، كيف أخدمك اليوم؟")

@bot.message_handler(func=lambda message: True)
def handle_ai(message):
    try:
        # رد الذكاء الاصطناعي السريع عبر Groq
        chat_completion = client_groq.chat.completions.create(
            messages=[{"role": "user", "content": message.text}],
            model="mixtral-8x7b-32768",
        )
        reply = chat_completion.choices[0].message.content
        bot.reply_to(message, reply)
    except Exception as e:
        print(f"Error: {e}")
        bot.reply_to(message, "جاري معالجة طلبك... يرجى المحاولة لاحقاً.")

print("البوت بدأ العمل بنجاح...")
bot.polling()
