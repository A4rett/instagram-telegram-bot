import os
import json
import urllib.request
from http.server import BaseHTTPRequestHandler


class handler(BaseHTTPRequestHandler):

    def do_GET(self):
        self.send_response(200)
        self.send_header("Content-Type", "text/plain")
        self.end_headers()
        self.wfile.write(b"Telegram bot is running")

    def do_POST(self):
        length = int(self.headers.get("Content-Length", 0))
        body = self.rfile.read(length)

        try:
            update = json.loads(body)
            message = update.get("message", {})
            chat = message.get("chat", {})
            text = message.get("text", "")

            chat_id = chat.get("id")

            if chat_id and text:
                if text == "/start":
                    reply = "سڵاو 👋\nبۆتەکە بە سەرکەوتوویی کار دەکات!"
                else:
                    reply = "نامەکەت گەیشت ✅"

                token = os.environ["BOT_TOKEN"]

                url = f"https://api.telegram.org/bot{token}/sendMessage"

                data = json.dumps({
                    "chat_id": chat_id,
                    "text": reply
                }).encode("utf-8")

                request = urllib.request.Request(
                    url,
                    data=data,
                    headers={"Content-Type": "application/json"},
                    method="POST"
                )

                urllib.request.urlopen(request, timeout=10)

            self.send_response(200)
            self.send_header("Content-Type", "text/plain")
            self.end_headers()
            self.wfile.write(b"OK")

        except Exception as e:
            self.send_response(200)
            self.send_header("Content-Type", "text/plain")
            self.end_headers()
            self.wfile.write(b"OK")
