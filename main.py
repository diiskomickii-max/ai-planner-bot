import asyncio
import logging
import os
from http.server import HTTPServer, BaseHTTPRequestHandler
from threading import Thread
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import CommandStart
import google.generativeai as genai

TOKEN = "8814274957:AAHXP4H_2pVRZvwdxWUeTctfTtCM0GDiAZo"
GEMINI_API_KEY = "AQ.Ab8RN6LYi-J1ae2taXpuYHFf3RyGoEdxYfvSeFnH5SNNuElZSg"

genai.configure(api_key=GEMINI_API_KEY)
model = genai.GenerativeModel('gemini-3.8-flash')

logging.basicConfig(level=logging.INFO)
bot = Bot(token=TOKEN)
dp = Dispatcher()

# Заглушка веб-сервера, чтобы Render (Free tier) думал, что это сайт и не отключал его
class SimpleHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.end_headers()
        self.wfile.write(b"Bot is running!")

def run_web_server():
    port = int(os.environ.get("PORT", 10000))
    server = HTTPServer(('0.0.0.0', port), SimpleHandler)
    server.serve_forever()

@dp.message(CommandStart())
async def cmd_start(message: types.Message):
    await message.answer(
        "Привет! Я твой умный планировщик (аналог GX Planner).\n"
        "Просто напиши мне текстовое сообщение или отправь мысль, задачу, расход или запись о еде, "
        "а я автоматически разложу всё по полочкам!"
    )

@dp.message(F.text)
async def process_thought(message: types.Message):
    user_text = message.text
    prompt = (
        "Ты — умный ИИ-помощник для классификации записей в дневнике/планировщике. "
        "Проанализируй текст пользователя и определи категорию (Встреча, Задача, Расход, Еда, Мысль). "
        "Выдай ответ в удобном структурированном виде на русском языке.\n\n"
        f"Текст пользователя: {user_text}"
    )
    try:
        response = model.generate_content(prompt)
        ai_reply = response.text
        await message.answer(f"📥 **Разобрано нейросетью:**\n\n{ai_reply}")
    except Exception as e:
        await message.answer(f"Ошибка при обращении к ИИ: {e}")

async def main():
    # Запускаем веб-сервер в отдельном потоке для Render
    server_thread = Thread(target=run_web_server, daemon=True)
    server_thread.start()
    
    print("Бот запущен и готов к работе...")
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())