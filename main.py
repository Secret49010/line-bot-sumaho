from fastapi import FastAPI, Request, HTTPException
from linebot.v3.messaging import MessagingApi, TextMessage as ReplyTextMessage, ReplyMessageRequest
from linebot.v3.webhooks import WebhookParser, MessageEvent, TextMessage
from linebot.v3.exceptions import InvalidSignatureError
from openai import OpenAI
import os

app = FastAPI()

# 環境変数から取得
LINE_CHANNEL_ACCESS_TOKEN = os.getenv("LINE_CHANNEL_ACCESS_TOKEN")
LINE_CHANNEL_SECRET = os.getenv("LINE_CHANNEL_SECRET")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

# LINE Bot設定
line_bot_api = MessagingApi(access_token=LINE_CHANNEL_ACCESS_TOKEN)
parser = WebhookParser(LINE_CHANNEL_SECRET)

# OpenAI設定
openai_api = OpenAI(api_key=OPENAI_API_KEY)

@app.post("/callback")
async def callback(request: Request):
    signature = request.headers.get("X-Line-Signature")
    body = await request.body()

    try:
        events = parser.parse(body.decode("utf-8"), signature)
    except InvalidSignatureError:
        raise HTTPException(status_code=400, detail="Invalid signature")

    for event in events:
        if isinstance(event, MessageEvent) and isinstance(event.message, TextMessage):
            user_message = event.message.text

            # OpenAI API呼び出し
            response = openai_api.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "user", "content": user_message}
                ]
            )
            reply_text = response.choices[0].message.content.strip()

            # LINEへ返信
            line_bot_api.reply_message(
                ReplyMessageRequest(
                    reply_token=event.reply_token,
                    messages=[ReplyTextMessage(text=reply_text)]
                )
            )

    return "OK"

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=10000)
