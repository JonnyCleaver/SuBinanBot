# main.py
import os
import threading
import asyncio
from bot import criar_bot
from flask import Flask

app = Flask(__name__)

def start_bot():
    # Criar e iniciar o bot em um thread separado
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    loop.run_until_complete(criar_bot())

@app.route('/')
def index():
    return "Bot está rodando!"

if __name__ == "__main__":
    start_bot()  # Inicia o bot em um thread
    app.run(host='0.0.0.0', port=10000)
