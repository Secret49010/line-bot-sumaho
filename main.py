from fastapi import FastAPI, Request
from linebot.v3.webhooks import WebhookHandler, MessageEvent, TextMessage
from linebot.v3.messaging import MessagingApi, ReplyMessageRequest, TextMessage as ReplyTextMessage
import openai
import os

app = FastAPI()

# 環境変数からキーを取得
LINE_CHANNEL_ACCESS_TOKEN = os.getenv("LINE_CHANNEL_ACCESS_TOKEN")
LINE_CHANNEL_SECRET = os.getenv("LINE_CHANNEL_SECRET")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

# インスタンス作成
handler = WebhookHandler(LINE_CHANNEL_SECRET)
line_bot_api = MessagingApi(channel_access_token=LINE_CHANNEL_ACCESS_TOKEN)
openai.api_key = OPENAI_API_KEY

@app.post("/callback")
async def callback(request: Request):
    body = await request.body()
    signature = request.headers.get("X-Line-Signature")
    handler.handle(body.decode("utf-8"), signature)
    return "OK"

@handler.add(MessageEvent, message=TextMessage)
def handle_message(event):
    user_message = event.message.text
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[{"role": "user", "content": user_message}]
    )
    reply_text = response.choices[0].message["content"]

    reply_message = ReplyTextMessage(text=reply_text)
    line_bot_api.reply_message(
        ReplyMessageRequest(
            reply_token=event.reply_token,
            messages=[reply_message]
        )
    )
