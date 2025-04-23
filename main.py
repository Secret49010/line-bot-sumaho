from fastapi import FastAPI, Request, HTTPException
from linebot.v3.webhook import WebhookHandler
from linebot.v3.messaging import MessagingApi, Configuration
from linebot.v3.messaging.models import ReplyMessageRequest, TextMessage
from linebot.v3.webhooks import MessageEvent, TextMessageContent
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

@handler.add(MessageEvent)
def handle_message(event: MessageEvent):
    if isinstance(event.message, TextMessageContent):
        text = event.message.text
        reply_token = event.reply_token

        reply = ReplyMessageRequest(
            reply_token=reply_token,
            messages=[TextMessage(text=f"受け取ったメッセージ: {text}")]
        )
        line_bot_api.reply_message(reply)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000)
