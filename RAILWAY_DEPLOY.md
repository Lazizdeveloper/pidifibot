# Railway Deploy Guide

## 1. Railway.app ga kirish
1. [Railway.app](https://railway.app) ga kiring
2. GitHub akkauntingiz bilan login qiling

## 2. Yangi loyiha yaratish
1. "New Project" tugmasini bosing
2. "Deploy from GitHub repo" ni tanlang
3. Bu repository ni tanlang (ozbot)

## 3. Environment Variables o'rnatish
Railway dashboard da:
1. "Variables" tab ga o'ting
2. Quyidagi environment variable ni qo'shing:
   - `BOT_TOKEN` = sizning bot tokeningiz (8532347560:AAGo9-dqbE_RS_UWuZMw3Ne8pC_9IbeGwjo)

## 4. Deploy qilish
1. Railway avtomatik deploy qiladi
2. Deploy tugagach, sizga URL beriladi (masalan: `https://ozbot-production.up.railway.app`)

## 5. Webhook o'rnatish
Deploy tugagach:
1. Railway URL ni oling
2. Bot avtomatik webhook o'rnatishga harakat qiladi
3. Agar ishlamasa, qo'lda o'rnating:
   ```
   https://api.telegram.org/bot<BOT_TOKEN>/setWebhook?url=https://your-railway-url.railway.app/<BOT_TOKEN>
   ```

## 6. Test qilish
1. Telegram da botingizga `/start` yuboring
2. Rasm yuboring va PDF olishni sinab ko'ring

## Muhim eslatmalar:
- Bot webhook rejimida ishlaydi (polling emas)
- Railway bepul plan 500 soat/oy beradi
- Agar xatolik bo'lsa, Railway logs ni tekshiring