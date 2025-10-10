from flask import Flask, request, jsonify
import requests, os
from dotenv import load_dotenv

# 🔐 Load environment variables
load_dotenv()
app = Flask(__name__)
BITRIX_WEBHOOK_URL = os.getenv("BITRIX_WEBHOOK_URL")

if not BITRIX_WEBHOOK_URL:
    raise ValueError("❌ BITRIX_WEBHOOK_URL is not set.")


@app.route("/collectchat", methods=["POST"])
def collectchat():
    try:
        # --- CRUCIAL CHANGE: ROBUST DATA PARSING ---
        
        # 1. Try to get JSON data (if Content-Type: application/json is set)
        data = request.get_json(silent=True)
        
        # 2. If no JSON data, try to get form data
        if data is None:
            if request.form:
                # Flask's request.form is a MultiDict; convert to a regular dict
                data = request.form.to_dict()
            else:
                # If no data found, initialize as empty dict to pass the error check below
                data = {}

        if not data:
            # Return 400 if no usable data was found
            return jsonify({"status": "error", "message": "No data received or incorrect Content-Type header."}), 400
        
        # Ensure data is a standard Python dict for .get() calls
        data = dict(data)
        # ----------------------------------------------
        
        print("📩 Received from Webhook:", data) 

        # --- Your Bitrix24 Payload Mapping (Make sure to include ALL fields from the log) ---
        payload = {
            "fields": {
                "TITLE": f"New lead from Web.chatbot - {data.get('name')}",
                "NAME": data.get("name"),
                "PHONE": [{"VALUE": data.get("phone"), "VALUE_TYPE": "WORK"}],
                "EMAIL": [{"VALUE": data.get("email"), "VALUE_TYPE": "WORK"}],
                # Include the new custom fields from your sample log:
                "UF_CRM_1758280375502": data.get("nationality"),
                "UF_CRM_1758280416783": data.get("tenure"),
                "UF_CRM_1758280458521": data.get("type"),
                "COMMENTS": f"URL: {data.get('page')} | IP: {data.get('ip')}",
                "SOURCE_ID": "UC_3B6N2Y", 
            }
        }
        
        # ... rest of your Bitrix API call ...
        response = requests.post(BITRIX_WEBHOOK_URL, json=payload)
        bitrix_response = response.json()
        
        print("Bitrix response:", bitrix_response)

        return jsonify({
            "status": "success",
            "bitrix_response": bitrix_response
        }), response.status_code

    except Exception as e:
        # If an error happens inside the logic (not the 400 error)
        return jsonify({
            "status": "error",
            "message": f"Server-side processing error: {str(e)}"
        }), 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
