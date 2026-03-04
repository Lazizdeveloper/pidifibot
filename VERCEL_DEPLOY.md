# Vercel Deploy Guide

## 1. Vercel project yaratish
1. `https://vercel.com/new` ga kiring.
2. GitHub repository sifatida `pidifi` ni tanlang.
3. Framework auto-detect bo'lmasa ham muammo emas (Python serverless function ishlatiladi).

## 2. Environment Variables
Vercel dashboard -> Settings -> Environment Variables:
- `BOT_TOKEN` = Telegram bot token
- `WEBHOOK_SECRET` = ixtiyoriy xavfsizlik token (masalan, uzun random string)

## 3. Deploy
1. `Deploy` bosing.
2. Deploydan keyin domen chiqadi: `https://<project>.vercel.app`

## 4. Telegram webhook o'rnatish
Webhook endpoint:
- `https://<project>.vercel.app/api/webhook`

Secret ishlatilsa:
```bash
https://api.telegram.org/bot<BOT_TOKEN>/setWebhook?url=https://<project>.vercel.app/api/webhook&secret_token=<WEBHOOK_SECRET>
```

Yoki lokaldan script:
```bash
set BOT_TOKEN=<BOT_TOKEN>
set WEBHOOK_URL=https://<project>.vercel.app/api/webhook
set WEBHOOK_SECRET=<WEBHOOK_SECRET>
python set_webhook.py
```

## 5. Health check
- `https://<project>.vercel.app/api/webhook` (GET) -> JSON `ok: true`

## Eslatma
- Bu serverless varianti har yuborilgan rasmni alohida PDF qilib qaytaradi.
- Ko'p rasmni bitta PDF qilish uchun tashqi storage/queue (masalan Redis + background worker) kerak bo'ladi.
