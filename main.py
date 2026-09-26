import os
import time
import requests
from http.server import HTTPServer, BaseHTTPRequestHandler
from threading import Thread
from google import genai

TOKEN = os.environ.get("TOKEN", "8814274957:AAEtuSWcBc2IxnvbUjX8TESDNTtGVNri0")
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY", "AQ.Ab8RN6K_c9z6XFpKjJF7rAU5MRxFCXizom1FKRY5kwxQ9aloA")

client = genai.Client(api_key=GEMINI_API_KEY)

class SimpleHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.end_headers()
        self.wfile.write(b"Bot is running!")

def run_web_server():
    port = int(os.environ.get("PORT", 10000))
    server = HTTPServer(('0.0.0.0', port), SimpleHandler)
    server.serve_forever()

def ask_gemini(text):
    print(f"Отправка запроса в Gemini: {text}")
    prompt = f"Ты — умный ИИ-помощник для классификации записей. Определи категорию (Встреча, Задача, Расход, Еда, Мысль) и структурируй текст:\n\n{text}"
    try:
        response = client.models.generate_content(
            model="gemini-1.5-flash",
            contents=prompt,
        )
        print("Ответ от Gemini получен успешно.")
        return response.text
    except Exception as e:
        print(f"Ошибка Gemini API: {e}")
        return f"Ошибка ИИ: {e}"

def run_telegram_bot():
    offset = 0
    print("Telegram бот запущен и слушает обновления...")
    while True:
        try:
            url = f"https://api.telegram.org/bot{TOKEN}/getUpdates?offset={offset}&timeout=30"
            response = requests.get(url, timeout=35)
            data = response.json()
            
            if data.get("ok"):
                for update in data.get("result", []):
                    offset = update["update_id"] + 1
                    message = update.get("message")
                    if message and "text" in message:
                        chat_id = message["chat"]["id"]
                        user_text = message["text"]
                        print(f"Получено сообщение от chatId {chat_id}: {user_text}")
                        
                        if user_text.startswith("/start"):
                            reply = "Привет! Я твой умный планировщик. Напиши задачу или расход, и я разложу всё по полочкам!"
                        else:
                            reply = ask_gemini(user_text)
                        
                        send_url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
                        res = requests.post(send_url, json={"chat_id": chat_id, "text": reply, "parse_mode": "Markdown"})
                        print(f"Статус отправки в Telegram: {res.status_code}")
        except Exception as e:
            print(f"Ошибка в цикле Telegram: {e}")
            time.sleep(5)

if __name__ == "__main__":
    server_thread = Thread(target=run_web_server, daemon=True)
    server_thread.start()
    run_telegram_bot()
