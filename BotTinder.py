from telegram.ext import ApplicationBuilder, MessageHandler, filters, CallbackQueryHandler, CommandHandler
from gpt import *
from util import *


#СТАРТ
async def start(update, context):
    dialog.mode = "main"
    text = load_message("main")
    await send_photo(update, context, "main")
    await send_text(update, context, text)
    await show_main_menu(update, context, {
        "start": "Главное меню бота",
        'gpt': 'Задать вопрос чату GPT 🧠',
        "profile": "Генерация Tinder-профиля 😎",
        'message': 'Переписка от вашего имени 😈',
        "opener": "Сообщение для знакомств 🥰",
        'date': 'Переписка со звёздами 🔥'
    })


#GPT
async def gpt(update, context):
    dialog.mode = "gpt"
    text = load_message("gpt")
    await send_photo(update, context, "gpt")
    await send_text(update, context, text)


async def gpt_dialog(update, context):
    text = update.message.text
    prompt = load_prompt("gpt")
    answer = await chatgpt.send_question(prompt, text)
    await send_text(update, context, answer)


#ПЕРЕПИСКА СО ЗВЁЗДАМИ
async def date(update, context):
    dialog.mode = "date"
    text = load_message("date")
    await send_photo(update, context, "date")
    await send_text_buttons(update, context, text, {
        "date_robbi": "Марго Робби",
        "date_zendaya": "Зендея",
        "date_gosling": "Райан Гослинг",
        "date_hardy": "Том Харди",
    })
    dialog.list.clear()  # Очищаем историю при новом выборе


async def date_button(update, context):
    query = update.callback_query
    await query.answer()

    star_data = query.data
    await send_photo(update, context, star_data)
    await send_text(update, context, "Отличный выбор! Пригласите звезду на свидание за 5 сообщений 💫")

    # Загружаем промпт для выбранной звезды
    prompt = load_prompt(star_data)
    chatgpt.set_prompt(prompt)

    # Запоминаем текущую звезду
    dialog.current_star = star_data
    dialog.list.clear()  # Очищаем историю для нового диалога


async def date_dialog(update, context):
    text = update.message.text

    # Сохраняем сообщение пользователя
    dialog.list.append(f"👤 Я: {text}")

    star_names = {
        "date_robbi": "Марго Робби",
        "date_zendaya": "Зендея",
        "date_gosling": "Райан Гослинг",
        "date_hardy": "Том Харди"
    }
    star_name = star_names.get(dialog.current_star, "Звезда")

    my_message = await send_text(update, context, f"⭐ {star_name} печатает...")

    try:
        # Формируем полную историю диалога
        chat_history = "\n".join(dialog.list)

        # Загружаем промпт звезды
        prompt = load_prompt(dialog.current_star)

        # Добавляем историю к промпту
        full_prompt = f"{prompt}\n\nИстория диалога:\n{chat_history}\n\nОтветь как {star_name}:"

        # Получаем ответ от GPT
        answer = await chatgpt.send_question(full_prompt, text)

        # Сохраняем ответ звезды
        dialog.list.append(f"⭐ {star_name}: {answer}")

        # Отправляем ответ пользователю
        await my_message.edit_text(answer)


        if len(dialog.list) >= 10:  # 5 сообщений туда-обратно
            await send_text(update, context, "💫 Диалог завершен. Хочешь поговорить с другой звездой? Напиши /date")
            dialog.mode = "main"

    except Exception as e:
        await my_message.edit_text(f"❌ Ошибка: {e}")


#ПЕРЕПИСКА ОТ ВАШЕГО ИМЕНИ
async def message(update, context):
    dialog.mode = 'message'
    text = load_message('message')
    await send_photo(update, context, "message")
    await send_text_buttons(update, context, text, {
        "message_nest": "Следующее сообщение",
        "message_date": "Пригласить на свидание"
    })
    dialog.list.clear()


async def message_button(update, context):
    query = update.callback_query
    await query.answer()

    button_data = query.data
    prompt = load_prompt(button_data)
    user_chat_history = "\n\n".join(dialog.list)

    my_message = await send_text(update, context, "ChatGPT думает над ответом...")
    answer = await chatgpt.send_question(prompt, user_chat_history)
    await my_message.edit_text(answer)


async def message_dialog(update, context):
    text = update.message.text
    dialog.list.append(text)


