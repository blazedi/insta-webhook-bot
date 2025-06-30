from flask import Flask, request, make_response
import os
import requests

app = Flask(__name__)

VERIFY_TOKEN      = "my_custom_verify_token"
PAGE_ACCESS_TOKEN = os.getenv("PAGE_ACCESS_TOKEN")
PAGE_ID           = os.getenv("PAGE_ID")
GUIDE_LINK        = "https://byecars.ru"

@app.route("/webhook", methods=["GET", "POST"])
def webhook():
    if request.method == "GET":
        # Верификация webhook
        token     = request.args.get("hub.verify_token")
        challenge = request.args.get("hub.challenge")
        if token == VERIFY_TOKEN:
            return make_response(challenge, 200)
        return make_response("Verification token mismatch", 403)

    data = request.json
    # Meta шлёт object = "page" для инстаграм-сообщений
    if data.get("object") == "page":
        for entry in data.get("entry", []):
            for messaging_event in entry.get("messaging", []):
                sender_id = messaging_event["sender"]["id"]
                message    = messaging_event.get("message", {})
                text       = message.get("text", "").lower()

                # Если в тексте есть слово "гайд"
                if "гайд" in text:
                    send_instagram_message(sender_id, f"Привет! Вот твой гайд: {GUIDE_LINK}")
        return make_response("EVENT_RECEIVED", 200)

    return make_response("Not a page object", 404)

def send_instagram_message(recipient_id: str, text: str):
    """Отправляет текстовое сообщение в Instagram DM через Graph API."""
    url = f"https://graph.facebook.com/v15.0/{PAGE_ID}/messages"
    payload = {
        "recipient": {"id": recipient_id},
        "message":   {"text": text},
        "messaging_type": "RESPONSE"
    }
    params = {"access_token": PAGE_ACCESS_TOKEN}
    resp = requests.post(url, params=params, json=payload)
    return resp.json()

if __name__ == "__main__":
    import os
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)

