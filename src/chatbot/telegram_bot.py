import requests
import logging
import uuid
import urllib3
from telegram import Update, ReplyKeyboardMarkup, ReplyKeyboardRemove
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
import os
from dotenv import load_dotenv

# --- 1. НАСТРОЙКИ ---
load_dotenv()

TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
GIGACHAT_CLIENT_SECRET = os.getenv("GIGACHAT_CLIENT_SECRET")
API_BASE_URL = os.getenv("API_BASE_URL", "https://example.com")  # Адрес API берем из .env

if not TELEGRAM_BOT_TOKEN or not GIGACHAT_CLIENT_SECRET:
    raise ValueError("Не найдены токены в .env файле! Убедитесь, что он существует и заполнен.")

GIGACHAT_ACCESS_TOKEN = ""
user_data = {}

QUESTIONS = [
    "Вопрос 1/10: Я чувствую себя эмоционально истощенным(-ой) на работе.",
    "Вопрос 2/10: К концу рабочего дня я чувствую себя как выжатый лимон.",
    "Вопрос 3/10: Утром я чувствую усталость, когда думаю о предстоящей работе.",
    "Вопрос 4/10: Я чувствую, что моя работа выматывает меня.",
    "Вопрос 5/10: Я стал(-а) более черствым(-ой) и циничным(-ой) по отношению к коллегам и клиентам.",
    "Вопрос 6/10: Я с меньшим энтузиазмом отношусь к своей работе, чем раньше.",
    "Вопрос 7/10: Я сомневаюсь в значимости и пользе своей работы.",
    "Вопрос 8/10: Я чувствую, что не добиваюсь значимых результатов в своей работе.",
    "Вопрос 9/10: Мне кажется, что я стал(-а) менее продуктивным(-ой).",
    "Вопрос 10/10: Я чувствую себя подавленным(-ой) и апатичным(-ой) из-за работы."
]

logging.basicConfig(format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO)
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# --- ФУНКЦИИ GIGACHAT ---
def get_giga_access_token():
    global GIGACHAT_ACCESS_TOKEN
    url = "https://ngw.devices.sberbank.ru:9443/api/v2/oauth"
    payload = {'scope': 'GIGACHAT_API_PERS'}
    headers = {
        'Content-Type': 'application/x-www-form-urlencoded',
        'Accept': 'application/json',
        'RqUID': str(uuid.uuid4()),
        'Authorization': GIGACHAT_CLIENT_SECRET
    }
    try:
        response = requests.post(url, headers=headers, data=payload, verify=False)
        response.raise_for_status()
        GIGACHAT_ACCESS_TOKEN = response.json()['access_token']
        logging.info("Токен GigaChat успешно получен!")
        return True
    except requests.exceptions.RequestException as e:
        logging.error(f"Не удалось получить токен GigaChat: {e}")
        return False


async def get_ai_recommendation(user_prompt: str) -> str:
    """
    Отправляет промпт в GigaChat и возвращает ответ нейросети.
    """
    url = "https://gigachat.devices.sberbank.ru/api/v1/chat/completions"

    headers = {
        'Content-Type': 'application/json',
        'Authorization': f'Bearer {GIGACHAT_ACCESS_TOKEN}'
    }

    payload = {
        "model": "GigaChat-2-Pro",
        "messages": [
            {
                "role": "user",
                "content": user_prompt
            }
        ],
        "temperature": 0.7
    }

    try:
        response = requests.post(url, headers=headers, json=payload, verify=False)
        response.raise_for_status()
        return response.json()['choices'][0]['message']['content']
    except requests.exceptions.RequestException as e:
        logging.error(f"Ошибка при обращении к GigaChat: {e}")
        return "К сожалению, не удалось получить рекомендацию от ИИ. Попробуйте позже."
    except (KeyError, IndexError) as e:
        logging.error(f"Не удалось разобрать ответ от GigaChat: {e}")
        return "Получен некорректный ответ от сервиса ИИ."


# --- ОТПРАВКА РЕЗУЛЬТАТОВ В API ---
async def send_survey_result(user_id: int, answers: list[int], total_score: int):
    url = f"{API_BASE_URL}/surveys"
    payload = {
        "id": user_id,
        "type": "base",
        "active": True,
        "json": {
            "ans": answers,
            "sum": total_score
        }
    }
    try:
        response = requests.post(url, json=payload)
        response.raise_for_status()
        logging.info(f"Результаты опроса пользователя {user_id} отправлены успешно.")
    except requests.exceptions.RequestException as e:
        logging.error(f"Ошибка при отправке результатов на API: {e}")


def get_department_stats_from_db() -> str:
    logging.info("Запрошена статистика (симуляция обращения к БД).")
    return (
        "http://10.106.21.221:5000/dashboard"
    )

