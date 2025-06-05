import telebot
from telebot import types
from flask import Flask, request

TOKEN = '7517404462:AAEcuLj0cMavBhlWw_61DJAIMZK89KEtmRY'
bot = telebot.TeleBot(TOKEN)
app = Flask(__name__)

user_data = {}

def main_menu():
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add("🔢 Рассчитать КБЖУ")
    return markup

def back_button():
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add("⬅️ Вернуться НАЗАД")
    return markup

@bot.message_handler(commands=['start'])
@bot.message_handler(func=lambda message: message.text == "🔢 Рассчитать КБЖУ")
def start(message):
    user_data[message.chat.id] = {}
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add('М', 'Ж')
    bot.send_message(message.chat.id, "👋 Привет! Давай рассчитаем твои КБЖУ.\n\nВыбери пол:", reply_markup=markup)
    bot.register_next_step_handler(message, get_gender)

def get_gender(message):
    if message.text not in ['М', 'Ж']:
        bot.send_message(message.chat.id, "❌ Пожалуйста, выбери пол из предложенных вариантов.", reply_markup=back_button())
        return bot.register_next_step_handler(message, get_gender)
    user_data[message.chat.id]['gender'] = message.text
    bot.send_message(message.chat.id, "🎂 Введите возраст:", reply_markup=back_button())
    bot.register_next_step_handler(message, get_age)

def get_age(message):
    if not message.text.isdigit():
        bot.send_message(message.chat.id, "❌ Возраст должен быть числом.", reply_markup=back_button())
        return bot.register_next_step_handler(message, get_age)
    user_data[message.chat.id]['age'] = int(message.text)
    bot.send_message(message.chat.id, "📏 Введите рост (в см):", reply_markup=back_button())
    bot.register_next_step_handler(message, get_height)

def get_height(message):
    if not message.text.isdigit():
        bot.send_message(message.chat.id, "❌ Рост должен быть числом.", reply_markup=back_button())
        return bot.register_next_step_handler(message, get_height)
    user_data[message.chat.id]['height'] = int(message.text)
    bot.send_message(message.chat.id, "⚖️ Введите вес (в кг):", reply_markup=back_button())
    bot.register_next_step_handler(message, get_weight)

def get_weight(message):
    try:
        weight = float(message.text.replace(",", "."))
    except ValueError:
        bot.send_message(message.chat.id, "❌ Вес должен быть числом.", reply_markup=back_button())
        return bot.register_next_step_handler(message, get_weight)
    user_data[message.chat.id]['weight'] = weight
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add('1.2', '1.375', '1.55', '1.725', '1.9')

    activity_text = (
        "🏃 Выберите коэффициент активности:\n\n"
        "🔹 1.2 — Минимальная активность\n< 5 000 шагов, нет тренировок, сидячая работа\n\n"
        "🔹 1.375 — Лёгкая активность\n5 000–8 000 шагов, 1–2 лёгкие тренировки в неделю\n\n"
        "🔹 1.55 — Средняя активность\n8 000–12 000 шагов, 3–4 силовые тренировки\n\n"
        "🔹 1.725 — Высокая активность\n12 000–15 000 шагов, 5–6 тяжёлых тренировок\n\n"
        "🔹 1.9 — Очень высокая активность\n15 000+ шагов, 2 тренировки в день или тяжёлая работа"
    )

    bot.send_message(message.chat.id, activity_text, reply_markup=markup)
    bot.register_next_step_handler(message, get_activity)

def get_activity(message):
    try:
        activity = float(message.text)
        if activity not in [1.2, 1.375, 1.55, 1.725, 1.9]:
            raise ValueError
    except ValueError:
        bot.send_message(message.chat.id, "❌ Выберите коэффициент из списка.", reply_markup=back_button())
        return bot.register_next_step_handler(message, get_activity)
    user_data[message.chat.id]['activity'] = activity
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add('похудение', 'поддержание', 'набор')
    bot.send_message(message.chat.id, "🎯 Выберите цель:", reply_markup=markup)
    bot.register_next_step_handler(message, get_goal)

def get_goal(message):
    goal = message.text
    if goal not in ['похудение', 'поддержание', 'набор']:
        bot.send_message(message.chat.id, "❌ Выберите цель из списка.", reply_markup=back_button())
        return bot.register_next_step_handler(message, get_goal)
    user_data[message.chat.id]['goal'] = goal

    if goal in ['похудение', 'набор']:
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
        markup.add('мягкий (10%)', 'умеренный (15%)', 'агрессивный (20%)')
        text = "📉 Выберите уровень " + ("дефицита:" if goal == "похудение" else "профицита:")
        bot.send_message(message.chat.id, text, reply_markup=markup)
        bot.register_next_step_handler(message, get_deficit)
    else:
        calculate_kbju(message)

def get_deficit(message):
    percent_map = {
        'мягкий (10%)': 0.10,
        'умеренный (15%)': 0.15,
        'агрессивный (20%)': 0.20
    }
    if message.text not in percent_map:
        bot.send_message(message.chat.id, "❌ Выберите вариант из предложенных.", reply_markup=back_button())
        return bot.register_next_step_handler(message, get_deficit)
    user_data[message.chat.id]['percent'] = percent_map[message.text]
    calculate_kbju(message)

def calculate_kbju(message):
    data = user_data[message.chat.id]
    gender = data['gender']
    age = data['age']
    height = data['height']
    weight = data['weight']
    activity = data['activity']
    goal = data['goal']
    percent = data.get('percent', 0)

    bmr = 10 * weight + 6.25 * height - 5 * age + (5 if gender == 'М' else -161)
    tdee = bmr * activity
    if goal == 'похудение':
        tdee *= (1 - percent)
    elif goal == 'набор':
        tdee *= (1 + percent)

    protein_factors = {1.2: 1.5, 1.375: 1.8, 1.55: 2.0, 1.725: 2.1, 1.9: 2.2}
    protein = round(weight * protein_factors[activity])
    fat = round(weight * 1)
    protein_kcal = protein * 4
    fat_kcal = fat * 9
    calories = round(tdee)
    carbs = round((calories - protein_kcal - fat_kcal) / 4)

    result = (
        f"📊 *Твои КБЖУ:*\n\n"
        f"🔥 Калории: {calories} ккал\n"
        f"🥩 Белки: {protein} г\n"
        f"🥑 Жиры: {fat} г\n"
        f"🍚 Углеводы: {carbs} г"
    )

    bot.send_message(message.chat.id, result, parse_mode='Markdown', reply_markup=main_menu())

@app.route(f"/{TOKEN}", methods=['POST'])
def receive_update():
    update = telebot.types.Update.de_json(request.get_json(force=True))
    bot.process_new_updates([update])
    return '', 200

@app.route('/')
def home():
    return 'Бот работает! ✅'

if __name__ == "__main__":
    bot.remove_webhook()
    bot.set_webhook(url=f"https://telegram-kbju-bot.onrender.com/{TOKEN}")
    app.run(host="0.0.0.0", port=10000)
