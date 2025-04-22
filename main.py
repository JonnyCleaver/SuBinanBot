import os
import asyncio
from flask import Flask
from bot import criar_bot  # Função que cria e executa o bot
from threading import Thread

app = Flask(__name__)

@app.route('/')
def home():
    return "Bot está em funcionamento!"

def start_bot():
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    loop.run_until_complete(criar_bot())  # Inicia o bot

if __name__ == "__main__":
    # Inicializa o servidor Flask em um thread separado
    flask_thread = Thread(target=lambda: app.run(host="0.0.0.0", port=10000))
    flask_thread.start()

    # Inicia o bot em um thread separado
    start_bot()