# --- ОБРАБОТЧИКИ ---
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user_id = update.effective_user.id
    user_data[user_id] = {'stage': 'awaiting_role'}
    reply_keyboard = [["Я — Начальник"], ["Я — Работник"]]
    await update.message.reply_text(
        "Здравствуйте! Пожалуйста, укажите вашу роль:",
        reply_markup=ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True, resize_keyboard=True),
    )

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user_id = update.effective_user.id
    text = update.message.text

    if user_id not in user_data:
        await start(update, context)
        return

    current_stage = user_data[user_id].get('stage')

    if current_stage == 'awaiting_role':
        if text == "Я — Начальник":
            user_data[user_id]['stage'] = 'manager_menu'
            stats = get_department_stats_from_db()
            await update.message.reply_text(stats, reply_markup=ReplyKeyboardRemove(), parse_mode='Markdown')
            await update.message.reply_text("Для возврата в главное меню, введите /start")

        elif text == "Я — Работник":
            user_data[user_id]['stage'] = 'employee_welcome'
            reply_keyboard = [["Да, хочу пройти опрос"], ["Нет, спасибо"]]
            await update.message.reply_text(
                "Отлично! Хотите пройти короткий опрос из 10 вопросов?",
                reply_markup=ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True, resize_keyboard=True),
            )
        else:
            await update.message.reply_text("Пожалуйста, выберите один из вариантов.")

    elif current_stage == 'employee_welcome':
        if text == "Да, хочу пройти опрос":
            user_data[user_id]['stage'] = 'quiz'
            user_data[user_id]['score'] = 0
            user_data[user_id]['question_index'] = 0
            user_data[user_id]['answers'] = []
            await update.message.reply_text("Оцени каждое утверждение от 1 до 10.", reply_markup=ReplyKeyboardRemove())
            await update.message.reply_text(QUESTIONS[0])
        else:
            await update.message.reply_text("Хорошо. Если передумаете, просто напишите /start.", reply_markup=ReplyKeyboardRemove())
            del user_data[user_id]

    elif current_stage == 'quiz':
        try:
            answer = int(text)
            if not 1 <= answer <= 10: raise ValueError
        except ValueError:
            await update.message.reply_text("Введите число от 1 до 10.")
            return

        user_data[user_id]['answers'].append(answer)
        user_data[user_id]['score'] += answer
        user_data[user_id]['question_index'] += 1
        q_index = user_data[user_id]['question_index']

        if q_index < len(QUESTIONS):
            await update.message.reply_text(QUESTIONS[q_index])
        else:
            await finish_quiz(update, context)


async def send_survey_result(user_id: int, anket_type: str, visible: bool, answers: list[int], total_score: int):
    """
    Отправляет результаты в API для сохранения в БД surveys
    """
    url = f"{API_BASE_URL}/surveys"

    payload = {
        "user_id": 1,        # FK на таблицу users
        "anket_type": anket_type,  # тип анкеты ('base')
        "visible": True,        # видимость
        "answers": {
            "ans": answers,        # список ответов
            "sum": total_score     # сумма баллов
        }
    }

    try:
        # Важно! Если API принимает JSON — используем json=payload
        response = requests.post(url, json=payload)
        response.raise_for_status()
        logging.info(f"Результаты для user_id={user_id} отправлены успешно.")
    except requests.exceptions.RequestException as e:
        logging.error(f"Ошибка при отправке результатов: {e}")



async def finish_quiz(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # Здесь можно оставить реальный update.effective_user.id
    user_id =update.effective_user.id
    visible = True
    anket_type = 'base'

    answers = user_data[user_id]['answers']  # список чисел [1..10]
    total_score = user_data[user_id]['score']

    result_message = ""

    if 10 <= total_score <= 39:
        await update.message.reply_text("Анализирую ваши результаты...")
        prompt = f"Ты — цифровой помощник... Пользователь набрал {total_score} баллов."
        ai_advice = await get_ai_recommendation(prompt)
        result_message = f"Ваш результат: {total_score} баллов.\n\n{ai_advice}"

    elif 40 <= total_score <= 70:
        await update.message.reply_text("Анализирую ваши результаты...")
        prompt = f"Ты — цифровой помощник... Пользователь набрал {total_score} баллов."
        ai_advice = await get_ai_recommendation(prompt)
        result_message = f"Ваш результат: {total_score} баллов.\n\n{ai_advice}"

    elif 71 <= total_score <= 100:
        result_message = "Высокий уровень стресса. Рекомендуется обратиться к специалисту."

    await update.message.reply_text(result_message, reply_markup=ReplyKeyboardRemove())
    await update.message.reply_text("Спасибо за участие! Чтобы начать заново, введите /start")

    # Отправляем в API в формате JSONB для таблицы surveys
    await send_survey_result(user_id, anket_type, visible, answers, total_score)

    if user_id in user_data:
        del user_data[user_id]



# --- ЗАПУСК ---
def main() -> None:
    if not get_giga_access_token():
        logging.error("Не удалось получить токен GigaChat. Бот не запущен.")
        return

    application = Application.builder().token(TELEGRAM_BOT_TOKEN).build()
    application.add_handler(CommandHandler("start", start))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    logging.info("Бот запущен и готов к работе...")
    application.run_polling()

if __name__ == "__main__":
    main()