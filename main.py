from fastapi import FastAPI, Request, HTTPException
from linebot.v3.messaging import MessagingApi, Configuration, ReplyMessageRequest, TextMessage as ReplyTextMessage
from linebot.v3.webhooks import WebhookParser, MessageEvent, TextMessage
from openai import OpenAI
import os

app = FastAPI()

channel_access_token = os.getenv("LINE_CHANNEL_ACCESS_TOKEN")
channel_secret = os.getenv("LINE_CHANNEL_SECRET")
openai_api_key = os.getenv("OPENAI_API_KEY")

configuration = Configuration(access_token=channel_access_token)
line_bot_api = MessagingApi(configuration)
parser = WebhookParser(channel_secret)
openai.api_key = openai_api_key

@app.post("/callback")
async def callback(request: Request):
    signature = request.headers.get("X-Line-Signature")
    body = await request.body()

    try:
        events = parser.parse(body.decode("utf-8"), signature)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

    for event in events:
        if isinstance(event, MessageEvent) and isinstance(event.message, TextMessage):
            user_message = event.message.text

            response = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages=[{"role": "user", "content": user_message}]
            )

            reply_text = response.choices[0].message["content"].strip()

            line_bot_api.reply_message(
                ReplyMessageRequest(
                    reply_token=event.reply_token,
                    messages=[ReplyTextMessage(text=reply_text)]
                )
            )

    return "OK"
