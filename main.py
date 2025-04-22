import asyncio
import threading
from bot import criar_bot
from server import app as flask_app  # app Flask no server.py

def start_bot():
    asyncio.run(_start_bot())

async def _start_bot():
    app = await criar_bot()
    await app.initialize()
    await app.start()
    print("🤖 Bot do Telegram iniciado com sucesso!")

if __name__ == "__main__":
    threading.Thread(target=start_bot, daemon=True).start()
    flask_app.run(host="0.0.0.0", port=10000)
