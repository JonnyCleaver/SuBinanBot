import os
from flask import Flask, request, jsonify
from telegram import Update, Bot
from telegram.ext import Dispatcher, CommandHandler, MessageHandler, filters, ConversationHandler, ContextTypes

# Estados da ConversationHandler
API_KEY, API_SECRET = range(2)

app = Flask(__name__)

# Instancia o bot e o dispatcher
BOT_TOKEN = os.getenv("BOT_TOKEN", "YOUR_BOT_TOKEN")
bot = Bot(token=BOT_TOKEN)
dispatcher = Dispatcher(bot, None, workers=4, use_context=True)

# ------- Handlers do Telegram ------- #

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Bem‑vindo! Use /configurar para enviar sua API Key da Binance."
    )

async def configurar(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Digite sua API Key:")
    return API_KEY

async def receber_api_key(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data['api_key'] = update.message.text
    await update.message.reply_text("Agora, envie sua API Secret:")
    return API_SECRET

async def receber_api_secret(update: Update, context: ContextTypes.DEFAULT_TYPE):
    api_key = context.user_data['api_key']
    api_secret = update.message.text
    user_id = update.effective_user.id

    # POST para seu endpoint salvar chaves
    requests.post(
        "https://seu-dominio.onrender.com/configurar_keys",
        json={"user_id": user_id, "api_key": api_key, "api_secret": api_secret}
    )
    await update.message.reply_text("✅ Chaves configuradas com sucesso!")
    return ConversationHandler.END

async def cancelar(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Configuração cancelada.")
    return ConversationHandler.END

# ConversationHandler para receber key/secret
conv = ConversationHandler(
    entry_points=[CommandHandler("configurar", configurar)],
    states={
        API_KEY: [MessageHandler(filters.TEXT & ~filters.COMMAND, receber_api_key)],
        API_SECRET: [MessageHandler(filters.TEXT & ~filters.COMMAND, receber_api_secret)],
    },
    fallbacks=[CommandHandler("cancelar", cancelar)],
)

# Registra os handlers no dispatcher
dispatcher.add_handler(CommandHandler("start", start))
dispatcher.add_handler(conv)

# ------- Endpoints Flask ------- #

@app.route('/')
def healthcheck():
    return "🤖 Bot e Flask no ar!"

@app.route('/webhook', methods=['POST'])
def webhook():
    """Recebe atualizações do Telegram via webhook e passa pro dispatcher."""
    data = request.get_json(force=True)
    update = Update.de_json(data, bot)
    dispatcher.process_update(update)
    return jsonify({"status": "ok"})

@app.route('/configurar_keys', methods=['POST'])
def configurar_keys():
    """Aqui você salva as API Keys recebidas em um DB ou dicionário."""
    payload = request.json
    user_id = payload["user_id"]
    api_key = payload["api_key"]
    api_secret = payload["api_secret"]
    # Exemplo: armazena em memória
    app.config.setdefault("CHAVES", {})[user_id] = {
        "api_key": api_key,
        "api_secret": api_secret
    }
    return jsonify({"status": "salvo"}), 200

if __name__ == "__main__":
    # Antes de subir, configure o webhook no Telegram:
    # https://api.telegram.org/bot<YOUR_BOT_TOKEN>/setWebhook?url=https://seu-dominio.onrender.com/webhook
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 10000)))
