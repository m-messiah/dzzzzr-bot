# coding=utf-8

DEFAULT_ANSWER = "I am DR bot (https://telegram.me/DzzzzR_bot)"
INLINE_TEXT = "Inline mode not implemented"
INLINE_DESCRIPTION = u"Inline-режим не реализован"

BOT_NAME = "@DzzzzR_bot"
BOT_VERSION = u"Версия: 3.2.5"
BOT_SESSIONS_TEMPL = u"Сейчас используют:\n%s"
BOT_COMMAND_NOT_FOUND = u"Команда не найдена. Используйте /help \nИли сделайте такую команду (мой код на github)"
BOT_START = u"Внимательно слушаю!"
BOT_STOP = u"До новых встреч!"
BOT_ABOUT = u"""Привет!
Мой код: https://github.com/m-messiah/dzzzzr-bot
Если хочется внести правки - мы открыты для пулл-реквестов.
"""
BOT_HELLO = u"Привет!"

DOZOR_HELP = u"""Бот умеет работать только со старой версией движка DozoR.
Если вы пользуетесь новой - авторизоваться не выйдет.

/set_dzzzr url captain pin login password - установить урл и учетные данные для движка DozoR.
Если все коды имеют префикс игры (например 27d), то его можно указать здесь:
/set_dzzzr url captain pin login password prefix
и отправлять коды уже в сокращенном виде (12r3 = 27d12r3)
Если коды не стандартные, то можно указать regexp для того, как выглядит код
(например, для 1d2r regexp будет [0-9dDrR]+ (если не знакомы с regexp лучше не использовать))
/set_dzzzr url captain pin login password [0-9dDrR]+
Префикс и regexp - необязательные параметры. (если нужны оба - сначала префикс, потом regexp)

/pause - приостанавливает отправку кодов
/resume - возобновляет отправку кодов

Сами коды могут пристуствовать в любом сообщении в чате
как с русскими буквами, так и английскими, игнорируя регистр символов.
(Главное, чтобы сообщение начиналось с кода)
"""

BOT_HELP = u"""Я могу принимать следующие команды:
/help - эта справка
/about - информация об авторе
/start - команда заглушка, эмулирующая начало общения
/stop - команда удаляющая сессию общения с ботом

/base64 <text> - Base64 кодирование/раскодирование
/gps <lat, long> - Карта по координатам
/pos <num1 num2 numN> - Слово из порядковых букв в алфавите

DozoR

""" + DOZOR_HELP

DOZOR_PAUSE = u"""Ок, я больше не буду реагировать на сообщения мне (не считая команды).
Не забудьте потом включить с помощью /resume"""
DOZOR_RESUME = u"Я вернулся! Давайте ваши коды!"

DOZOR_AUTH_FAILED = u"Авторизация не удалась"
DOZOR_AUTH_PATTERN = u"Авторизация пройдена успешно"
DOZOR_BAD_PAGE_TEMPL = u"Incorrect page (%s)"
DOZOR_CODE_RANK_TEMPL = u"%s (%s)"
DOZOR_DUPLICATE_TEMPL = u"Бот уже используется этой командой. В чате %s\nСначала остановите его. (/stop)\n"
DOZOR_INCORRECT_TEMPL = u"Incorrect format (%s)"
DOZOR_NEED_AUTH = u"Сначала надо войти в движок"
DOZOR_NO_ANSWER = u"Нет ответа. Проверьте вручную."
DOZOR_NO_CODE_RANKS = u"Коды сложности не найдены"
DOZOR_SECTOR_CODES_TEMPL = u"%s (осталось %s): %s"
DOZOR_SET_DZZZR_HELP = u"Использование:\n/set_dzzzr url captain pin login password [prefix] [regexp]"
DOZOR_SET_LITE_HELP = u"Использование:\n/set_lite url pin"
DOZOR_TIME_ON_TEMPL = u"Время на уровне: %s, Осталось: %s"
DOZOR_WELCOME_TEMPL = u"Добро пожаловать, %s"

BOT_GREETING_TEMPL = u"Привет, %s! "
BOT_GREETING_PHRASES = (
    u"Во время игры мы тут не флудим.",
    u"Я буду отправлять найденные коды сразу в движок.",
    u"Буду краток - тебя ждали.",
    u"А мы тебя уже давно ждём.",
    u"А меня зовут Бот. Приятно познакомиться.",
    u"Как оно?",
    u"Как дела?",
    u"Как жизнь?",
    u"Как ты сюда попал(а)?",
)

BOT_LEFT_PARTICIPANT = u"А я буду скучать..."
