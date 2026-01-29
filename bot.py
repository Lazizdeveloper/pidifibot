import telebot
from PIL import Image
import pillow_heif
import io
import threading
import tempfile
import os

TOKEN = os.getenv('BOT_TOKEN', '8532347560:AAGo9-dqbE_RS_UWuZMw3Ne8pC_9IbeGwjo')
bot = telebot.TeleBot(TOKEN)

@bot.message_handler(commands=['start'])
def handle_start(message):
    bot.send_message(message.chat.id, "Отправь файл, чтобы я конвертировал его в PDF")

user_files = {}      # Хранение изображений пользователей
user_timers = {}     # Таймеры для автоматической конвертации

WAIT_TIME = 5  # секунд после последнего файла

def send_pdf(user_id, chat_id):
    if user_id not in user_files or not user_files[user_id]:
        return
    try:
        images = user_files[user_id]
        pdf_output = io.BytesIO()
        images[0].save(pdf_output, format='PDF', save_all=True, append_images=images[1:])
        pdf_output.seek(0)

        # Создаём временный файл с расширением .pdf
        tmp = tempfile.NamedTemporaryFile(delete=False, suffix=".pdf")
        tmp_path = tmp.name
        try:
            # Записываем содержимое BytesIO в файл
            tmp.write(pdf_output.read())
            tmp.flush()
            tmp.close()

            # Открываем файл в бинарном режиме и отправляем — Telegram увидит имя и расширение
            with open(tmp_path, "rb") as f:
                # подпись (caption) можно убрать или изменить
                bot.send_document(chat_id, f, caption="skd_adm @pidifibot")

        finally:
            # Удаляем временный файл
            if os.path.exists(tmp_path):
                try:
                    os.remove(tmp_path)
                except Exception:
                    pass

        # Очищаем список пользователя
        user_files[user_id] = []

    except Exception as e:
        bot.send_message(chat_id, f"Ошибка при создании PDF: {e}")

def start_timer(user_id, chat_id):
    # Отменяем предыдущий таймер
    if user_id in user_timers:
        try:
            user_timers[user_id].cancel()
        except Exception:
            pass

    # Новый таймер
    timer = threading.Timer(WAIT_TIME, send_pdf, args=(user_id, chat_id))
    user_timers[user_id] = timer
    timer.start()

@bot.message_handler(content_types=['photo', 'document'])
def handle_file(message):
    user_id = message.from_user.id
    if user_id not in user_files:
        user_files[user_id] = []

    try:
        # Получаем файл
        if message.content_type == 'photo':
            file_info = bot.get_file(message.photo[-1].file_id)
        elif message.content_type == 'document':
            if message.document.mime_type.lower() not in ['image/jpeg', 'image/jpg', 'image/heic']:
                bot.reply_to(message, "Нужен формат JPG, JPEG или HEIC.")
                return
            file_info = bot.get_file(message.document.file_id)
        else:
            bot.reply_to(message, "Отправьте фото или документ в формате JPG/JPEG/HEIC.")
            return

        downloaded_file = bot.download_file(file_info.file_path)

        # Конвертация HEIC
        if file_info.file_path.lower().endswith('.heic') or (message.content_type == 'document' and message.document.file_name and message.document.file_name.lower().endswith('.heic')):
            heif = pillow_heif.read_heif(io.BytesIO(downloaded_file))
            image = Image.frombytes(heif.mode, heif.size, heif.data, "raw")
        else:
            image = Image.open(io.BytesIO(downloaded_file))

        if image.mode in ("RGBA", "P"):
            image = image.convert("RGB")

        user_files[user_id].append(image)
        bot.reply_to(message, f"Файл добавлен! PDF будет готов через {WAIT_TIME} секунд после последнего файла.")

        start_timer(user_id, message.chat.id)

    except Exception as e:
        bot.reply_to(message, f"Ошибка: {e}")

bot.infinity_polling()

