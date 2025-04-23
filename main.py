import os
from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import PlainTextResponse
from linebot.v3.webhooks import WebhookParser
from linebot.v3.webhooks import MessageEvent, TextMessageContent
from linebot.v3.messaging import Configuration, MessagingApi, ApiClient, ReplyMessageRequest, TextMessage
from openai import OpenAI


app = FastAPI()

# 環境変数の取得
LINE_CHANNEL_ACCESS_TOKEN = os.getenv("LINE_CHANNEL_ACCESS_TOKEN")
LINE_CHANNEL_SECRET = os.getenv("LINE_CHANNEL_SECRET")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

# LINE Webhook パーサー
parser = WebhookParser(channel_secret=LINE_CHANNEL_SECRET)

# OpenAIクライアント
openai_client = OpenAI(api_key=OPENAI_API_KEY)

# ルート確認用
@app.get("/")
async def root():
    return {"message": "スマホ説明Bot 起動中 ✅"}

# LINE Webhook用エンドポイント
@app.post("/callback")
async def callback(request: Request):
    signature = request.headers.get("x-line-signature")
    body = await request.body()

    try:
        events = parser.parse(body.decode("utf-8"), signature)
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Invalid signature: {str(e)}")

    for event in events:
        if isinstance(event, MessageEvent) and isinstance(event.message, TextMessageContent):
            user_text = event.message.text

            # OpenAIに問い合わせ
            try:
                chat_response = openai_client.chat.completions.create(
                    model="gpt-3.5-turbo",
                    messages=[{"role": "user", "content": user_text}]
                )
                reply_text = chat_response.choices[0].message.content
            except Exception as e:
                reply_text = "OpenAIの応答でエラーが発生しました。"

            # LINEに返信
            config = Configuration(access_token=LINE_CHANNEL_ACCESS_TOKEN)
            with ApiClient(config) as api_client:
                line_bot_api = MessagingApi(api_client)
                line_bot_api.reply_message(
                    ReplyMessageRequest(
                        reply_token=event.reply_token,
                        messages=[TextMessage(text=reply_text)]
                    )
                )

    return PlainTextResponse("OK", status_code=200)
