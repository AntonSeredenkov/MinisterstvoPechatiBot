import telebot
from telebot import types
import config as conf
import re

bot = telebot.TeleBot(conf.bot_token)


# Старт бота/приветствие пользователя
@bot.message_handler(commands=['start'])
def start(message):
    bot.send_message(message.chat.id, "Доброго времени суток! Данный бот предназначен для заказа продукции в "
                                      "\"Министерстве печати и штампов\".\nВы можете ознакомится с нашей продукцией "
                                      "при помощи команды \n/makets\nДля того, чтобы узнать какие необходимы документы "
                                      "для заказа, Вы можете использовать команду \n/documents\nДля того, чтобы узнать "
                                      "где расположены наши офисы, Вы можете ввести \n/address\n\nПосле того, "
                                      "как вы выбрали товар и узнали все необходимые документы, Вы можете сделать "
                                      "заказ, при помощи команды /order")


# Бот отправялет картинку со списком документов
@bot.message_handler(commands=['documents'])
def send_documents(message):
    bot.send_message(message.chat.id, "Ознакомьтесь со списком документов")
    photo_address = open("images/documents/documents.jpg", "rb")
    bot.send_photo(message.chat.id, photo_address)
    photo_address.close()


# Обработчик команды /макеты. Должен давать список кнопок с макета. Дальнейшая обработка проходит ниже.
@bot.message_handler(commands=['makets'])
def print_layouts(message):
    markup = types.InlineKeyboardMarkup(row_width=2)
    items = []
    for i in range(len(conf.button_name)):
        items.append(types.InlineKeyboardButton(conf.button_name[i], callback_data=conf.button_name[i]))
        markup.add(items[i])
    bot.send_message(message.chat.id, 'Выберите нужный Вам макет. Обратите внимание у каждого макета есть имя ('
                                      'указано под ценой)!', reply_markup=markup)


# Обработчик кнопок связанных с макетами
@bot.callback_query_handler(func=lambda call: True)
def message_reply(call):
    if call.message:
        bot.send_message(call.message.chat.id, f"===Макеты \"{call.data}\"===")
        if call.data == "ИП":
            photo_address_1 = open(f"./images/documents/ИП1.jpg", "rb")
            photo_address_2 = open(f"./images/documents/ИП2.jpg", "rb")
            bot.send_photo(call.message.chat.id, photo_address_1)
            bot.send_photo(call.message.chat.id, photo_address_2)
            photo_address_1.close()
            photo_address_2.close()
        elif call.data == "ООО":
            photo_address_1 = open(f"./images/documents/ООО1.jpg", "rb")
            photo_address_2 = open(f"./images/documents/ООО2.jpg", "rb")
            bot.send_photo(call.message.chat.id, photo_address_1)
            bot.send_photo(call.message.chat.id, photo_address_2)
            photo_address_1.close()
            photo_address_2.close()
        else:
            photo_address = open(f"./images/documents/{call.data}.jpg", "rb")
            bot.send_photo(call.message.chat.id, photo_address)
            photo_address.close()
    return


@bot.message_handler(commands=['address'])
def print_address(message):
    bot.send_message(message.chat.id, 'Посмотрите на все наши офисы в городе.')
    photo_address_1 = open("images/address/Офис на Чернышевского.png", "rb")
    photo_address_2 = open("./images/address/Офис на Адмиралтейской.png", "rb")
    photo_address_3 = open("./images/address/Офис на Кирова.png", "rb")
    bot.send_photo(message.chat.id, photo_address_1, caption="Телефон:\n+79881734585\n\nПочта: 434585@gmail.com")
    bot.send_photo(message.chat.id, photo_address_2, caption="Телефон:\n+79881724535\n\nПочта: t424535@gmail.com")
    bot.send_photo(message.chat.id, photo_address_3, caption="Телефон:\n+79881734535\n\nПочта: t434535@gmail.com")
    photo_address_1.close()
    photo_address_2.close()
    photo_address_3.close()


@bot.message_handler(commands=['order'])
def make_order(message):
    msg = bot.send_message(message.chat.id,
                           "Вы уверены, что готовы сделать заказ? Перед началом рекомендуем ознакомится с макетами и "
                           "всеми необходимыми документами при помощи следующих команд:\n /documents - выводит список"
                           " всех необходимых документов \n/makets - выводит набор макетов\n\nВ ответе указать \"Да\""
                           " или \"Нет\"")
    bot.register_next_step_handler(msg, check_answer)


