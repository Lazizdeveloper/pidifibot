import io
import os

import pillow_heif
import requests
from flask import Flask, jsonify, request
from PIL import Image

app = Flask(__name__)

BOT_TOKEN = (os.getenv("BOT_TOKEN") or "").strip()
WEBHOOK_SECRET = os.getenv("WEBHOOK_SECRET")
TELEGRAM_API = f"https://api.telegram.org/bot{BOT_TOKEN}" if BOT_TOKEN else None
TELEGRAM_FILE_API = f"https://api.telegram.org/file/bot{BOT_TOKEN}" if BOT_TOKEN else None

ALLOWED_MIME_TYPES = {"image/jpeg", "image/jpg", "image/heic", "image/heif"}
ALLOWED_EXTENSIONS = (".jpg", ".jpeg", ".heic", ".heif")


def telegram_request(method: str, payload: dict | None = None, files: dict | None = None) -> dict:
    if not TELEGRAM_API:
        raise RuntimeError("BOT_TOKEN is not configured")

    response = requests.post(
        f"{TELEGRAM_API}/{method}",
        data=payload or {},
        files=files,
        timeout=30,
    )
    response.raise_for_status()
    body = response.json()
    if not body.get("ok"):
        raise RuntimeError(body.get("description", "Telegram API error"))
    return body.get("result", {})


def send_message(chat_id: int, text: str) -> None:
    telegram_request("sendMessage", {"chat_id": chat_id, "text": text})


def send_pdf_document(chat_id: int, pdf_bytes: bytes) -> None:
    files = {"document": ("converted.pdf", pdf_bytes, "application/pdf")}
    payload = {"chat_id": chat_id, "caption": "PDF tayyor!"}
    telegram_request("sendDocument", payload, files=files)


def is_heic(file_path: str, mime_type: str, file_name: str) -> bool:
    file_path = (file_path or "").lower()
    mime_type = (mime_type or "").lower()
    file_name = (file_name or "").lower()

    return (
        file_path.endswith((".heic", ".heif"))
        or mime_type in {"image/heic", "image/heif"}
        or file_name.endswith((".heic", ".heif"))
    )


def download_telegram_file(file_id: str) -> tuple[bytes, str]:
    file_info = telegram_request("getFile", {"file_id": file_id})
    file_path = file_info.get("file_path")
    if not file_path:
        raise RuntimeError("Telegram file path was not returned")

    download = requests.get(f"{TELEGRAM_FILE_API}/{file_path}", timeout=30)
    download.raise_for_status()
    return download.content, file_path


def convert_image_to_pdf(file_bytes: bytes, treat_as_heic: bool) -> bytes:
    if treat_as_heic:
        heif_file = pillow_heif.read_heif(io.BytesIO(file_bytes))
        image = Image.frombytes(heif_file.mode, heif_file.size, heif_file.data, "raw")
    else:
        image = Image.open(io.BytesIO(file_bytes))
        image.load()

    if image.mode != "RGB":
        image = image.convert("RGB")

    output = io.BytesIO()
    image.save(output, format="PDF")
    output.seek(0)
    return output.read()


def process_message(message: dict) -> None:
    chat = message.get("chat", {})
    chat_id = chat.get("id")
    if not chat_id:
        return

    text = (message.get("text") or "").strip()
    if text.startswith("/start"):
        send_message(chat_id, "Rasm yuboring, PDF qilib beraman!")
        return

    file_id = None
    mime_type = ""
    file_name = ""

    photos = message.get("photo") or []
    if photos:
        file_id = photos[-1].get("file_id")
    else:
        document = message.get("document") or {}
        mime_type = (document.get("mime_type") or "").lower()
        file_name = document.get("file_name") or ""
        if document:
            if mime_type and mime_type not in ALLOWED_MIME_TYPES and not file_name.lower().endswith(ALLOWED_EXTENSIONS):
                send_message(chat_id, "JPG, JPEG yoki HEIC format kerak.")
                return
            file_id = document.get("file_id")

    if not file_id:
        send_message(chat_id, "Rasm yuboring (JPG/JPEG/HEIC), men PDF qilib yuboraman.")
        return

    file_bytes, file_path = download_telegram_file(file_id)
    pdf_bytes = convert_image_to_pdf(file_bytes, is_heic(file_path, mime_type, file_name))
    send_pdf_document(chat_id, pdf_bytes)


def process_update(update: dict) -> None:
    message = update.get("message") or update.get("edited_message")
    if message:
        process_message(message)


@app.route("/", methods=["GET"])
def healthcheck():
    if not BOT_TOKEN:
        return jsonify({"ok": False, "error": "BOT_TOKEN is missing"}), 500
    return jsonify({"ok": True, "service": "ozbot-webhook"})


@app.route("/", methods=["POST"])
def webhook():
    if not BOT_TOKEN:
        return jsonify({"ok": False, "error": "BOT_TOKEN is missing"}), 500

    if WEBHOOK_SECRET:
        secret_from_header = request.headers.get("X-Telegram-Bot-Api-Secret-Token", "")
        if secret_from_header != WEBHOOK_SECRET:
            return jsonify({"ok": False, "error": "Invalid webhook secret"}), 401

    update = request.get_json(silent=True)
    if not isinstance(update, dict):
        return jsonify({"ok": False, "error": "Invalid JSON payload"}), 400

    try:
        process_update(update)
    except Exception as exc:
        return jsonify({"ok": False, "error": str(exc)}), 500

    return jsonify({"ok": True})
