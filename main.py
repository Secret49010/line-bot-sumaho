from fastapi import FastAPI, Request
from linebot.v3.messaging import MessagingApi, TextMessageContent, ReplyMessageRequest, TextMessage
from linebot.v3.webhooks import WebhookHandler, MessageEvent
from starlette.responses import PlainTextResponse
import openai
import os

app = FastAPI()

# 環境変数から設定値を取得
LINE_CHANNEL_ACCESS_TOKEN = os.environ["LINE_CHANNEL_ACCESS_TOKEN"]
LINE_CHANNEL_SECRET = os.environ["LINE_CHANNEL_SECRET"]
OPENAI_API_KEY = os.environ["OPENAI_API_KEY"]

# LINE Bot APIクライアントとWebhookHandlerを初期化
line_bot_api = MessagingApi(LINE_CHANNEL_ACCESS_TOKEN)
handler = WebhookHandler(LINE_CHANNEL_SECRET)

# OpenAIのAPIキー設定
openai.api_key = OPENAI_API_KEY

# Webhookの受け口
@app.post("/callback")
async def callback(request: Request):
    signature = request.headers.get("X-Line-Signature")
    body = await request.body()

    try:
        handler.handle(body.decode("utf-8"), signature)
    except Exception as e:
        return PlainTextResponse(str(e), status_code=400)

    return PlainTextResponse("OK", status_code=200)

# メッセージ受信時の処理
@handler.add(MessageEvent)
def handle_message(event):
    if isinstance(event.message, TextMessageContent):
        user_message = event.message.text

        # ChatGPTへ問い合わせ
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "あなたは親切なスマホ・アプリ操作説明アシスタントです。"},
                {"role": "user", "content": user_message}
            ]
        )

        reply_text = response.choices[0].message.content

        # LINEに返信
        line_bot_api.reply_message(
            ReplyMessageRequest(
                reply_token=event.reply_token,
                messages=[TextMessage(text=reply_text)]
            )
        )

# ローカル起動用（Renderでは不要）
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))

