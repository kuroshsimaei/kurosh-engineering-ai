import os
from flask import Flask, request, jsonify
from flask_cors import CORS
from openai import OpenAI

# =========================
# NEXUS AI - Backend
# =========================

app = Flask(__name__)
CORS(app)

# API Key باید در Environment Variables قرار بگیرد
API_KEY = os.getenv("OPENAI_API_KEY")

if not API_KEY:
    print("WARNING: OPENAI_API_KEY is not configured.")

client = OpenAI(api_key=API_KEY) if API_KEY else None


# =========================
# Health Check
# =========================

@app.route("/", methods=["GET"])
def home():
    return jsonify({
        "status": "online",
        "service": "NEXUS AI Backend",
        "message": "Backend is running successfully."
    })


@app.route("/health", methods=["GET"])
def health():
    return jsonify({
        "status": "healthy",
        "api_configured": bool(API_KEY)
    })


# =========================
# AI Chat
# =========================

@app.route("/api/chat", methods=["POST"])
def chat():

    if not client:
        return jsonify({
            "success": False,
            "error": "OPENAI_API_KEY is not configured on the server."
        }), 500

    try:
        data = request.get_json(silent=True)

        if not data:
            return jsonify({
                "success": False,
                "error": "Invalid JSON request."
            }), 400

        message = data.get("message", "").strip()

        if not message:
            return jsonify({
                "success": False,
                "error": "Message cannot be empty."
            }), 400

        # جلوگیری از ورودی‌های بسیار بزرگ
        if len(message) > 12000:
            return jsonify({
                "success": False,
                "error": "Message is too long."
            }), 400

        response = client.responses.create(
            model="gpt-5-mini",
            instructions="""
You are NEXUS AI, a professional engineering and technical AI assistant.

Answer accurately, clearly and logically.

For engineering questions:
- Analyze the problem before answering.
- Give practical and technically reasonable solutions.
- Use structured lists when appropriate.
- Explain the reasoning behind important conclusions.
- Do not invent measurements, specifications or sources.
- If information is insufficient, clearly state what is missing.
- Answer in the same language as the user.
""",
            input=message
        )

        answer = response.output_text

        return jsonify({
            "success": True,
            "answer": answer
        })

    except Exception as e:

        print("AI ERROR:", str(e))

        return jsonify({
            "success": False,
            "error": "An error occurred while processing the request."
        }), 500


# =========================
# Run Server
# =========================

if __name__ == "__main__":

    port = int(os.environ.get("PORT", 5000))

    app.run(
        host="0.0.0.0",
        port=port
    )
