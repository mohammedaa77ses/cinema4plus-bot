import os
from telegram.ext import Updater, CommandHandler
from supabase import create_client, Client

# قراءة المفاتيح من البيئة (env)
BOT_TOKEN = os.getenv("BOT_TOKEN")
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

# أمر البداية
def start(update, context):
    update.message.reply_text("أهلاً ياوحش 👊 البوت شغال!")

# إعداد البوت
def main():
    updater = Updater(BOT_TOKEN, use_context=True)
    dp = updater.dispatcher

    dp.add_handler(CommandHandler("start", start))

    updater.start_polling()
    updater.idle()

if __name__ == "__main__":
    main()
