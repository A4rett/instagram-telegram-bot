import os
import json
import urllib.request
from http.server import BaseHTTPRequestHandler
from urllib.parse import quote


BOT_TOKEN = os.environ.get("BOT_TOKEN")


def telegram(method, data):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/{method}"

    request = urllib.request.Request(
        url,
        data=json.dumps(data).encode("utf-8"),
        headers={"Content-Type": "application/json"},
        method="POST"
    )

    with urllib.request.urlopen(request, timeout=15) as response:
        return response.read()


def send_message(chat_id, text):
    telegram("sendMessage", {
        "chat_id": chat_id,
        "text": text,
        "disable_web_page_preview": True
    })


def public_profile(username):
    username = username.strip().lstrip("@")

    if not username:
        return "❌ Username ـەکە بەتاڵە."

    profile_url = (
        "https://www.instagram.com/"
        + quote(username, safe="")
        + "/"
    )

    return (
        "🔎 ڕاپۆرتی زانیاری گشتی\n\n"
        f"👤 Username: @{username}\n\n"
        f"🔗 Profile:\n{profile_url}\n\n"
        "🌐 سەرچاوە:\n"
        "Instagram public profile\n\n"
        "⚠️ تێبینی:\n"
        "ئەم بۆتە تەنها زانیارییە گشتییەکان "
        "پشکنین دەکات. داتای private، "
        "followers ـی شاراوە، password، token "
        "یان session بەدەست ناهێنێت."
    )


def menu():
    return {
        "inline_keyboard": [
            [
                {
                    "text": "🔎 Username",
                    "callback_data": "search"
                },
                {
                    "text": "📍 شوێن",
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


class handler(BaseHTTPRequestHandler):

    def do_GET(self):
        self.send_response(200)
        self.send_header(
            "Content-Type",
            "text/plain; charset=utf-8"
        )
        self.end_headers()
        self.wfile.write(b"OSINT Bot is running")

    def do_POST(self):

        try:
            length = int(
                self.headers.get("Content-Length", 0)
            )

            body = self.rfile.read(length)
            update = json.loads(body)

            # -------------------------
            # Callback buttons
            # -------------------------

            callback = update.get("callback_query")

            if callback:

                callback_id = callback.get("id")
                data = callback.get("data")

                message = callback.get(
                    "message",
                    {}
                )

                chat = message.get(
                    "chat",
                    {}
                )

                chat_id = chat.get("id")

                if callback_id:
                    telegram(
                        "answerCallbackQuery",
                        {
                            "callback_query_id":
                            callback_id
                        }
                    )

                if chat_id:

                    if data == "search":

                        send_message(
                            chat_id,
                            "🔎 Username ـی Instagram بنێرە.\n\n"
                            "نموونە:\n"
                            "@example"
                        )

                    elif data == "location":

                        send_message(
                            chat_id,
                            "📍 ناوی شار یان شوێنی گشتی بنێرە.\n\n"
                            "تەنها زانیاریی گشتی پشکنین دەکرێت."
                        )

                    elif data == "report":

                        send_message(
                            chat_id,
                            "📊 بۆ دروستکردنی ڕاپۆرت، "
                            "Username ـەکە بنێرە."
                        )

                    elif data == "info":

                        send_message(
                            chat_id,
                            "ℹ️ Public OSINT Bot\n\n"
                            "ئەم بۆتە بۆ پشکنینی "
                            "زانیارییە گشتییەکانە.\n\n"
                            "🔒 Private data bypass ناکرێت."
                        )

                self.send_response(200)
                self.end_headers()
                self.wfile.write(b"OK")
                return

            # -------------------------
            # Normal message
            # -------------------------

            message = update.get(
                "message",
                {}
            )

            chat = message.get(
                "chat",
                {}
            )

            chat_id = chat.get("id")

            text = message.get(
                "text",
                ""
            ).strip()

            if not chat_id:

                self.send_response(200)
                self.end_headers()
                self.wfile.write(b"OK")
                return

            # -------------------------
            # /start
            # -------------------------

            if text == "/start":

                send_message(
                    chat_id,
                    "سڵاو 👋\n\n"
                    "بەخێربێیت بۆ "
                    "🔎 Public OSINT Bot\n\n"
                    "Username ـی ئەکاونتێکی گشتی "
                    "بنێرە بۆ دروستکردنی ڕاپۆرت.",
                )

                telegram(
                    "sendMessage",
                    {
                        "chat_id": chat_id,
                        "text": "⬇️ یەکێک هەڵبژێرە:",
                        "reply_markup": menu()
                    }
                )

            # -------------------------
            # Commands
            # -------------------------

            elif text == "/search":

                send_message(
                    chat_id,
                    "🔎 Username ـەکە بنێرە."
                )

            elif text == "/location":

                send_message(
                    chat_id,
                    "📍 ناوی شار یان شوێنی گشتی بنێرە."
                )

            elif text == "/report":

                send_message(
                    chat_id,
                    "📊 Username ـەکە بنێرە "
                    "بۆ دروستکردنی ڕاپۆرت."
                )

            elif text == "/info":

                send_message(
                    chat_id,
                    "ℹ️ ئەم بۆتە تەنها داتای "
                    "گشتی و ڕێگەپێدراو بەکاردێنێت."
                )

            # -------------------------
            # Username
            # -------------------------

            elif text:

                username = (
                    text
                    .replace("https://instagram.com/", "")
                    .replace("https://www.instagram.com/", "")
                    .strip("/")
                    .lstrip("@")
                    .split("?")[0]
                )

                if username:

                    send_message(
                        chat_id,
                        "⏳ پشکنین دەکرێت..."
                    )

                    result = public_profile(
                        username
                    )

                    send_message(
                        chat_id,
                        result
                    )

                else:

                    send_message(
                        chat_id,
                        "❌ Username ـی دروست بنێرە."
                    )

            else:

                send_message(
                    chat_id,
                    "تکایە /start بنێرە."
                )

        except Exception:

            try:
                if chat_id:
                    send_message(
                        chat_id,
                        "❌ هەڵەیەک ڕوویدا. "
                        "دواتر هەوڵ بدەرەوە."
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
