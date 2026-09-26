import os
import time
import requests
from http.server import HTTPServer, BaseHTTPRequestHandler
from threading import Thread

# Vashi toki i klyuchi
TOKEN = os.environ.get("TOKEN", "8814274957:AAEtuSWcBc2IxnvbUjX8TESDNTtGVNri0")
OPENROUTER_API_KEY = os.environ.get("OPENROUTER_API_KEY", "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")

class SimpleHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.end_headers()
        self.wfile.write(b"Bot is running!")

def run_web_server():
    port = int(os.environ.get("PORT", 10000))
    server = HTTPServer(('0.0.0.0', port), SimpleHandler)
    server.serve_forever()

def ask_ai(text):
    url = "https://openrouter.ai/api/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {OPENROUTER_API_KEY}",
        "Content-Type": "application/json"
    }
    data = {
        "model": "meta-llama/llama-3-8b-instruct:free",
        "messages": [
            {
                "role": "system",
                "content": "Ty — umnyy II-pomoshchnik dlya klassifikatsii zapisey. Opredeli kategoriyu (Vstrecha, Zadacha, Raskhod, Eda, Mysl) i strukturiruy tekst."
            },
            {
                "role": "user",
                "content": text
            }
        ]
    }
    try:
        response = requests.post(url, headers=headers, json=data, timeout=30)
        res_json = response.json()
        
        if "error" in res_json:
            return f" Oshibka API: {res_json['error'].get('message', 'Neizvestnaya oshibka')}"
            
        return res_json["choices"][0]["message"]["content"]
    except Exception as e:
        return f" Oshibka soedineniya: {e}"

def run_telegram_bot():
    offset = 0
    print("Bot cherez OpenRouter zapushen...")
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
                            reply = "Privet! Ya tvoy umnyy planirovshchik. Napishi zadachu ili raskhod, i ya razlozhu vsyo po polochkam!"
                        else:
                            reply = ask_ai(user_text)
                        
                        send_url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
                        requests.post(send_url, json={"chat_id": chat_id, "text": reply, "parse_mode": "Markdown"})
        except Exception as e:
            print(f"Oshibka Telegram: {e}")
            time.sleep(5)

if __name__ == "__main__":
    server_thread = Thread(target=run_web_server, daemon=True)
    server_thread.start()
    run_telegram_bot()
