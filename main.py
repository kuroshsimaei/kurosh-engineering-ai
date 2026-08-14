import os

from flask import Flask, request, jsonify
from flask_cors import CORS
from openai import OpenAI


# =========================================================
# KUROSH-AI / NEXUS AI BACKEND
# =========================================================

app = Flask(__name__)
CORS(app)


# =========================================================
# CONFIGURATION
# =========================================================

API_KEY = os.environ.get("OPENAI_API_KEY")

client = None

if API_KEY:
    client = OpenAI(api_key=API_KEY)


# =========================================================
# HOME
# =========================================================

@app.get("/")
def home():
    return jsonify({
        "status": "online",
        "service": "NEXUS AI Backend",
        "message": "Backend is running successfully."
    })


# =========================================================
# HEALTH CHECK
# =========================================================

@app.get("/health")
def health():
    return jsonify({
        "status": "healthy",
        "api_configured": bool(API_KEY)
    })


# =========================================================
# AI CHAT
# =========================================================

@app.post("/api/chat")
def chat():

    if client is None:
        return jsonify({
            "success": False,
            "error": "OPENAI_API_KEY is not configured."
        }), 500

    try:

        data = request.get_json(silent=True)

        if not isinstance(data, dict):
            return jsonify({
                "success": False,
                "error": "Invalid JSON request."
            }), 400

        message = str(data.get("message", "")).strip()

        if not message:
            return jsonify({
                "success": False,
                "error": "Message cannot be empty."
            }), 400

        if len(message) > 12000:
            return jsonify({
                "success": False,
                "error": "Message is too long."
            }), 400


        # =================================================
        # OPENAI REQUEST
        # =================================================

        response = client.responses.create(
            model="gpt-5-mini",

            instructions="""
You are NEXUS AI, a professional engineering,
science and technical AI assistant.

Your responsibilities:

1. Understand the user's problem before answering.
2. Give accurate and logically structured answers.
3. For engineering problems, explain the reasoning.
4. Provide practical and technically reasonable solutions.
5. When useful, provide multiple possible solutions.
6. Do not invent measurements, specifications,
   experimental results or sources.
7. If important information is missing, say what is missing.
8. Answer in the same language as the user.
9. Keep answers clear and useful.
10. For calculations, show the important steps.
""",

            input=message
        )

        answer = response.output_text

        return jsonify({
            "success": True,
            "answer": answer
        })


    except Exception as error:

        print("AI ERROR:", repr(error))

        return jsonify({
            "success": False,
            "error": "AI request failed."
        }), 500


# =========================================================
# ERROR HANDLERS
# =========================================================

@app.errorhandler(404)
def not_found(error):
    return jsonify({
        "success": False,
        "error": "Endpoint not found."
    }), 404


@app.errorhandler(500)
def server_error(error):
    return jsonify({
        "success": False,
        "error": "Internal server error."
    }), 500


# =========================================================
# LOCAL DEVELOPMENT
# =========================================================

if __name__ == "__main__":

    port = int(os.environ.get("PORT", 10000))

    app.run(
        host="0.0.0.0",
        port=port
    )