#ГЕНЕРАЦИЯ TINDER-ПРОФИЛЯ
async def profile(update, context):
    dialog.mode = "profile"
    text = load_message("profile")
    await send_photo(update, context, "profile")
    await send_text(update, context, text)

    dialog.user.clear()
    dialog.count = 0
    await send_text(update, context, "Сколько вам лет?")


async def profile_dialog(update, context):
    text = update.message.text
    dialog.count += 1

    if dialog.count == 1:
        dialog.user["age"] = text
        await send_text(update, context, "Кем вы работаете?")
    elif dialog.count == 2:
        dialog.user["occupation"] = text
        await send_text(update, context, "У вас есть хобби?")
    elif dialog.count == 3:
        dialog.user["hobby"] = text
        await send_text(update, context, "Что вам не нравится в людях?")
    elif dialog.count == 4:
        dialog.user["annoys"] = text
        await send_text(update, context, "Цели знакомства?")
    elif dialog.count == 5:
        dialog.user["goals"] = text
        prompt = load_prompt("profile")
        user_info = dialog_user_info_to_str(dialog.user)

        my_message = await send_text(update, context,
                                     "ChatGPT занимается генерацией вашего профиля, подождите пару секунд...")
        answer = await chatgpt.send_question(prompt, user_info)
        await my_message.edit_text(answer)
        dialog.mode = "main"


#СООБЩЕНИЕ ДЛЯ ЗНАКОМСТВ
async def opener(update, context):
    dialog.mode = "opener"
    text = load_message("opener")
    await send_photo(update, context, "opener")
    await send_text(update, context, text)

    dialog.user.clear()
    dialog.count = 0
    await send_text(update, context, "Имя девушки?")


async def opener_dialog(update, context):
    text = update.message.text
    dialog.count += 1

    if dialog.count == 1:
        dialog.user["name"] = text
        await send_text(update, context, "Сколько ей лет?")
    elif dialog.count == 2:
        dialog.user["age"] = text
        await send_text(update, context, "Оцените её внешность 1-10 баллов:")
    elif dialog.count == 3:
        dialog.user["handsome"] = text
        await send_text(update, context, "Кем она работает?")
    elif dialog.count == 4:
        dialog.user["occupation"] = text
        await send_text(update, context, "Цель знакомства?")
    elif dialog.count == 5:
        dialog.user["goals"] = text
        prompt = load_prompt("opener")
        user_info = dialog_user_info_to_str(dialog.user)

        answer = await chatgpt.send_question(prompt, user_info)
        await send_text(update, context, answer)
        dialog.mode = "main"


#ОСНОВНОЙ ОБРАБОТЧИК СООБЩЕНИЙ
async def hello(update, context):
    if dialog.mode == "gpt":
        await gpt_dialog(update, context)
    elif dialog.mode == "date":
        await date_dialog(update, context)
    elif dialog.mode == "message":
        await message_dialog(update, context)
    elif dialog.mode == "profile":
        await profile_dialog(update, context)
    elif dialog.mode == "opener":
        await opener_dialog(update, context)
    else:
        await send_text(update, context, "*Привет!*")
        await send_text(update, context, "_Как дела?_")
        await send_text(update, context, "Вы написали " + update.message.text)
        await send_photo(update, context, "avatar_main")
        await send_text_buttons(update, context, "Запустить процесс?", {
            "start": "Запустить",
            "stop": "Остановить"
        })



async def hello_button(update, context):
    query = update.callback_query
    await query.answer()

    if query.data == "start":
        await send_text(update, context, "Процесс запущен")
    else:
        await send_text(update, context, "Процесс остановлен")


#ИНИЦИАЛИЗАЦИЯ
dialog = Dialog()
dialog.mode = None
dialog.list = []
dialog.count = 0
dialog.user = {}
dialog.current_star = None

chatgpt = ChatGptService(
    token="")

#АПУСК БОТА
app = ApplicationBuilder().token("").build()


app.add_handler(CommandHandler("start", start))
app.add_handler(CommandHandler("gpt", gpt))
app.add_handler(CommandHandler("date", date))
app.add_handler(CommandHandler("message", message))
app.add_handler(CommandHandler("profile", profile))
app.add_handler(CommandHandler("opener", opener))


app.add_handler(CallbackQueryHandler(date_button, pattern="^date_.*"))
app.add_handler(CallbackQueryHandler(message_button, pattern="^message_.*"))
app.add_handler(CallbackQueryHandler(hello_button))


app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, hello))

app.run_polling()
