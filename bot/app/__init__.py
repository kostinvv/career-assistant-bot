import logging
import requests
from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, ContextTypes, ConversationHandler, filters

# Включаем логирование
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Константы состояний
CHOOSING_TOPIC, ASKING_QUESTION = range(2)

# Храним состояние по chat_id
user_sessions = {}

API_URL = "http://localhost:80/api"

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    response = requests.get(f"{API_URL}/topics")
    topics = response.json()

    keyboard = [[t["name"]] for t in topics]
    context.user_data["topics_map"] = {t["name"]: t["id"] for t in topics}

    await update.message.reply_text(
        "Привет! Выбери топик для начала:",
        reply_markup=ReplyKeyboardMarkup(keyboard, one_time_keyboard=True)
    )
    return CHOOSING_TOPIC

async def choose_topic(update: Update, context: ContextTypes.DEFAULT_TYPE):
    topic_name = update.message.text
    topic_id = context.user_data["topics_map"].get(topic_name)
    logging.info(f"Topic chosen: {topic_name}")
    logging.info(f"Topic Id: {topic_id}")

    if not topic_id:
        await update.message.reply_text("Топик не найден. Попробуй снова.")
        return CHOOSING_TOPIC

    # Создаём сессию
    resp = requests.post(f"{API_URL}/sessions", json={"topic_id": topic_id})
    session = resp.json()

    context.user_data["session_id"] = session["session_id"]
    context.user_data["question_id"] = session["question_id"]

    # Получаем текст вопроса
    first_question = session["text"]
    await update.message.reply_text(f"Вопрос: {first_question}")
    return ASKING_QUESTION

async def handle_answer(update: Update, context: ContextTypes.DEFAULT_TYPE):
    answer = update.message.text
    session_id = context.user_data["session_id"]
    question_id = context.user_data["question_id"]

    payload = {"question_id": question_id, "answer": answer}
    resp = requests.post(f"{API_URL}/sessions/{session_id}/interactions", json=payload)
    data = resp.json()

    # Отправляем ответ от AI.
    await update.message.reply_text(f"AI: {data['ai_response']}")

    # Если есть следующий вопрос.
    next_q = data.get("next_question")
    if next_q:
        context.user_data["question_id"] = next_q["id"]
        await update.message.reply_text(f"Следующий вопрос: {next_q['text']}")
        return ASKING_QUESTION

# Команда /cancel
async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Сессия завершена.")
    return ConversationHandler.END

def main():
    app = ApplicationBuilder().token("7513748711:AAEgVYfopKJaRn02O5Nex24NA-AQj0Vrwv0").build()

    conv_handler = ConversationHandler(
        entry_points=[CommandHandler("start", start)],
        states={
            CHOOSING_TOPIC: [MessageHandler(filters.TEXT & ~filters.COMMAND, choose_topic)],
            ASKING_QUESTION: [MessageHandler(filters.TEXT & ~filters.COMMAND, handle_answer)],
        },
        fallbacks=[CommandHandler("cancel", cancel)],
    )

    app.add_handler(conv_handler)
    app.run_polling()

if __name__ == "__main__":
    main()