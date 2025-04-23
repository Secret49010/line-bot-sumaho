from fastapi import FastAPI, Request, HTTPException
from linebot.v3.webhook import WebhookHandler
from linebot.v3.models import MessageEvent, TextMessageContent
from linebot.v3.messaging import MessagingApi, Configuration
from linebot.v3.messaging.models import ReplyMessageRequest, TextMessage
import os

app = FastAPI()

channel_secret = os.getenv("LINE_CHANNEL_SECRET")
channel_access_token = os.getenv("LINE_CHANNEL_ACCESS_TOKEN")

if not channel_secret or not channel_access_token:
    raise Exception("環境変数が設定されていません")

handler = WebhookHandler(channel_secret)

configuration = Configuration(access_token=channel_access_token)
line_bot_api = MessagingApi(configuration)

@app.post("/callback")
async def callback(request: Request):
    signature = request.headers.get("X-Line-Signature")
    body = await request.body()

    try:
        handler.handle(body.decode("utf-8"), signature)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

    return "OK"

@handler.add(MessageEvent, message=TextMessageContent)
def handle_message(event: MessageEvent):
    text = event.message.text
    reply_token = event.reply_token

    reply = ReplyMessageRequest(
        reply_token=reply_token,
        messages=[TextMessage(text=f"受け取ったメッセージ: {text}")]
    )
    line_bot_api.reply_message(reply)

    )

    reply_text = response.choices[0].message["content"].strip()

    with ApiClient(configuration) as api_client:
        line_bot_api = MessagingApi(api_client)
        line_bot_api.reply_message(
            reply_token=event.reply_token,
            messages=[{"type": "text", "text": reply_text}]
        )
