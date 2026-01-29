#!/usr/bin/env python3
"""
Railway deploy qilingandan keyin webhook o'rnatish uchun script
"""
import os
import requests

def set_webhook():
    bot_token = os.getenv('BOT_TOKEN')
    railway_url = os.getenv('RAILWAY_STATIC_URL')
    
    if not bot_token:
        print("BOT_TOKEN environment variable kerak!")
        return
    
    if not railway_url:
        print("RAILWAY_STATIC_URL environment variable kerak!")
        print("Yoki qo'lda URL kiriting:")
        railway_url = input("Railway URL (https://your-app.railway.app): ").strip()
        if not railway_url:
            return
    
    webhook_url = f"https://{railway_url}/{bot_token}"
    api_url = f"https://api.telegram.org/bot{bot_token}/setWebhook"
    
    print(f"Webhook o'rnatilmoqda: {webhook_url}")
    
    response = requests.post(api_url, json={'url': webhook_url})
    
    if response.status_code == 200:
        result = response.json()
        if result.get('ok'):
            print("✅ Webhook muvaffaqiyatli o'rnatildi!")
        else:
            print(f"❌ Xatolik: {result.get('description')}")
    else:
        print(f"❌ HTTP xatolik: {response.status_code}")

if __name__ == "__main__":
    set_webhook()