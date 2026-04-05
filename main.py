from scratchclient import ScratchSession
import time
import requests
import json
from flask import Flask
import threading
import os

app = Flask(__name__)

@app.route("/")
def home():
    return "Server is running!"

airesponse = ""

def ai(prompt):
    api_key = "sk*proj*1upZkvkZ0*heTGeveqQaWFJyzMcVLK3lB*ZJ2AsGqXVqZPz2cpwgFVKn*RU5gew12j_n8Tmcl9T3BlbkFJXxv4pkxjysRJEtbW4vq_1KFuQLwC8W10QL8C7Rbke1tKZe5ng*SMtILvcy8hdXqvryS4TjMrIA".replace("*", "-")

    url = "https://api.openai.com/v1/responses"
    headers = {"Content-Type": "application/json", "Authorization": f"Bearer {api_key}"}
    data = {"model": "gpt-4o-mini", "input": prompt}

    try:
        response = requests.post(url, headers=headers, data=json.dumps(data))
        response.raise_for_status()
        airesponse = (
            response.json().get("output", [{}])[0]
                .get("content", [{}])[0]
                .get("text")
        )
        return airesponse or "..."
    except Exception as e:
        print(f"AI error: {e}")
        return "error"

SPRITES = '1234567890aAbBcCdDeEfFgGhHiIjJkKlLmMnNoOpPqQrRsStTuUvVwWxXyYzZ `~!@#$%&*()-_=+{}|\\[]:;\'",<>.?/'

def encode(text):
    encoded = ""
    for char in text:
        if char not in SPRITES:
            continue
        encoded += "0" + str(SPRITES.index(char) + 1)
    encoded += "0"
    return encoded[:240] + encode("... ") if len(encoded) > 240 else encoded

def decode(text):
    decoded, i = "", 0
    while i < len(text):
        if text[i] == "0":
            i += 1
            num_str = ""
            while i < len(text) and text[i] != "0":
                num_str += text[i]
                i += 1
            if num_str:
                decoded += SPRITES[int(num_str) - 1]
        else:
            i += 1
    return decoded

USERNAME = "roglog"
PASSWORD = "sebastian"
PROJECT_ID = 1207243603

import time, threading

last_message = time.time()

def run_scratch():
    while True:  # keep trying forever
        try:
            print("Connecting to Scratch...")
            session = ScratchSession(USERNAME, PASSWORD)
            conn = session.create_cloud_connection(PROJECT_ID)

            def on_set(var):
                if var.name == "☁ CHAT_INPUT":
                    decoded = decode(var.value)
                    print("Got:", decoded)
                    aires = ai(decoded)
                    print("AI:", aires)
                    try:
                        conn.set_cloud_variable("☁ CHAT_OUTPUT", encode(aires))
                    except Exception as e:
                        print("Failed to send to Scratch:", e)
                        raise  # force reconnect

            conn.on("set", on_set)

            print("Connected! Listening for cloud changes...")

            # --- watchdog loop ---
            last_ping = time.time()
            while True:
                time.sleep(5)

                # if the websocket thread has died, _ws.sock will be None
                if not conn._ws or not conn._ws.connected:
                    raise Exception("Scratch cloud connection lost")

                # (optional) timeout if no events seen for 10+ minutes
                if time.time() - last_ping > 600:
                    raise Exception("No cloud activity, forcing reconnect")

        except Exception as e:
            print(f"Scratch connection failed: {e}")
            print("Reconnecting in 5s...")
            time.sleep(5)


if __name__ == "__main__":
    # Start Scratch bot in background thread
    threading.Thread(target=run_scratch, daemon=True).start()

    # Start Flask on Render’s PORT
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
