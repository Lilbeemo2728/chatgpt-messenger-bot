from flask import Flask, request
import openai
import os
import requests

app = Flask(__name__)

VERIFY_TOKEN = os.getenv("VERIFY_TOKEN")
PAGE_ACCESS_TOKEN = os.getenv("PAGE_ACCESS_TOKEN")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

@app.route("/webhook", methods=["GET", "POST"])
def webhook():
    if request.method == "GET":
        if request.args.get("hub.mode") == "subscribe" and request.args.get("hub.verify_token") == VERIFY_TOKEN:
            return request.args.get("hub.challenge"), 200
        return "Verification failed", 403

    elif request.method == "POST":
        data = request.json
        print("Received:", data)

        for entry in data.get("entry", []):
            for messaging in entry.get("messaging", []):
                sender_id = messaging["sender"]["id"]
                if "message" in messaging:
                    message_text = messaging["message"].get("text")
                    if message_text:
                        reply = generate_gpt_reply(message_text)
                        send_message(sender_id, reply)
        return "ok", 200

def generate_gpt_reply(prompt):
    openai.api_key = OPENAI_API_KEY
    try:
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": prompt}],
            max_tokens=100,
            temperature=0.7
        )
        return response["choices"][0]["message"]["content"]
    except Exception as e:
        print("OpenAI Error:", e)
        return "Xin lỗi, tôi không trả lời được ngay bây giờ."

def send_message(recipient_id, message_text):
    url = f"https://graph.facebook.com/v17.0/me/messages?access_token={PAGE_ACCESS_TOKEN}"
    payload = {
        "recipient": {"id": recipient_id},
        "message": {"text": message_text}
    }
    headers = {"Content-Type": "application/json"}
    response = requests.post(url, json=payload, headers=headers)
    print("Sent message:", response.status_code, response.text)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
