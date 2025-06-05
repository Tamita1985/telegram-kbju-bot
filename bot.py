import telebot
from flask import Flask, request
import os

TOKEN = '7517404462:AAEcuLj0cMavBhlWw_61DJAIMZK89KEtmRY'
bot = telebot.TeleBot(TOKEN)
app = Flask(__name__)

@app.route(f'/{TOKEN}', methods=['POST'])
def webhook():
    update = telebot.types.Update.de_json(request.get_json(force=True))
    bot.process_new_updates([update])
    return '', 200

@app.route('/')
def home():
    return 'Бот запущен! ✅'

@bot.message_handler(commands=['start'])
def start(message):
    bot.send_message(message.chat.id, "Привет! Я работаю. 🎉")

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 10000))
    app.run(host='0.0.0.0', port=port)
