from flask import Flask, request, abort
import os
from dotenv import load_dotenv
from linebot import LineBotApi, WebhookHandler
from linebot.models import MessageEvent, TextMessage, TextSendMessage
from linebot.exceptions import InvalidSignatureError
import google.generativeai as genai

# 環境変数を読み込む
load_dotenv()

# 環境変数取得
LINE_CHANNEL_ACCESS_TOKEN = os.getenv("LINE_CHANNEL_ACCESS_TOKEN")
LINE_CHANNEL_SECRET = os.getenv("LINE_CHANNEL_SECRET")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

# 初期化
line_bot_api = LineBotApi(LINE_CHANNEL_ACCESS_TOKEN)
handler = WebhookHandler(LINE_CHANNEL_SECRET)

# Gemini 初期化
genai.configure(api_key=GEMINI_API_KEY)
model = genai.GenerativeModel(model_name="models/gemini-pro")  # ← 正しいモデル名に修正

# Flask アプリ
app = Flask(__name__)

# Webhookエンドポイント
@app.route("/callback", methods=["POST"])
def callback():
    signature = request.headers["X-Line-Signature"]
    body = request.get_data(as_text=True)

    try:
        handler.handle(body, signature)
    except InvalidSignatureError:
        abort(400)

    return "OK"

# メッセージイベント処理
@handler.add(MessageEvent, message=TextMessage)
def handle_message(event):
    user_input = event.message.text

    try:
        response = model.generate_content(user_input)
        reply_text = response.text.strip()
    except Exception as e:
        reply_text = f"エラーが発生しました: {e}"

    line_bot_api.reply_message(
        event.reply_token,
        TextSendMessage(text=reply_text)
    )

# ローカル実行用
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))
