import os

from flask import Flask, request, jsonify, send_from_directory
from openai import OpenAI

app = Flask(__name__, static_folder=".")

# API Key از Environment Variable خوانده می‌شود
API_KEY = os.getenv("OPENAI_API_KEY")

client = OpenAI(api_key=API_KEY) if API_KEY else None


@app.route("/")
def home():
    return send_from_directory(".", "index.html")


@app.route("/health")
def health():
    return jsonify({
        "status": "ok",
        "ai_configured": client is not None
    })


@app.route("/api/chat", methods=["POST"])
def chat():
    try:
        if client is None:
            return jsonify({
                "error": "OPENAI_API_KEY تنظیم نشده است."
            }), 500

        data = request.get_json(silent=True) or {}

        message = str(data.get("message", "")).strip()

        if not message:
            return jsonify({
                "error": "پیام خالی است."
            }), 400

        response = client.responses.create(
            model="gpt-5-mini",
            input=[
                {
                    "role": "system",
                    "content": (
                        "تو NEXUS AI هستی؛ یک دستیار مهندسی و تحلیل پروژه. "
                        "پاسخ‌ها را دقیق، ساختاریافته و قابل فهم بده. "
                        "در مسائل مهندسی، فرضیات، محدودیت‌ها، ریسک‌ها و "
                        "اطلاعات ناقص را مشخص کن."
                    )
                },
                {
                    "role": "user",
                    "content": message
                }
            ]
        )

        answer = response.output_text

        return jsonify({
            "answer": answer
        })

    except Exception as e:
        return jsonify({
            "error": str(e)
        }), 500


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))

    app.run(
        host="0.0.0.0",
        port=port
    )
