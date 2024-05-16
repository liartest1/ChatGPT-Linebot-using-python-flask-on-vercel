from flask import Flask, request, abort
from linebot import LineBotApi, WebhookHandler
from linebot.exceptions import InvalidSignatureError
from linebot.models import MessageEvent, TextMessage, TextSendMessage
import openai

app = Flask(__name__)

# 設置LineBot的Channel Access Token和Channel Secret
line_bot_api = LineBotApi("LINE_CHANNEL_ACCESS_TOKEN")
handler = WebhookHandler("LINE_CHANNEL_SECRET")

# 設置OpenAI API 密鑰
openai.api_key = "OPENAI_API_KEY"

# 與GPT模型交互的函數
def chat_with_gpt(prompt):
    response = openai.Completion.create(
        engine="davinci-codex",  # 或者你想用的其他引擎
        prompt=prompt,
        temperature=0,
        max_tokens=240
    )
    return response.choices[0].text.strip()

# Line的Webhook接口
@app.route("/webhook", methods=['POST'])
def callback():
    signature = request.headers['X-Line-Signature']

    # 獲取request的body
    body = request.get_data(as_text=True)
    app.logger.info("Request body: " + body)

    # 驗證簽名
    try:
        handler.handle(body, signature)
    except InvalidSignatureError:
        abort(400)

    return 'OK'

# 處理TextMessage事件
@handler.add(MessageEvent, message=TextMessage)
def handle_message(event):
    user_input = event.message.text
    response = chat_with_gpt(user_input)
    line_bot_api.reply_message(
        event.reply_token,
        TextSendMessage(text=response)
    )

if __name__ == "__main__":
    app.run()
