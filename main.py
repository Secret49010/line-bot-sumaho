import os
import openai
from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import PlainTextResponse  # ← 追加
from linebot.v3.messaging import Configuration, ApiClient, MessagingApi
from linebot.v3.webhook import WebhookHandler
from linebot.v3.webhook_models import MessageEvent, TextMessageContent

app = FastAPI()

LINE_CHANNEL_SECRET = os.getenv("LINE_CHANNEL_SECRET")
LINE_CHANNEL_ACCESS_TOKEN = os.getenv("LINE_CHANNEL_ACCESS_TOKEN")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

if not all([LINE_CHANNEL_SECRET, LINE_CHANNEL_ACCESS_TOKEN, OPENAI_API_KEY]):
    raise Exception("環境変数が設定されていません")

openai.api_key = OPENAI_API_KEY
handler = WebhookHandler(LINE_CHANNEL_SECRET)

configuration = Configuration(access_token=LINE_CHANNEL_ACCESS_TOKEN)


@app.post("/callback")
async def callback(request: Request):
    signature = request.headers.get("X-Line-Signature")
    body = await request.body()
    body_str = body.decode("utf-8")

    try:
        handler.handle(body_str, signature)
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Invalid signature or error: {str(e)}")
    return "OK"


@handler.add(MessageEvent, message=TextMessageContent)
def handle_message(event: MessageEvent):
    user_message = event.message.text

    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": "あなたはスマホの専門家です。"},
            {"role": "user", "content": user_message}
        ]
    )

    reply_text = response.choices[0].message["content"].strip()

    with ApiClient(configuration) as api_client:
        line_bot_api = MessagingApi(api_client)
        line_bot_api.reply_message(
            reply_token=event.reply_token,
            messages=[{"type": "text", "text": reply_text}]
        )
