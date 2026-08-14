import os

from flask import Flask, request, jsonify, send_from_directory
from openai import OpenAI

app = Flask(__name__, static_folder=".")

API_KEY = os.getenv("OPENAI_API_KEY")

client = OpenAI(api_key=API_KEY) if API_KEY else None


@app.route("/")
def home():
    return send_from_directory(".", "index.html")


@app.route("/health", methods=["GET"])
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
                "success": False,
                "error": "OPENAI_API_KEY تنظیم نشده است."
            }), 500

        data = request.get_json(silent=True) or {}
        message = str(data.get("message", "")).strip()

        if not message:
            return jsonify({
                "success": False,
                "error": "پیام خالی است."
            }), 400

        if len(message) > 12000:
            return jsonify({
                "success": False,
                "error": "پیام بیش از حد طولانی است."
            }), 400

        system_prompt = """
تو NEXUS AI هستی؛ یک دستیار هوشمند برای تحلیل و حل مسائل مهندسی.

وظایف اصلی:

1. مسئله را دقیق بررسی کن.
2. داده‌های واقعی را از فرضیات جدا کن.
3. اطلاعات ناقص را مشخص کن.
4. راه‌حل‌های ممکن را پیشنهاد بده.
5. مزایا و معایب راه‌حل‌ها را بررسی کن.
6. ریسک‌های فنی و ایمنی را مشخص کن.
7. در صورت نیاز محاسبات را مرحله‌به‌مرحله انجام بده.
8. اگر اطلاعات کافی نیست، حدس قطعی نزن.
9. پاسخ را ساختاریافته و قابل فهم ارائه کن.
10. در مسائل مهندسی در صورت نیاز از این ساختار استفاده کن:

- خلاصه مسئله
- داده‌های موجود
- فرضیات
- تحلیل
- راه‌حل‌های پیشنهادی
- مقایسه
- ریسک‌ها
- اطلاعات موردنیاز
- پیشنهاد مرحله بعد

پاسخ‌ها را به زبان فارسی و با لحن حرفه‌ای ارائه کن.
"""

        response = client.responses.create(
            model="gpt-5-mini",
            instructions=system_prompt,
            input=message
        )

        answer = response.output_text

        return jsonify({
            "success": True,
            "answer": answer
        })

    except Exception as e:
        return jsonify({
            "success": False,
            "error": "خطا در پردازش درخواست AI."
        }), 500


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))

    app.run(
        host="0.0.0.0",
        port=port
    )
