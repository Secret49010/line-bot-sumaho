from fastapi import FastAPI, Request
from linebot.v3.messaging import MessagingApiClient
from linebot.v3.webhook import WebhookHandler
from linebot.v3.models import MessageEvent, TextMessageContent, ReplyMessageRequest, TextMessage
from starlette.responses import PlainTextResponse
import openai
import os

app = FastAPI()

# 環境変数から各種トークンを取得
LINE_CHANNEL_ACCESS_TOKEN = os.environ["LINE_CHANNEL_ACCESS_TOKEN"]
LINE_CHANNEL_SECRET = os.environ["LINE_CHANNEL_SECRET"]
OPENAI_API_KEY = os.environ["OPENAI_API_KEY"]

line_bot_api = MessagingApiClient(LINE_CHANNEL_ACCESS_TOKEN)
handler = WebhookHandler(LINE_CHANNEL_SECRET)
openai.api_key = OPENAI_API_KEY

@app.post("/callback")
async def callback(request: Request):
    signature = request.headers.get("X-Line-Signature")
    body = await request.body()

    try:
        handler.handle(body.decode("utf-8"), signature)
    except Exception as e:
        return PlainTextResponse(str(e), status_code=400)

    return PlainTextResponse("OK", status_code=200)

@handler.add(MessageEvent)
def handle_message(event):
    if isinstance(event.message, TextMessageContent):
        user_message = event.message.text

        # ChatGPTへの問い合わせ
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "あなたは親切なスマホ・アプリ操作説明アシスタントです。"},
                {"role": "user", "content": user_message}
            ]
        )

        reply_text = response.choices[0].message.content

        line_bot_api.reply_message(
            ReplyMessageRequest(
                reply_token=event.reply_token,
                messages=[TextMessage(text=reply_text)]
            )
        )

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))
