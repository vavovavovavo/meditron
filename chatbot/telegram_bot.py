import requests
import logging
import uuid
import urllib3
from telegram import Update, ReplyKeyboardMarkup, ReplyKeyboardRemove
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
import os
from dotenv import load_dotenv

load_dotenv() # Загружаем переменные из файла .env

# --- 1. НАСТРОЙКИ: БЕРЕМ ДАННЫЕ ИЗ ОКРУЖЕНИЯ ---
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
GIGACHAT_CLIENT_SECRET = os.getenv("GIGACHAT_CLIENT_SECRET")

# Проверка, что ключи загрузились
if not TELEGRAM_BOT_TOKEN or not GIGACHAT_CLIENT_SECRET:
    raise ValueError("Не найдены токены в .env файле! Скопируйте .env.example в .env и заполните его.")

# Глобальная переменная для хранения токена GigaChat
GIGACHAT_ACCESS_TOKEN = ""

# --- ЛОГИКА АГЕНТА ---

# Словарь для хранения состояния каждого пользователя
user_data = {}

# Вопросы для опросника
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

# Настройка логирования для отладки
logging.basicConfig(format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO)
# Отключаем предупреждения о небезопасном SSL-соединении
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# --- ФУНКЦИИ ДЛЯ РАБОТЫ С API GIGACHAT ---

def get_giga_access_token():
    """Получает новый токен доступа для GigaChat."""
    global GIGACHAT_ACCESS_TOKEN
    url = "https://ngw.devices.sberbank.ru:9443/api/v2/oauth"
    payload = {'scope': 'GIGACHAT_API_PERS'}
    headers = {
        'Content-Type': 'application/x-www-form-urlencoded',
        'Accept': 'application/json',
        'RqUID': str(uuid.uuid4()),  # Генерируем уникальный ID для каждого запроса токена
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

# --- ФУНКЦИИ-ОБРАБОТЧИКИ ДЛЯ TELEGRAM ---

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Обработчик команды /start."""
    user_id = update.effective_user.id
    user_data[user_id] = {'stage': 'welcome', 'score': 0, 'question_index': 0}
    reply_keyboard = [["Да, хочу пройти опрос"], ["Нет, спасибо"]]
    await update.message.reply_text(
        "Привет! Я — твой персональный ассистент по ментальному здоровью.\n\n"
        "Хочешь пройти короткий опрос из 10 вопросов, чтобы лучше понять свой текущий уровень профессионального выгорания?",
        reply_markup=ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True, resize_keyboard=True),
    )

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Основной обработчик сообщений, который ведет пользователя по логике."""
    user_id = update.effective_user.id
    text = update.message.text

    if user_id not in user_data:
        await start(update, context)
        return

    current_stage = user_data[user_id]['stage']

    if current_stage == 'welcome':
        if text == "Да, хочу пройти опрос":
            user_data[user_id]['stage'] = 'quiz'
            await update.message.reply_text(
                "Отлично! Оцени каждое утверждение по шкале от 1 до 10, где 1 — «совсем не согласен», а 10 — «полностью согласен».",
                reply_markup=ReplyKeyboardRemove()
            )
            await update.message.reply_text(QUESTIONS[0])
        else:
            await update.message.reply_text("Хорошо. Если передумаешь, просто напиши /start.", reply_markup=ReplyKeyboardRemove())
            del user_data[user_id]

    elif current_stage == 'quiz':
        try:
            answer = int(text)
            if not 1 <= answer <= 10: raise ValueError
        except ValueError:
            await update.message.reply_text("Пожалуйста, введи число от 1 до 10.")
            return

        user_data[user_id]['score'] += answer
        user_data[user_id]['question_index'] += 1
        q_index = user_data[user_id]['question_index']

        if q_index < len(QUESTIONS):
            await update.message.reply_text(QUESTIONS[q_index])
        else:
            await finish_quiz(update, context)

async def finish_quiz(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Подводит итоги и отправляет результат."""
    user_id = update.effective_user.id
    total_score = user_data[user_id]['score']
    result_message = ""

    if 10 <= total_score <= 39:
        result_message = (
            "Спасибо за твои ответы! По результатам опросника, твой уровень стресса находится в норме. "
            "Это отличный результат! Продолжай в том же духе, заботься о себе и сохраняй баланс между работой и личной жизнью."
        )
    elif 40 <= total_score <= 70:
        result_message = (
            "Спасибо, что поделился(-ась) своими ощущениями. Результаты показывают, что ты находишься в зоне риска профессионального выгорания. "
            "Важно обратить на это внимание сейчас, чтобы не допустить ухудшения состояния.\n\n"
            "Я рекомендую тебе попробовать простые, но эффективные практики:\n"
            "• **Дыхательные практики:** 5 минут глубокого дыхания.\n"
            "• **Йога и медитации:** Помогают снизить уровень стресса.\n"
            "• **Здоровый сон:** Старайся спать 7-8 часов.\n"
            "• **Цифровой детокс:** Ограничь гаджеты перед сном."
        )
    elif 71 <= total_score <= 100:
        result_message = (
            "Спасибо за твою откровенность. Результаты опросника показывают высокий уровень стресса и симптомы сильного профессионального выгорания. "
            "Это серьезный сигнал, который нельзя игнорировать.\n\n"
            "В такой ситуации лучшим решением будет обратиться за поддержкой к специалисту — психологу или психотерапевту. Он поможет разобраться в причинах и разработает план помощи."
            # Опцию с отчетом начальству пока убрал для простоты
        )

    await update.message.reply_text(result_message)
    # Сбрасываем состояние пользователя после завершения теста
    del user_data[user_id]

def main() -> None:
    """Основная функция запуска бота."""
    # Сначала пытаемся получить токен GigaChat
    if not get_giga_access_token():
        logging.error("Не удалось запустить бота: не получен токен GigaChat. Проверьте ваш GIGACHAT_CLIENT_SECRET.")
        return

    # Создаем приложение
    application = Application.builder().token(TELEGRAM_BOT_TOKEN).build()

    # Добавляем обработчики
    application.add_handler(CommandHandler("start", start))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    # Запускаем бота (он будет работать, пока не остановишь его вручную)
    logging.info("Бот запущен и готов к работе...")
    application.run_polling()

if __name__ == "__main__":
    main()