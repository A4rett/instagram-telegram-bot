import os
from telegram import Update
from telegram.ext import Application


async def handler(request):
    token = os.environ["BOT_TOKEN"]

    app = Application.builder().token(token).build()

    data = await request.json()
    update = Update.de_json(data, app.bot)

    await app.process_update(update)

    return {
        "statusCode": 200,
        "body": "OK"
    }
