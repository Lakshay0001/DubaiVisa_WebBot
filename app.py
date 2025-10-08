from flask import Flask, request, jsonify
import requests
import os
from dotenv import load_dotenv

# 🔐 Load environment variables from .env file (local) or system env (Render etc.)
load_dotenv()

# ✅ Flask app
app = Flask(__name__)

# ✅ Get Bitrix webhook URL from environment variable
BITRIX_WEBHOOK_URL = os.getenv("BITRIX_WEBHOOK_URL")

# ❗ Safety check: Warn if webhook URL is not set
if not BITRIX_WEBHOOK_URL:
    raise ValueError("❌ BITRIX_WEBHOOK_URL is not set. Please check your environment variables.")

@app.route("/")
def home():
    return "✅ Flask app is running!"

@app.route("/collectchat", methods=["POST"])
def collectchat():
    try:
        data = request.json  # JSON input from Collect.chat

        print("📩 Received from Collect.chat:", data)  # For debug logs

        # ✅ Mapping Collect.chat data to Bitrix24 lead fields
        payload = {
            "fields": {
                "TITLE": "Lead from Collect.chat",
                "NAME": data.get("name", ""),
                "LAST_NAME": data.get("last_name", ""),
                "EMAIL": [
                    {"VALUE": data.get("email", ""), "VALUE_TYPE": "WORK"}
                ],
                "PHONE": [
                    {"VALUE": data.get("phone", ""), "VALUE_TYPE": "WORK"}
                ]
            }
        }

        # ✅ Send to Bitrix24 CRM
        response = requests.post(BITRIX_WEBHOOK_URL, json=payload)
        bitrix_response = response.json()

        # 🧾 Return response to client
        return jsonify({
            "status": "success",
            "data_received": data,
            "bitrix_response": bitrix_response
        }), response.status_code

    except Exception as e:
        # ❌ If something goes wrong
        return jsonify({
            "status": "error",
            "message": str(e)
        }), 500

# ✅ Only used in local development (not in Render)
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
