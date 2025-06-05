import telebot
from flask import Flask, request

# 🔐 Вставь сюда свой токен от BotFather
TOKEN = '7517404462:AAEcuLj0cMavBhlWw_61DJAIMZK89KEtmRY'
bot = telebot.TeleBot(TOKEN)
app = Flask(__name__)

# 👉 Обработка команды /start
@bot.message_handler(commands=['start'])
def start(message):
    bot.send_message(message.chat.id, "Привет! Я работаю. 🎉")

# 👉 Обработка вебхуков от Telegram
@app.route(f'/{TOKEN}', methods=['POST'])
def webhook():
    update = telebot.types.Update.de_json(request.get_json(force=True))
    bot.process_new_updates([update])
    return '', 200

# 👉 Проверка на главной странице (для Render)
@app.route('/')
def home():
    return 'Бот запущен! ✅'

# 👉 Запуск
if __name__ == '__main__':
    bot.remove_webhook()
    bot.set_webhook(url=f'https://PoKrasoteEat_bot.onrender.com/{TOKEN}')  # 👈 заменим позже
    app.run(host='0.0.0.0', port=10000)
