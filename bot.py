import os
import asyncio
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ConversationHandler, ContextTypes
import requests

API_KEY, API_SECRET = range(2)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Bem-vindo! Use /configurar para enviar sua API Key da Binance.")

async def configurar(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Digite sua API Key:")
    return API_KEY

async def receber_api_key(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data['api_key'] = update.message.text
    await update.message.reply_text("Agora envie sua API Secret:")
    return API_SECRET

async def receber_api_secret(update: Update, context: ContextTypes.DEFAULT_TYPE):
    api_key = context.user_data['api_key']
    api_secret = update.message.text
    user_id = update.effective_user.id

    url = "https://subinanbot.onrender.com/configurar_keys"
    response = requests.post(url, json={
        "user_id": user_id,
        "api_key": api_key,
        "api_secret": api_secret
    })

    if response.status_code == 200:
        await update.message.reply_text("✅ Chaves configuradas com sucesso!")
    else:
        await update.message.reply_text("❌ Erro ao salvar suas chaves.")
    return ConversationHandler.END

async def cancelar(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Configuração cancelada.")
    return ConversationHandler.END

async def main():
    # Crie a instância do bot e inicie o polling
    app = Application.builder().token(os.getenv("BOT_TOKEN")).build()

    conv_handler = ConversationHandler(
        entry_points=[CommandHandler("configurar", configurar)],
        states={API_KEY: [MessageHandler(filters.TEXT & ~filters.COMMAND, receber_api_key)],
                API_SECRET: [MessageHandler(filters.TEXT & ~filters.COMMAND, receber_api_secret)]},
        fallbacks=[CommandHandler("cancelar", cancelar)],
    )

    app.add_handler(CommandHandler("start", start))
    app.add_handler(conv_handler)

    # Isso vai rodar o polling do bot
    await app.run_polling()

if __name__ == "__main__":
    asyncio.run(main())
