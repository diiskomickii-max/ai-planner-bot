import os
import time
import requests
from http.server import HTTPServer, BaseHTTPRequestHandler
from threading import Thread

TOKEN = os.environ.get("TOKEN", "8814274957:AAHXP4H_2pVRZvwdxWUeTctfTtCM0GDiAZo")
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY", "AQ.Ab8RN6LYi-J1ae2taXpuYHFf3RyGoEdxYfvSeFnH5SNNuElZSg")
# Используем модель gemini-pro, которая стабильнее работает с регионами
GEMINI_URL = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-pro:generateContent?key={GEMINI_API_KEY}"

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
    headers = {'Content-Type': 'application/json'}
    data = {
        "contents": [{
            "parts": [{"text": f"Ты — умный ИИ-помощник для классификации записей. Определи категорию (Встреча, Задача, Расход, Еда, Мысль) и структурируй текст: {text}"}]
        }]
    }
    try:
        response = requests.post(GEMINI_URL, headers=headers, json=data)
        res_json = response.json()
        
        # Безопасная проверка ответа на наличие ошибок
        if "error" in res_json:
            return f"Ошибка API Google: {res_json['error'].get('message', 'Неизвестная ошибка')}"
            
        return res_json['candidates'][0]['content']['parts'][0]['text']
    except Exception as e:
        return f"Ошибка соединения с ИИ: {e}"

def run_telegram_bot():
    offset = 0
    print("Бот запущен...")
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
                        
                        if user_text.startswith("/start"):
                            reply = "Привет! Я твой умный планировщик. Напиши задачу или расход, и я разложу всё по полочкам!"
                        else:
                            reply = ask_gemini(user_text)
                        
                        send_url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
                        requests.post(send_url, json={"chat_id": chat_id, "text": reply, "parse_mode": "Markdown"})
        except Exception as e:
            print(f"Ошибка оглавления Telegram: {e}")
            time.sleep(5)

if __name__ == "__main__":
    server_thread = Thread(target=run_web_server, daemon=True)
    server_thread.start()
    run_telegram_bot()
