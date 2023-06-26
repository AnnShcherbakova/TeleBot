import telebot
import requests
import json
from config import keys, TOKEN

TOKEN = "5949452775:AAGh9gVXNBUVKKBEJidaYRcqU8ORP8ceyx4"
bot = telebot.TeleBot(TOKEN)


class APIException(Exception):
    pass


class CryptoConverter:
    @staticmethod
    def get_price(base: str, quote: str, amount: str):
        if quote == base:
            raise APIException(f'Введите различные валюты: {base}.')

        try:
            base_ticker = keys[base]
        except KeyError:
            raise APIException(f'Не удалось обработать валюту {base}')

        try:
            quote_ticker = keys[quote]
        except KeyError:
            raise APIException(f'Не удалось обработать валюту {quote}')

        try:
            amount = float(amount)
        except ValueError:
            raise APIException(f'Не удалось обработать количество {amount}')

        url = f'https://min-api.cryptocompare.com/data/price?fsym={quote_ticker}&tsyms={base_ticker}'
        response = requests.get(url)
        response.raise_for_status()

        try:
            data = json.loads(response.content)
            total_base = data[base_ticker]
        except (ValueError, KeyError):
            raise APIException('Ошибка при обработке данных')

        return total_base


@bot.message_handler(commands=['start', 'help'])
def help(message: telebot.types.Message):
    text = 'Для начала работы введите команду в следующем формате (через пробел):\n' \
           '- <Название валюты, цену которой Вы хотите узнать>\n' \
           '- <Название валюты, в которой Вы хотите узнать цену первой валюты>\n' \
           '- <Количество первой валюты>\n' \
           'Список доступных валют: /values'
    bot.reply_to(message, text)


@bot.message_handler(commands=['values'])
def values(message: telebot.types.Message):
    try:
        currency_list = '\n'.join(keys.keys())
        text = f'Доступные валюты:\n{currency_list}'
    except Exception as e:
        text = 'Ошибка при получении списка доступных валют'
        print(f'Error in values function: {e}')

    bot.reply_to(message, text)


@bot.message_handler(content_types=['text'])
def get_price(message: telebot.types.Message):
    try:
        values = message.text.split(' ')

        if len(values) != 3:
            raise APIException('Параметры введены неверно')

        base, quote, amount = values
        total_base = CryptoConverter.get_price(base, quote, amount)
        text = f'Цена {amount} {base} в {quote}: {total_base}'
        bot.send_message(message.chat.id, text)
    except APIException as e:
        bot.reply_to(message, f'Ошибка пользователя: {e}')
    except Exception as e:
        bot.reply_to(message, f'Произошла ошибка: {e}')


bot.polling(none_stop=True)
