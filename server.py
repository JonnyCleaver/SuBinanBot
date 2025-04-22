from flask import Flask, request, jsonify

app = Flask(__name__)

@app.route("/")
def home():
    return "🏠 Bot está rodando."

@app.route("/configurar_keys", methods=["POST"])
def configurar_keys():
    data = request.json
    print("🔑 Recebido:", data)

    # Aqui você pode salvar essas chaves num banco de dados, etc.
    return jsonify({"status": "ok"}), 200
