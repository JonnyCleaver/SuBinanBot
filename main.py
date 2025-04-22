import threading
from server import app as flask_app
from bot import iniciar_bot
from waitress import serve
import os
import asyncio

def run_flask():
    port = int(os.environ.get("PORT", 5000))
    serve(flask_app, host="0.0.0.0", port=port)

def run_bot():
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    loop.run_until_complete(iniciar_bot())

if __name__ == "__main__":
    t1 = threading.Thread(target=run_flask)
    t2 = threading.Thread(target=run_bot)
    t1.start()
    t2.start()
