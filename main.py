from scratchclient import ScratchSession
import time
import threading

USERNAME = "roglog"
PASSWORD = "sebastian"
PROJECT_ID = 1207243603

def run_bot():
    session = ScratchSession(USERNAME, PASSWORD)
    conn = session.create_cloud_connection(PROJECT_ID)

    print("Connected to Scratch cloud!")

    @conn.on("set")
    def on_set(var):
        if var.name == "☁ CHAT_INPUT":
            print("Got:", var.value)
            response = "Echo: " + var.value
            conn.set_cloud_variable("☁ CHAT_OUTPUT", response)
            print("Sent:", response)

    # Keep connection alive
    while True:
        time.sleep(1)

while True:
    try:
        print("Connecting to Scratch...")
        run_bot()
    except Exception as e:
        print("❌ Disconnected from Scratch:", e)
        print("🔁 Reconnecting in 5 seconds...")
        time.sleep(5)
