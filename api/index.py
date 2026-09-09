import os
import json
import urllib.request
from http.server import BaseHTTPRequestHandler


def send_message(chat_id, text):
    token = os.environ["BOT_TOKEN"]
    url = f"https://api.telegram.org/bot{token}/sendMessage"

    data = json.dumps({
        "chat_id": chat_id,
        "text": text
    }).encode("utf-8")

    request = urllib.request.Request(
        url,
        data=data,
        headers={"Content-Type": "application/json"},
        method="POST"
    )

    urllib.request.urlopen(request, timeout=10)


class handler(BaseHTTPRequestHandler):

    def do_GET(self):
        self.send_response(200)
        self.send_header("Content-Type", "text/plain; charset=utf-8")
        self.end_headers()
        self.wfile.write(b"Bot is running")

    def do_POST(self):
        length = int(self.headers.get("Content-Length", 0))
        body = self.rfile.read(length)

        try:
            update = json.loads(body)

            message = update.get("message", {})
            chat = message.get("chat", {})
            text = message.get("text", "")
            chat_id = chat.get("id")

            if not chat_id:
                self.send_response(200)
                self.end_headers()
                return

            if text == "/start":
                reply = (
                    "سڵاو 👋\n\n"
                    "بەخێربێیت بۆ سیستەمی زانیاری گشتی 🔎\n\n"
                    "لە خوارەوە دەتوانیت هەڵبژێریت:\n\n"
                    "🔎 گەڕان\n"
                    "📊 ڕاپۆرت\n"
                    "ℹ️ زانیاری"
                )

                send_message(chat_id, reply)

            elif text == "/search":
                send_message(
                    chat_id,
                    "🔎 ناوی بەکارهێنەر یان داتای گشتی بنێرە."
                )

            elif text == "/report":
                send_message(
                    chat_id,
                    "📊 ڕاپۆرتی زانیاری گشتی لێرە دروست دەکرێت."
                )

            elif text == "/info":
                send_message(
                    chat_id,
                    "ℹ️ ئەم بۆتە تەنها داتای گشتی و ڕێگەپێدراو بەکاردێنێت."
                )

            else:
                send_message(
                    chat_id,
                    "تکایە یەکێک لەم فرمانانە بەکاربهێنە:\n"
                    "/start\n"
                    "/search\n"
                    "/report\n"
                    "/info"
                )

        except Exception:
            pass

        self.send_response(200)
        self.send_header("Content-Type", "text/plain")
        self.end_headers()
        self.wfile.write(b"OK")
