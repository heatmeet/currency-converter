from xml.etree import ElementTree

import requests
import telebot

bot = telebot.TeleBot("5799715226:AAGIxO_X_L_fzZOWtcS9-PpU2fWSHRTk8KY")


# Обработчик команды /start
@bot.message_handler(commands=['start'])
def send_welcome(message):
    bot.reply_to(message, "Привет! Я бот для конвертации валют. Введите команду /convert для начала конвертации.")


# Обработчик команды /help
@bot.message_handler(commands=['help'])
def send_help(message):
    bot.reply_to(message,
                 'Я могу конвертировать валюты по курсу ЦБ и обычному курсу. Чтобы узнать курс, введите команду '
                 '/convert:'
                 '/convert [сумма] [валюта1] [валюта2].')


# Обработчик команды /convert
@bot.message_handler(commands=['convert'])
def convert(message):
    try:
        text = message.text.split()
        if len(text) != 4:
            raise ValueError
        amount = float(text[1])
        base = text[2].upper()
        target = text[3].upper()
        if base == target:
            bot.reply_to(message, "Вы ввели одинаковые валюты.")
            return
        url_cbr = "https://www.cbr.ru/scripts/XML_daily.asp"
        response_cbr = requests.get(url_cbr)
        root_cbr = ElementTree.fromstring(response_cbr.content)
        rate_cbr = 1
        for valute in root_cbr.findall('Valute'):
            if valute.find('CharCode').text == base:
                rate_cbr = float(valute.find('Value').text.replace(',', '.'))
                break
        url_normal = f"https://api.exchangerate-api.com/v4/latest/{base}"
        response_normal = requests.get(url_normal)
        rate_normal = response_normal.json()['rates'][target]
        result_cbr = round(amount * rate_cbr, 2)
        result_normal = round(amount * rate_normal, 2)
        bot.reply_to(message,
                     f"{amount} {base} = {result_cbr} RUB (Центральный Банк России) и {result_normal} {target} (обычный"
                     f" курс).")

    # Неверный формат ввода
    except ValueError:
        bot.reply_to(message,
                     "Неверный формат команды. Пожалуйста, введите команду в формате /convert [сумма] [валюта1] [валю"
                     "та2]. Например, /convert 100 USD RUB.")

    # Неверный формат валюты
    except KeyError:
        bot.reply_to(message, "Неверный код валюты. Пожалуйста, введите корректный код валюты.")


bot.polling()
