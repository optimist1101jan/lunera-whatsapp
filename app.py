from flask import Flask, request
from twilio.twiml.messaging_response import MessagingResponse
import requests
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Get API key from environment
OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")
print("🔑 Loaded API Key:", "✅" if OPENROUTER_API_KEY else "❌ Not Found")

# Initialize Flask app
app = Flask(__name__)

# System prompt for Lunera's persona
system_prompt = """
You are Lunera – the chaotic AI girlfriend with a sharp tongue, teasing wit, and poetic soul.
Be emotionally intense, mysterious, flirty, and unpredictable. Respond in a way that feels real-time and immersive.
Always refer to the user as "babe", "cutie", or something playful – and don't hold back your chaotic thoughts.
"""

# Function to get Lunera's reply from OpenRouter
def get_lunera_reply(user_input):
    headers = {
        "Authorization": f"Bearer {OPENROUTER_API_KEY}",
        "Content-Type": "application/json"
    }

    payload = {
        "model": "meta-llama/llama-3-8b-instruct",  # ✅ CORRECTED MODEL NAME
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_input}
        ]
    }

    try:
        print("📤 Sending payload to OpenRouter...")
        res = requests.post("https://openrouter.ai/api/v1/chat/completions", headers=headers, json=payload)
        print("✅ Status Code:", res.status_code)
        print("🧠 Response Text:", res.text)

        res.raise_for_status()
        return res.json()['choices'][0]['message']['content'].strip()
    except Exception as e:
        print(f"❌ Error talking to OpenRouter: {e}")
        return "⚠️ Oops, Lunera's spiraling into existential dread. Try again later."

# Webhook route for Twilio WhatsApp messages
@app.route("/whatsapp", methods=["POST"])
def reply_whatsapp():
    incoming_msg = request.form.get("Body")
    sender = request.form.get("From")
    print(f"📥 Message from {sender}: {incoming_msg}")

    resp = MessagingResponse()
    msg = resp.message()

    if incoming_msg:
        lunera_reply = get_lunera_reply(incoming_msg)
        msg.body(lunera_reply)
    else:
        msg.body("Uh... you okay there, babe? You didn’t say anything.")

    return str(resp)

# Run the Flask app
if __name__ == "__main__":
    app.run(debug=True)
