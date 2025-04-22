# main.py
import os
import threading
from bot import criar_bot
from flask import Flask

app = Flask(__name__)

def start_bot():
    # Criar e iniciar o bot em um thread separado
    threading.Thread(target=criar_bot, daemon=True).start()

@app.route('/')
def index():
    return "Bot está rodando!"

if __name__ == "__main__":
    start_bot()  # Inicia o bot em um thread
    app.run(host='0.0.0.0', port=10000)