def check_answer(message):
    if message.text == "Да":
        begin_order(message)
    else:
        return


def begin_order(message):
    msg = bot.send_message(message.chat.id, 'Введите своё имя')
    bot.register_next_step_handler(msg, get_name)


def get_name(message):
    if message.content_type == "text":
        bot.forward_message(conf.resender, message.chat.id, message.id)  # ОТПРАВКА ИМЕНИ В ДРУГОЙ ЧАТ
        msg = bot.send_message(message.chat.id, "Введите номер телефона, чтобы наши сотрудники могли с вами связаться, "
                                                "если возникнут вопросы")
        bot.register_next_step_handler(msg, get_phone_number)
    else:
        msg = bot.send_message(message.chat.id, "Вы неправильно ввели имя, повторите ещё раз")
        bot.register_next_step_handler(msg, get_name)


def get_phone_number(message):
    if message.content_type == "text" and (
            re.fullmatch(r'[0-9]{11}', message.text) or re.fullmatch(r'\+[0-9]{11}', message.text)):
        bot.forward_message(conf.resender, message.chat.id, message.id)  # ОТПРАВКА НОМЕРА ТЕЛЕФОНА В ДРУГОЙ ЧАТ
        msg = bot.send_message(message.chat.id, "Какую печать Вы выбрали? \n\nНеобходимо написать только название "
                                                "печати, например, И-40 К-6 В-12 О-40")
        bot.register_next_step_handler(msg, get_print_type)
    else:
        msg = bot.send_message(message.chat.id, "Вы неправильно ввели номер телефона, повторите ещё раз")
        bot.register_next_step_handler(msg, get_phone_number)


def get_print_type(message):
    if message.content_type == "text" and re.fullmatch(r'([А-Я][А-Я]-\d\d)|([А-Я]-\d\d)|([А-Я]-\d)|([А-Я][А-Я]-\d)',
                                                       message.text):
        bot.forward_message(conf.resender, message.chat.id, message.id)  # ОТПРАВКА ПЕЧАТИ В ДРУГОЙ ЧАТ
        msg = bot.send_message(message.chat.id, "Прикрепите нужные документы.")
        bot.register_next_step_handler(msg, get_photo)
    else:
        msg = bot.send_message(message.chat.id, "Вы неправильно ввели тип печати, повторите ещё раз")
        bot.register_next_step_handler(msg, get_print_type)


def get_photo(message):
    if message.content_type == "photo":
        bot.forward_message(conf.resender, message.chat.id, message.id)  # ОТПРАВКА ФОТО В ДРУГОЙ ЧАТ
        msg = bot.send_message(message.chat.id, "Введите адрес получения изделия \n\nНеобходимо указать только улицу, "
                                                "например, Адмиралтейская, Чернышевского, Кирова")
        bot.register_next_step_handler(msg, get_address)
    else:
        msg = bot.send_message(message.chat.id, "Вы неправильно прикрепили фотографии, повторите ещё раз")
        bot.register_next_step_handler(msg, get_photo)


def get_address(message):
    if message.content_type == "text" and re.fullmatch(r"Адмиралтейская|Кирова|Чернышевского", message.text):
        bot.forward_message(conf.resender, message.chat.id, message.id)  # ОТПРАВКА АДРЕСА В ДРУГОЙ ЧАТ
        msg = bot.send_message(message.chat.id, "Вы можете написать свои дополнения к заказу. Если нечего дополнить, "
                                                "напишите -")
        bot.register_next_step_handler(msg, get_addition)
    else:
        msg = bot.send_message(message.chat.id, "Вы неправильно ввели адрес, повторите ещё раз")
        bot.register_next_step_handler(msg, get_address)


def get_addition(message):
    if message.content_type == "text":
        bot.forward_message(conf.resender, message.chat.id, message.id)  # ОТПРАВКА ДОПОЛНЕНИЙ В ДРУГОЙ ЧАТ
        bot.send_message(message.chat.id, "Спасибо за заказ! В ближайшее время наш сотрудник с вами свяжется, "
                                          "чтобы уточнить детали.")


bot.infinity_polling()
