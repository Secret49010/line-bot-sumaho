import os
from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import PlainTextResponse
from linebot.v3.webhooks import WebhookHandler
from linebot.v3.webhooks.events import MessageEvent, TextMessageContent
from linebot.v3.messaging import MessagingApi, Configuration, ApiClient, ReplyMessageRequest, TextMessage
import openai

# 環境変数取得
LINE_CHANNEL_ACCESS_TOKEN = os.getenv("LINE_CHANNEL_ACCESS_TOKEN")
LINE_CHANNEL_SECRET = os.getenv("LINE_CHANNEL_SECimport os
from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import PlainTextResponse
from linebot.v3.messaging import Configuration, ApiClient, MessagingApi, ReplyMessageRequest, TextMessage
from linebot.v3.webhooks.models import MessageEvent, TextMessageContent, Event
from linebot.v3.webhooks.parser import WebhookParser
import openai
import json

# 環境変数
LINE_CHANNEL_ACCESS_TOKEN = os.getenv("LINE_CHANNEL_ACCESS_TOKEN")
LINE_CHANNEL_SECRET = os.getenv("LINE_CHANNEL_SECRET")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

# 初期設定
app = FastAPI()
openai.api_key = OPENAI_API_KEY
configuration = Configuration(access_token=LINE_CHANNEL_ACCESS_TOKEN)
parser = WebhookParser(channel_secret=LINE_CHANNEL_SECRET)

# Webhookエンドポイント
@app.post("/callback")
async def callback(request: Request):
    signature = request.headers.get("x-line-signature")
    body = await request.body()
    try:
        events = parser.parse(body.decode('utf-8'), signature)
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Invalid signature: {str(e)}")

    for event in events:
        if isinstance(event, MessageEvent) and isinstance(event.message, TextMessageContent):
            user_message = event.message.text

            # ChatGPT 呼び出し
            response = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "あなたはスマホの専門家です。スマホに関する質問に優しく答えてください。"},
                    {"role": "user", "content": user_message}
                ]
            )
            reply_text = response.choices[0].message.content

            # LINE に返信
            with ApiClient(configuration) as api_client:
                line_bot_api = MessagingApi(api_client)
                line_bot_api.reply_message(
                    ReplyMessageRequest(
                        reply_token=event.reply_token,
                        messages=[TextMessage(text=reply_text)]
                    )
                )

    return PlainTextResponse("OK")

@app.get("/")
def health():
    return {"status": "ok"}
