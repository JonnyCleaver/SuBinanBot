
from flask import Flask, request, jsonify
import sqlite3
import os
from binance.client import Client
import re
from trader import place_order_customizado

app = Flask(__name__)
DB_PATH = "users.db"

if not os.path.exists(DB_PATH):
    with sqlite3.connect(DB_PATH) as conn:
        conn.execute("""
            CREATE TABLE users (
                user_id INTEGER PRIMARY KEY,
                api_key TEXT,
                api_secret TEXT
            )
        """)

@app.route("/configurar_keys", methods=["POST"])
def configurar_keys():
    data = request.get_json()
    user_id = data["user_id"]
    api_key = data["api_key"]
    api_secret = data["api_secret"]

    with sqlite3.connect(DB_PATH) as conn:
        conn.execute("INSERT OR REPLACE INTO users (user_id, api_key, api_secret) VALUES (?, ?, ?)", (user_id, api_key, api_secret))
    return jsonify({"status": "ok"})

@app.route("/webhook", methods=["POST"])
def webhook():
    data = request.get_json()
    user_id = data.get("user_id")
    mensagem = data.get("message", "")

    with sqlite3.connect(DB_PATH) as conn:
        result = conn.execute("SELECT api_key, api_secret FROM users WHERE user_id = ?", (user_id,)).fetchone()

    if not result:
        return jsonify({"error": "Usuário não encontrado."}), 404

    api_key, api_secret = result
    client = Client(api_key, api_secret)

    try:
        simbolo = re.search(r"MOEDA:\s*#(\w+/USDT)", mensagem).group(1).replace("/", "")
        direcao = "BUY" if "LONG" in mensagem else "SELL"
        entrada = list(map(float, re.findall(r"ENTRADA EM:\s*([\d.]+)\s*-\s*([\d.]+)", mensagem)[0]))
        preco_entrada = sum(entrada) / 2
        stop_loss = float(re.search(r"StopLoss:\s*([\d.]+)", mensagem).group(1))
        alavancagem = int(re.search(r"ALAVANCAGEM\s*:\s*(\d+)", mensagem).group(1))

        place_order_customizado(client, simbolo, direcao, preco_entrada, stop_loss, alavancagem)

        return jsonify({"status": "ok"})
    except Exception as e:
        return jsonify({"error": str(e)}), 400

if __name__ == "__main__":
    app.run(debug=True)
