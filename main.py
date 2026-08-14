```python
import os

from flask import Flask, request, jsonify, send_from_directory
from openai import OpenAI


app = Flask(__name__, static_folder=".")


# =====================================================
# OPENAI CONFIGURATION
# =====================================================

API_KEY = os.getenv("OPENAI_API_KEY")

client = OpenAI(
    api_key=API_KEY
) if API_KEY else None


# =====================================================
# FRONTEND
# =====================================================

@app.route("/")
def home():

    return send_from_directory(
        ".",
        "index.html"
    )


# =====================================================
# HEALTH CHECK
# =====================================================

@app.route("/health", methods=["GET"])
def health():

    return jsonify({
        "status": "ok",
        "ai_configured": client is not None
    })


# =====================================================
# AI CHAT
# =====================================================

@app.route("/api/chat", methods=["POST"])
def chat():

    try:

        # ---------------------------------------------
        # CHECK API KEY
        # ---------------------------------------------

        if client is None:

            return jsonify({
                "error": "OPENAI_API_KEY تنظیم نشده است."
            }), 500


        # ---------------------------------------------
        # READ REQUEST
        # ---------------------------------------------

        data = request.get_json(
            silent=True
        ) or {}


        message = str(
            data.get("message", "")
        ).strip()


        if not message:

            return jsonify({
                "error": "پیام خالی است."
            }), 400


        # ---------------------------------------------
        # OPENAI REQUEST
        # ---------------------------------------------

        response = client.responses.create(

            model="gpt-5-mini",

            instructions=(
                "تو NEXUS AI هستی؛ یک دستیار مهندسی و "
                "تحلیل پروژه. "
                "پاسخ‌ها را دقیق، ساختاریافته و قابل فهم بده. "
                "در مسائل مهندسی، فرضیات، محدودیت‌ها، "
                "ریسک‌ها، داده‌های ناقص و عدم قطعیت را مشخص کن. "
                "اگر اطلاعات کافی نیست، قبل از نتیجه‌گیری "
                "اطلاعات موردنیاز را مشخص کن."
            ),

            input=message
        )


        # ---------------------------------------------
        # EXTRACT ANSWER
        # ---------------------------------------------

        answer = response.output_text


        if not answer:

            answer = (
                "مدل پاسخی تولید نکرد. "
                "لطفاً دوباره تلاش کن."
            )


        # ---------------------------------------------
        # RESPONSE
        # ---------------------------------------------

        return jsonify({

            "success": True,

            "answer": answer

        })


    except Exception as e:

        print(
            "NEXUS AI ERROR:",
            repr(e)
        )


        return jsonify({

            "success": False,

            "error": str(e)

        }), 500


# =====================================================
# SERVER
# =====================================================

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
```
