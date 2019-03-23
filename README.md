# DozoR telegram bot

**ВНИМАНИЕ:** Бот умеет работать только со старой версией движка DozoR

[![Travis](https://img.shields.io/travis/m-messiah/dzzzzr-bot.svg?style=flat-square)](https://travis-ci.org/m-messiah/dzzzzr-bot)[![Maintainability](https://api.codeclimate.com/v1/badges/37cd4d9a1b6cb56ca1ba/maintainability)](https://codeclimate.com/github/m-messiah/dzzzzr-bot/maintainability)[![Test Coverage](https://api.codeclimate.com/v1/badges/37cd4d9a1b6cb56ca1ba/test_coverage)](https://codeclimate.com/github/m-messiah/dzzzzr-bot/test_coverage)
[@DzzzzR_bot](https://telegram.me/DzzzzR_bot)

Telegram бот, который умеет авторизовываться в движке classic.dzzzr.ru и отправлять коды из чата (и некоторое другое)

Подробности  в группе [vk.com/DzzzR_bot](https://vk.com/dzzzzr_bot)

## Инструкция

1. Для начала работы с ботом, необходимо добавить его в чат ([@DzzzzR_bot](https://telegram.me/DzzzzR_bot)), после чего можно установить настройки Dozor-движка:

`/set_dzzzr url captain pin login password [prefix]` - установить урл (например, https://classic.dzzzr.ru/spb/go/ ) и учетные данные для движка DozoR (капитанская учетка и пин на игру + логин/пароль члена команды, от которого будут отправляться коды).

Если все коды имеют префикс игры (например 27d),то его можно указать здесь и отправлять коды уже в сокращенном виде (12r3 = 27d12r3)

2. Коды могут присутствовать в любом сообщении в чате как с русскими буквами, так и английскими, игнорируя регистр символов. (Главное, чтобы сообщение начиналось с кода)

3. Если на уровне есть ложные коды или необходим контроль над тем, что отправляется в движок, бота можно приостановить с помощью команды `/pause`
`/resume` восстанавливает работу.

4. По окончании игры или при необходимости залогиниться под другими данными, но в той же команде - можно сбросить сессию с ботом, с помощью команд `/stop` + `/start`

5.  Также бот имеет несколько вспомогательных функций:
    1. `/time` - время на уровне. Заведомо не вычитаю из 1.5 часов, зная о возможности смены тайминга в движке.
    2. `/codes` - коды на уровне. (пока без пометок о снятии)
    3. Кодирование/раскодирование base64 текста: `/base64 <текст>`
    4. Преобразование чисел в буквы по порядковому номеру в алфавитах (рус/англ): `/pos <num1 num2 numN>`
    5. Telegram-карта по координатам: `/gps <lat, long>` - координаты могут быть в любом из трех форматов, без использования букв и кавычек, только цифры и точки (если дробные). Внимание на запятую между широтой и долготой. Также, бот пришлет карту, если увидит координаты в сообщении.

По всем вопросам можно писать автору [ВК](https://vk.com/m_messiah) или в [Telegram](https://telegram.me/m_messiah)


Donate:
+ http://yasobe.ru/na/m_messiah
+ https://www.paypal.me/muzafarov
