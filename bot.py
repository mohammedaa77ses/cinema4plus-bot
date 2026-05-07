import os
import telebot
from supabase import create_client

# سحب البيانات من ريندر (اللي حطيناها في الـ Environment)
TOKEN = os.getenv('TELEGRAM_TOKEN')
SUPABASE_URL = os.getenv('SUPABASE_URL')
SUPABASE_KEY = os.getenv('SUPABASE_KEY')

bot = telebot.TeleBot(TOKEN)
supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

@bot.message_handler(commands=['start'])
def send_welcome(message):
    bot.reply_to(message, "يا هلا يا محمد! بوت Cinema For Plus شغال وقاعدة البيانات مربوطة ✅")

print("البوت بدأ العمل...")
bot.infinity_polling()
