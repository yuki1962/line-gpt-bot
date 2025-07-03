from flask import Flask, request, abort
import os
from dotenv import load_dotenv
from linebot import LineBotApi, WebhookHandler
from linebot.exceptions import InvalidSignatureError
from linebot.models import MessageEvent, TextMessage, TextSendMessage
import google.generativeai as genai

# .envファイルを読み込む
load_dotenv()

# 環境変数からAPIキーとLINE設定を取得
LINE_CHANNEL_ACCESS_TOKEN = os.getenv("LINE_CHANNEL_ACCESS_TOKEN")
LINE_CHANNEL_SECRET = os.getenv("LINE_CHANNEL_SECRET")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

# LINE APIとGemini APIを初期化
line_bot_api = LineBotApi(LINE_CHANNEL_ACCESS_TOKEN)
handler = WebhookHandler(LINE_CHANNEL_SECRET)

genai.configure(api_key=GEMINI_API_KEY)
model = genai.GenerativeModel(model_name="models/gemini-pro")

# Flaskアプリ
app = Flask(__name__)

# LINE Webhookエンドポイント
@app.route("/callback", methods=["POST"])
def callback():
    signature = request.headers.get("X-Line-Signature")
    body = request.get_data(as_text=True)

    try:
        handler.handle(body, signature)
    except InvalidSignatureError:
        abort(400)

    return "OK"

# ユーザーのメッセージ受信時
@handler.add(MessageEvent, message=TextMessage)
def handle_message(event):
    user_input = event.message.text

    try:
        # Geminiに問い合わせ
        response = model.generate_content(user_input)
        reply_text = response.text.strip()
    except Exception as e:
        print(f"Gemini API Error: {e}")
        reply_text = "エラーが発生しました。少し時間を置いて再試行してください。"

    # LINEに返信
    line_bot_api.reply_message(
        event.reply_token,
        TextSendMessage(text=reply_text)
    )

# ローカル実行用
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))
