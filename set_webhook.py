#!/usr/bin/env python3
"""
Telegram webhook o'rnatish uchun universal script.

Priority:
1) WEBHOOK_URL (full URL)
2) VERCEL_URL (domain only)
3) RAILWAY_STATIC_URL (domain only)
"""

import os

import requests


def resolve_webhook_url() -> str:
    explicit = (os.getenv("WEBHOOK_URL") or "").strip()
    if explicit:
        return explicit

    vercel_url = (os.getenv("VERCEL_URL") or "").strip()
    if vercel_url:
        if not vercel_url.startswith("http"):
            vercel_url = f"https://{vercel_url}"
        return f"{vercel_url.rstrip('/')}/api/webhook"

    railway_url = (os.getenv("RAILWAY_STATIC_URL") or "").strip()
    if railway_url:
        if not railway_url.startswith("http"):
            railway_url = f"https://{railway_url}"
        bot_token = (os.getenv("BOT_TOKEN") or "").strip()
        return f"{railway_url.rstrip('/')}/{bot_token}"

    manual = input("Webhook URL kiriting (example: https://your-app.vercel.app/api/webhook): ").strip()
    return manual


def set_webhook() -> None:
    bot_token = (os.getenv("BOT_TOKEN") or "").strip()
    webhook_secret = (os.getenv("WEBHOOK_SECRET") or "").strip()
    if not bot_token:
        print("BOT_TOKEN environment variable kerak.")
        return

    webhook_url = resolve_webhook_url()
    if not webhook_url:
        print("Webhook URL topilmadi.")
        return

    api_url = f"https://api.telegram.org/bot{bot_token}/setWebhook"
    payload = {"url": webhook_url}
    if webhook_secret:
        payload["secret_token"] = webhook_secret

    print(f"Webhook ornatilmoqda: {webhook_url}")
    response = requests.post(api_url, json=payload, timeout=30)
    if response.status_code != 200:
        print(f"HTTP xatolik: {response.status_code}")
        print(response.text)
        return

    result = response.json()
    if result.get("ok"):
        print("Webhook muvaffaqiyatli ornatildi.")
    else:
        print(f"Xatolik: {result.get('description')}")


if __name__ == "__main__":
    set_webhook()
