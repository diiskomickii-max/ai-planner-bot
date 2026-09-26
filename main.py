import asyncio
import logging
import os
from http.server import HTTPServer, BaseHTTPRequestHandler
from threading import Thread
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import CommandStart
import google.generativeai as genai

TOKEN = os.environ.get("TOKEN", "8814274957:AAHXP4H_2pVRZvwdxWUeTctfTtCM0GDiAZo")
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY", "AQ.Ab8RN6LYi-J1ae2taXpuYHFf3RyGoEdxYfvSeFnH5SNNuElZSg")

genai.configure(api_key=GEMINI_API_KEY)
model = genai.GenerativeModel('gemini-1.5-flash')

logging.basicConfig(level=logging.INFO)
bot = Bot(token=TOKEN)
dp = Dispatcher()

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
        "Привет! Я твой умный планировщик.\n"
        "Отправь мне задачу, мысль или расход, и я разложу всё по полочкам!"
    )

@dp.message(F.text)
async def process_thought(message: types.Message):
    user_text = message.text
    prompt = (
        "Ты — умный ИИ-помощник для классификации записей. "
        "Проанализируй текст и определи категорию (Встреча, Задача, Расход, Еда, Мысль). "
        "Выдай ответ в удобном структурированном виде на русском языке.\n\n"
        f"Текст: {user_text}"
    )
    try:
        response = model.generate_content(prompt)
        await message.answer(f"📥 **Результат:**\n\n{response.text}")
    except Exception as e:
        await message.answer(f"Ошибка: {e}")

async def main():
    server_thread = Thread(target=run_web_server, daemon=True)
    server_thread.start()
    
    print("Бот запущен...")
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
