import os

from flask import Flask, request, jsonify, send_from_directory
from openai import OpenAI

app = Flask(__name__, static_folder=".")

# =========================
# OpenAI Configuration
# =========================

API_KEY = os.getenv("OPENAI_API_KEY")

client = OpenAI(api_key=API_KEY) if API_KEY else None


# =========================
# Frontend
# =========================

@app.route("/")
def home():
    return send_from_directory(".", "index.html")


# =========================
# Health Check
# =========================

@app.route("/health", methods=["GET"])
def health():
    return jsonify({
        "status": "healthy",
        "api_configured": client is not None
    })


# =========================
# AI Chat
# =========================

@app.route("/api/chat", methods=["POST"])
def chat():

    try:

        # Check API configuration
        if client is None:

            return jsonify({
                "success": False,
                "error": "OPENAI_API_KEY در Environment Variables تنظیم نشده است."
            }), 500


        # Read JSON
        data = request.get_json(silent=True) or {}

        message = str(
            data.get("message", "")
        ).strip()


        # Empty message
        if not message:

            return jsonify({
                "success": False,
                "error": "پیام خالی است."
            }), 400


        # Limit extremely large requests
        if len(message) > 12000:

            return jsonify({
                "success": False,
                "error": "پیام بیش از حد طولانی است."
            }), 400


        # System instruction
        system_prompt = """
تو NEXUS AI هستی؛ یک دستیار هوشمند برای تحلیل و حل مسائل مهندسی.

وظایف اصلی تو:

1. مسئله را دقیق بررسی کن.
2. اطلاعات داده‌شده را از فرضیات جدا کن.
3. اطلاعات ناقص را مشخص کن.
4. راه‌حل‌های ممکن را پیشنهاد بده.
5. مزایا و معایب راه‌حل‌ها را بررسی کن.
6. ریسک‌های فنی و ایمنی را مشخص کن.
7. اگر محاسبه لازم است، مراحل محاسبه را واضح بنویس.
8. اگر اطلاعات کافی نیست، حدس قطعی نزن.
9. پاسخ را ساختاریافته و قابل فهم ارائه کن.
10. برای مسائل مهندسی، در صورت نیاز این ساختار را رعایت کن:

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


        # OpenAI Responses API
        response = client.responses.create(

            model="gpt-5-mini",

            instructions=system_prompt,

            input=message
        )


        answer = response.output_text


        # Return result
        return jsonify({

            "success": True,

            "answer": answer

        })


    except Exception as e:

        print("NEXUS AI ERROR:", repr(e))

        return jsonify({

            "success": False,

            "error": "خطا در پردازش درخواست AI."

        }), 500


# =========================
# Local Development
# =========================

if __name__ == "__main__":

    port = int(
        os.environ.get(
            "PORT",
            10000
        )
    )

    app.run(
        host="0.0.0.0",
        port=port
    )
