import telebot
from PIL import Image
import pillow_heif
import io
import threading
import tempfile
import os
from flask import Flask, request

TOKEN = os.getenv('BOT_TOKEN', '8532347560:AAGo9-dqbE_RS_UWuZMw3Ne8pC_9IbeGwjo')
bot = telebot.TeleBot(TOKEN)
app = Flask(__name__)

user_files = {}
user_timers = {}
WAIT_TIME = 5

def send_pdf(user_id, chat_id):
    if user_id not in user_files or not user_files[user_id]:
        return
    try:
        images = user_files[user_id]
        pdf_output = io.BytesIO()
        images[0].save(pdf_output, format='PDF', save_all=True, append_images=images[1:])
        pdf_output.seek(0)

        tmp = tempfile.NamedTemporaryFile(delete=False, suffix=".pdf")
        tmp_path = tmp.name
        try:
            tmp.write(pdf_output.read())
            tmp.flush()
            tmp.close()

            with open(tmp_path, "rb") as f:
                bot.send_document(chat_id, f, caption="PDF tayyor!")

        finally:
            if os.path.exists(tmp_path):
                try:
                    os.remove(tmp_path)
                except Exception:
                    pass

        user_files[user_id] = []

    except Exception as e:
        bot.send_message(chat_id, f"Xatolik: {e}")

def start_timer(user_id, chat_id):
    if user_id in user_timers:
        try:
            user_timers[user_id].cancel()
        except Exception:
            pass

    timer = threading.Timer(WAIT_TIME, send_pdf, args=(user_id, chat_id))
    user_timers[user_id] = timer
    timer.start()

@bot.message_handler(commands=['start'])
def handle_start(message):
    bot.send_message(message.chat.id, "Rasm yuboring, PDF qilib beraman!")

@bot.message_handler(content_types=['photo', 'document'])
def handle_file(message):
    user_id = message.from_user.id
    if user_id not in user_files:
        user_files[user_id] = []

    try:
        if message.content_type == 'photo':
            file_info = bot.get_file(message.photo[-1].file_id)
        elif message.content_type == 'document':
            if message.document.mime_type.lower() not in ['image/jpeg', 'image/jpg', 'image/heic']:
                bot.reply_to(message, "JPG, JPEG yoki HEIC format kerak.")
                return
            file_info = bot.get_file(message.document.file_id)
        else:
            bot.reply_to(message, "Rasm yuboring.")
            return

        downloaded_file = bot.download_file(file_info.file_path)

        if file_info.file_path.lower().endswith('.heic') or (message.content_type == 'document' and message.document.file_name and message.document.file_name.lower().endswith('.heic')):
            heif = pillow_heif.read_heif(io.BytesIO(downloaded_file))
            image = Image.frombytes(heif.mode, heif.size, heif.data, "raw")
        else:
            image = Image.open(io.BytesIO(downloaded_file))

        if image.mode in ("RGBA", "P"):
            image = image.convert("RGB")

        user_files[user_id].append(image)
        bot.reply_to(message, f"Rasm qo'shildi! {WAIT_TIME} soniyadan keyin PDF tayyor bo'ladi.")

        start_timer(user_id, message.chat.id)

    except Exception as e:
        bot.reply_to(message, f"Xatolik: {e}")

@app.route('/' + TOKEN, methods=['POST'])
def webhook():
    json_string = request.get_data().decode('utf-8')
    update = telebot.types.Update.de_json(json_string)
    bot.process_new_updates([update])
    return "OK"

@app.route('/')
def index():
    return "Bot ishlayapti!"

if __name__ == "__main__":
    # Webhook o'rnatish
    bot.remove_webhook()
    bot.set_webhook(url=f"https://your-railway-url.railway.app/{TOKEN}")
    
    # Flask serverni ishga tushirish
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)