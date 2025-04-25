import os
import openai
from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import PlainTextResponse
from linebot.v3.messaging import (
    MessagingApi, Configuration, ApiClient,
    ReplyMessageRequest, TextMessage
)
from linebot.v3.webhook import WebhookHandler
from linebot.v3.webhook.models import MessageEvent, TextMessageContent
from linebot.v3.exceptions import InvalidSignatureError

# 環境変数の読み込み
LINE_CHANNEL_SECRET = os.getenv("LINE_CHANNEL_SECRET")
LINE_CHANNEL_ACCESS_TOKEN = os.getenv("LINE_CHANNEL_ACCESS_TOKEN")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

# FastAPIインスタンス
app = FastAPI()

# LINE SDK 設定
configuration = Configuration(access_token=LINE_CHANNEL_ACCESS_TOKEN)
handler = WebhookHandler(channel_secret=LINE_CHANNEL_SECRET)
openai.api_key = OPENAI_API_KEY

# ルート確認用
@app.get("/")
def read_root():
    return {"message": "LINE Bot is running!"}

# コールバックエンドポイント
@app.post("/callback")
async def callback(request: Request):
    signature = request.headers.get("X-Line-Signature", "")
    body = await request.body()

    try:
        handler.handle(body.decode("utf-8"), signature)
    except InvalidSignatureError:
        raise HTTPException(status_code=400, detail="Invalid signature")

    return PlainTextResponse("OK", status_code=200)

# メッセージイベント処理
@handler.add(MessageEvent, message=TextMessageContent)
def handle_message(event: MessageEvent):
    user_message = event.message.text

    # OpenAI API に問い合わせ
    try:
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "あなたはスマホの先生です。"},
                {"role": "user", "content": user_message}
            ]
        )
        ai_response = response.choices[0].message["content"]
    except Exception as e:
        ai_response = "OpenAI応答エラー: " + str(e)

    # LINEに返信
    with ApiClient(configuration) as api_client:
        line_bot_api = MessagingApi(api_client)
        line_bot_api.reply_message(
            ReplyMessageRequest(
                reply_token=event.reply_token,
                messages=[TextMessage(text=ai_response)]
            )
        )
