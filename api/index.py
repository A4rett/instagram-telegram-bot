import os
import json
import urllib.request
from http.server import BaseHTTPRequestHandler


def send_message(chat_id, text, keyboard=None):
    token = os.environ["BOT_TOKEN"]
    url = f"https://api.telegram.org/bot{token}/sendMessage"

    data = {
        "chat_id": chat_id,
        "text": text
    }

    if keyboard:
        data["reply_markup"] = keyboard

    request = urllib.request.Request(
        url,
        data=json.dumps(data).encode("utf-8"),
        headers={"Content-Type": "application/json"},
        method="POST"
    )

    urllib.request.urlopen(request, timeout=10)


def answer_callback(callback_id):
    token = os.environ["BOT_TOKEN"]
    url = f"https://api.telegram.org/bot{token}/answerCallbackQuery"

    data = json.dumps({
        "callback_query_id": callback_id
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
        self.send_header(
            "Content-Type",
            "text/plain; charset=utf-8"
        )
        self.end_headers()
        self.wfile.write(b"Bot is running")

    def do_POST(self):
        length = int(
            self.headers.get("Content-Length", 0)
        )
        body = self.rfile.read(length)

        try:
            update = json.loads(body)

            # =========================
            # Callback buttons
            # =========================

            callback = update.get("callback_query")

            if callback:
                callback_id = callback.get("id")
                callback_data = callback.get("data")

                callback_message = callback.get(
                    "message", {}
                )

                callback_chat = callback_message.get(
                    "chat", {}
                )

                callback_chat_id = callback_chat.get(
                    "id"
                )

                if callback_id:
                    answer_callback(callback_id)

                if callback_chat_id:

                    if callback_data == "search":
                        send_message(
                            callback_chat_id,
                            "🔎 تکایە Username ـەکە بنێرە."
                        )

                    elif callback_data == "location":
                        send_message(
                            callback_chat_id,
                            "📍 تکایە ناوی شار یان شوێنێکی گشتی بنێرە."
                        )

                    elif callback_data == "report":
                        send_message(
                            callback_chat_id,
                            "📊 ڕاپۆرتی زانیاری گشتی لێرە دروست دەکرێت."
                        )

                    elif callback_data == "info":
                        send_message(
                            callback_chat_id,
                            "ℹ️ ئەم بۆتە تەنها داتای گشتی و ڕێگەپێدراو بەکاردێنێت."
                        )

                self.send_response(200)
                self.end_headers()
                self.wfile.write(b"OK")
                return

            # =========================
            # Normal messages
            # =========================

            message = update.get("message", {})

            chat = message.get("chat", {})

            text = message.get("text", "").strip()

            chat_id = chat.get("id")

            if not chat_id:
                self.send_response(200)
                self.end_headers()
                return

            # =========================
            # START
            # =========================

            if text == "/start":

                keyboard = {
                    "inline_keyboard": [
                        [
                            {
                                "text": "🔎 گەڕانی Username",
                                "callback_data": "search"
                            },
                            {
                                "text": "📍 گەڕانی شوێن",
                                "callback_data": "location"
                            }
                        ],
                        [
                            {
                                "text": "📊 ڕاپۆرت",
                                "callback_data": "report"
                            },
                            {
                                "text": "ℹ️ زانیاری",
                                "callback_data": "info"
                            }
                        ]
                    ]
                }

                send_message(
                    chat_id,
                    "سڵاو 👋\n\n"
                    "بەخێربێیت بۆ بۆتی زانیاری گشتی 🔎\n\n"
                    "لە مێنیوەکەوە هەڵبژێرە:",
                    keyboard
                )

            # =========================
            # SEARCH COMMAND
            # =========================

            elif text == "/search":

                send_message(
                    chat_id,
                    "🔎 تکایە Username ـەکە بنێرە."
                )

            # =========================
            # LOCATION
            # =========================

            elif text == "/location":

                send_message(
                    chat_id,
                    "📍 تکایە ناوی شار یان شوێنی گشتی بنێرە."
                )

            # =========================
            # REPORT
            # =========================

            elif text == "/report":

                send_message(
                    chat_id,
                    "📊 ڕاپۆرتی زانیاری گشتی لێرە دروست دەکرێت."
                )

            # =========================
            # INFO
            # =========================

            elif text == "/info":

                send_message(
                    chat_id,
                    "ℹ️ ئەم بۆتە تەنها داتای گشتی "
                    "و ڕێگەپێدراو بەکاردێنێت."
                )

            # =========================
            # USERNAME
            # =========================

            elif text:

                username = text.lstrip("@").strip()

                send_message(
                    chat_id,
                    f"🔎 Username ـەکە وەرگیرا:\n\n"
                    f"@{username}\n\n"
                    f"⏳ ئێستا پشکنینی داتای گشتی "
                    f"بۆ ئەم ناوە دەکرێت."
                )

            else:

                send_message(
                    chat_id,
                    "تکایە /start بنێرە."
                )

        except Exception:
            pass

        self.send_response(200)
        self.send_header(
            "Content-Type",
            "text/plain; charset=utf-8"
        )
        self.end_headers()
        self.wfile.write(b"OK")
