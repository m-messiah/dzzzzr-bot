# coding=utf-8
from base64 import b64decode, b64encode
from random import choice
from re import compile as re_compile, split as re_split
from urllib import urlencode
from zlib import decompress, MAX_WBITS
import logging

import webapp2
from bs4 import BeautifulSoup
from requests import Session
from google.appengine.api import urlfetch
from webapp2_extras import json

__author__ = 'm_messiah'

SESSIONS = {}
CREDENTIALS = {}

USERAGENTS = (
    '(Windows NT 6.2; WOW64) AppleWebKit/537.22 (KHTML, like Gecko) '
    'Chrome/25.0.1364.172 YaBrowser/1.7.1364.22194 Safari/537.22',
    '(X11; U; Linux x86_64; en-US; rv:1.9.1.3) Gecko/20090913 Firefox/3.5.3',
    '(X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) '
    'Ubuntu Chromium/28.0.1500.71 Chrome/28.0.1500.71 Safari/537.36',
    '(Windows; U; Windows NT 6.1; en; rv:1.9.1.3) Gecko/20090824 '
    'Firefox/3.5.3 (.NET CLR 3.5.30729)',
    '(Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) '
    'Chrome/30.0.1599.69 Safari/537.36',
    '(Windows NT 6.1; WOW64; rv:24.0) Gecko/20100101 Firefox/24.0',
    '(Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) '
    'Chrome/29.0.1547.76 Safari/537.36',
    '(Macintosh; Intel Mac OS X 10_8_5) AppleWebKit/536.30.1 '
    '(KHTML, like Gecko) Version/6.0.5 Safari/536.30.1',
    '(iPhone; CPU iPhone OS 7_0_2 like Mac OS X) AppleWebKit/537.51.1 '
    '(KHTML, like Gecko) Version/7.0 Mobile/11A501 Safari/9537.53',
    '(iPad; CPU OS 7_0 like Mac OS X) AppleWebKit/537.51.1 '
    '(KHTML, like Gecko) Version/7.0 Mobile/11A465 Safari/9537.53',
    '(iPhone; CPU iPhone OS 6_1_3 like Mac OS X) AppleWebKit/536.26 '
    '(KHTML, like Gecko) Version/6.0 Mobile/10B329 Safari/8536.25',
    '(Windows NT 6.2; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) '
    'Chrome/30.0.1599.66 Safari/537.36',
    '(Linux; Android 4.1.2; GT-I9100 Build/JZO54K) AppleWebKit/537.36 '
    '(KHTML, like Gecko) Chrome/30.0.1599.82 Mobile Safari/537.36',
    '(Windows; U; Windows NT 5.2; en-US; rv:1.9.1.3) Gecko/20090824 '
    'Firefox/3.5.3 (.NET CLR 3.5.30729)',
    '(Windows; U; Windows NT 6.1; en-US; rv:1.9.1.1) Gecko/20090718 '
    'Firefox/3.5.1',
    '(Windows; U; Windows NT 5.1; en-US) AppleWebKit/532.1 '
    '(KHTML, like Gecko) Chrome/4.0.219.6 Safari/532.1',
    '(compatible; MSIE 8.0; Windows NT 6.1; WOW64; '
    'Trident/4.0; SLCC2; .NET CLR 2.0.50727; InfoPath.2)',
    '(compatible; MSIE 8.0; Windows NT 6.0; Trident/4.0; SLCC1; '
    '.NET CLR 2.0.50727; .NET CLR 1.1.4322; .NET CLR 3.5.30729; '
    '.NET CLR 3.0.30729)',
    '(compatible; MSIE 8.0; Windows NT 5.2; Win64; x64; Trident/4.0)',
    '(compatible; MSIE 9.0; Windows NT 6.1; Trident/5.0)',
    '(compatible; MSIE 10.0; Windows NT 6.2; WOW64; Trident/6.0)',
    '(compatible; MSIE 8.0; Windows NT 5.1; Trident/4.0; SV1; '
    '.NET CLR 2.0.50727; InfoPath.2)',
    '(Windows; U; MSIE 7.0; Windows NT 6.0; en-US)',
    '(compatible; MSIE 7.0; Windows NT 5.1)',
    '(compatible; MSIE 6.1; Windows XP)',
    '(Windows NT 5.2; U; ru) Presto/2.5.22 Version/10.51',
    '(Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) '
    'Chrome/30.0.1599.69 Safari/537.36',
    '(Windows NT 6.1; WOW64; rv:24.0) Gecko/20100101 Firefox/24.0',
    '(Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) '
    'Chrome/29.0.1547.76 Safari/537.36',
    '(Macintosh; Intel Mac OS X 10_8_5) AppleWebKit/536.30.1 '
    '(KHTML, like Gecko) Version/6.0.5 Safari/536.30.1',
    '(Macintosh; Intel Mac OS X 10_8_5) AppleWebKit/537.36 '
    '(KHTML, like Gecko) Chrome/30.0.1599.69 Safari/537.36',
    '(Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) '
    'Chrome/30.0.1599.101 Safari/537.36',
    '(Macintosh; Intel Mac OS X 10.8; rv:24.0) Gecko/20100101 Firefox/24.0',
    '(Macintosh; Intel Mac OS X 10_8_5) AppleWebKit/537.36 '
    '(KHTML, like Gecko) Chrome/30.0.1599.101 Safari/537.36',
    '(Macintosh; Intel Mac OS X 10_8_5) AppleWebKit/537.36 '
    '(KHTML, like Gecko) Chrome/29.0.1547.76 Safari/537.36',
    '(Windows NT 6.2; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) '
    'Chrome/30.0.1599.69 Safari/537.36',
    '(compatible; MSIE 10.0; Windows NT 6.1; WOW64; Trident/6.0)',
    '(Windows NT 6.1; rv:24.0) Gecko/20100101 Firefox/24.0',
    '(Windows NT 6.2; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) '
    'Chrome/29.0.1547.76 Safari/537.36',
    '(Windows NT 5.1; rv:24.0) Gecko/20100101 Firefox/24.0',
    '(iPhone; CPU iPhone OS 7_0_2 like Mac OS X) AppleWebKit/537.51.1 '
    '(KHTML, like Gecko) Version/7.0 Mobile/11A501 Safari/9537.53',
    '(Windows NT 6.1) AppleWebKit/537.36 (KHTML, like Gecko) '
    'Chrome/30.0.1599.69 Safari/537.36',
    '(X11; Ubuntu; Linux x86_64; rv:24.0) Gecko/20100101 Firefox/24.0',
    '(Windows NT 6.1; WOW64; rv:23.0) Gecko/20100101 Firefox/23.0',
    '(Windows NT 6.1) AppleWebKit/537.36 (KHTML, like Gecko) '
    'Chrome/29.0.1547.76 Safari/537.36',
    '(Windows NT 6.2; WOW64; rv:24.0) Gecko/20100101 Firefox/24.0',
    '(iPad; CPU OS 7_0_2 like Mac OS X) AppleWebKit/537.51.1 '
    '(KHTML, like Gecko) Version/7.0 Mobile/11A501 Safari/9537.53',
    '(Macintosh; Intel Mac OS X 10_7_5) AppleWebKit/536.30.1 '
    '(KHTML, like Gecko) Version/6.0.5 Safari/536.30.1',
    '(Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) '
    'Chrome/30.0.1599.66 Safari/537.36',
    '(compatible; MSIE 9.0; Windows NT 6.1; WOW64; Trident/5.0)',
    '(Windows NT 6.1) AppleWebKit/537.36 (KHTML, like Gecko) '
    'Chrome/30.0.1599.101 Safari/537.36',
    '(X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) '
    'Chrome/30.0.1599.66 Safari/537.36',
    '(X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) '
    'Ubuntu Chromium/28.0.1500.71 Chrome/28.0.1500.71 Safari/537.36',
    '(Windows NT 5.1) AppleWebKit/537.36 (KHTML, like Gecko) '
    'Chrome/30.0.1599.69 Safari/537.36',
    '(Macintosh; Intel Mac OS X 10_8_4) AppleWebKit/537.36 '
    '(KHTML, like Gecko) Chrome/29.0.1547.76 Safari/537.36',
    '(Macintosh; Intel Mac OS X 10_9) AppleWebKit/537.71 '
    '(KHTML, like Gecko) Version/7.0 Safari/537.71',
    '(Windows NT 6.2; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) '
    'Chrome/30.0.1599.101 Safari/537.36',
    '(Macintosh; Intel Mac OS X 10_7_5) AppleWebKit/537.36 '
    '(KHTML, like Gecko) Chrome/30.0.1599.69 Safari/537.36',
    '(Macintosh; Intel Mac OS X 10_8_5) AppleWebKit/537.36 '
    '(KHTML, like Gecko) Chrome/30.0.1599.66 Safari/537.36',
    '(Windows NT 5.1) AppleWebKit/537.36 (KHTML, like Gecko) '
    'Chrome/29.0.1547.76 Safari/537.36',
    '(Macintosh; Intel Mac OS X 10_8_4) AppleWebKit/536.30.1 '
    '(KHTML, like Gecko) Version/6.0.5 Safari/536.30.1',
    '(X11; Linux x86_64; rv:24.0) Gecko/20100101 Firefox/24.0',
    '(X11; Ubuntu; Linux i686; rv:24.0) Gecko/20100101 Firefox/24.0',
    '(Macintosh; Intel Mac OS X 10_8_4) AppleWebKit/537.36 '
    '(KHTML, like Gecko) Chrome/30.0.1599.69 Safari/537.36',
    '(Macintosh; Intel Mac OS X 10_9_0) AppleWebKit/537.36 '
    '(KHTML, like Gecko) Chrome/30.0.1599.101 Safari/537.36',
    '(compatible; MSIE 10.0; Windows NT 6.1; Trident/6.0)',
    '(Macintosh; Intel Mac OS X 10.7; rv:24.0) Gecko/20100101 Firefox/24.0',
    '(Macintosh; Intel Mac OS X 10_7_5) AppleWebKit/537.36 '
    '(KHTML, like Gecko) Chrome/29.0.1547.76 Safari/537.36',
    '(Macintosh; Intel Mac OS X 10_6_8) AppleWebKit/534.59.10 '
    '(KHTML, like Gecko) Version/5.1.9 Safari/534.59.10',
    '(Macintosh; Intel Mac OS X 10_6_8) AppleWebKit/537.36 '
    '(KHTML, like Gecko) Chrome/30.0.1599.69 Safari/537.36',
    '(compatible; MSIE 9.0; Windows NT 6.1; Trident/5.0)',
    '(Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) '
    'Chrome/29.0.1547.66 Safari/537.36',
    '(iPhone; CPU iPhone OS 7_0 like Mac OS X) AppleWebKit/537.51.1 '
    '(KHTML, like Gecko) Version/7.0 Mobile/11A465 Safari/9537.53',
    '(X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) '
    'Chrome/29.0.1547.76 Safari/537.36',
    '(compatible; MSIE 10.0; Windows NT 6.2; WOW64; Trident/6.0)',
    '(Windows NT 5.1) AppleWebKit/537.36 (KHTML, like Gecko) '
    'Chrome/30.0.1599.101 Safari/537.36',
    '(Macintosh; Intel Mac OS X 10.6; rv:24.0) Gecko/20100101 Firefox/24.0',
    '(Macintosh; Intel Mac OS X 10.8; rv:23.0) Gecko/20100101 Firefox/23.0',
    '(Windows NT 5.1; rv:23.0) Gecko/20100101 Firefox/23.0',
    '(iPad; CPU OS 7_0 like Mac OS X) AppleWebKit/537.51.1 '
    '(KHTML, like Gecko) Version/7.0 Mobile/11A465 Safari/9537.53',
    '(Macintosh; Intel Mac OS X 10_6_8) AppleWebKit/537.36 '
    '(KHTML, like Gecko) Chrome/29.0.1547.76 Safari/537.36',
    '(Macintosh; Intel Mac OS X 10_7_5) AppleWebKit/537.36 '
    '(KHTML, like Gecko) Chrome/30.0.1599.101 Safari/537.36',
    '(iPhone; CPU iPhone OS 6_1_3 like Mac OS X) AppleWebKit/536.26 '
    '(KHTML, like Gecko) Version/6.0 Mobile/10B329 Safari/8536.25',
    '(Windows NT 6.1; rv:23.0) Gecko/20100101 Firefox/23.0',
    '(X11; Linux i686) AppleWebKit/537.36 (KHTML, like Gecko) '
    'Ubuntu Chromium/28.0.1500.71 Chrome/28.0.1500.71 Safari/537.36',
    '(Macintosh; Intel Mac OS X 10_8_4) AppleWebKit/537.36 '
    '(KHTML, like Gecko) Chrome/30.0.1599.101 Safari/537.36',
    '(Windows NT 6.3; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) '
    'Chrome/30.0.1599.101 Safari/537.36',
    '(Windows NT 6.1; WOW64) Presto/2.12.388 Version/12.16',
    '(iPad; CPU OS 6_1_3 like Mac OS X) AppleWebKit/536.26 '
    '(KHTML, like Gecko) Version/6.0 Mobile/10B329 Safari/8536.25',
    '(Windows NT 6.2; WOW64; rv:23.0) Gecko/20100101 Firefox/23.0',
    '(Windows NT 6.2; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) '
    'Chrome/30.0.1599.66 Safari/537.36',
    '(Linux; Android 4.1.2; GT-I9100 Build/JZO54K) AppleWebKit/537.36 '
    '(KHTML, like Gecko) Chrome/30.0.1599.82 Mobile Safari/537.36',
    '(Windows NT 6.0; rv:24.0) Gecko/20100101 Firefox/24.0',
    '(Windows NT 6.3; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) '
    'Chrome/30.0.1599.69 Safari/537.36',
    '(Macintosh; Intel Mac OS X 10_7_5) AppleWebKit/537.36 '
    '(KHTML, like Gecko) Chrome/30.0.1599.66 Safari/537.36',
    '(X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) '
    'Chrome/29.0.1547.65 Safari/537.36',
    '(X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) '
    'Chrome/30.0.1599.101 Safari/537.36',
    '(Windows NT 6.0) AppleWebKit/537.36 (KHTML, like Gecko) '
    'Chrome/30.0.1599.69 Safari/537.36',
    '(compatible; MSIE 9.0; Windows NT 6.0; Trident/5.0)',
    '(Macintosh; Intel Mac OS X 10_6_8) AppleWebKit/537.36 '
    '(KHTML, like Gecko) Chrome/30.0.1599.101 Safari/537.36',
    '(Windows NT 6.1; WOW64; rv:25.0) Gecko/20100101 Firefox/25.0',
    '(iPad; CPU OS 5_1_1 like Mac OS X) AppleWebKit/534.46 '
    '(KHTML, like Gecko) Version/5.1 Mobile/9B206 Safari/7534.48.3',
    '(Windows NT 6.1; WOW64; rv:17.0) Gecko/20100101 Firefox/17.0',
    '(X11; Linux i686) AppleWebKit/537.36 (KHTML, like Gecko) '
    'Chrome/29.0.1547.76 Safari/537.36',
    '(Macintosh; Intel Mac OS X 10_8_4) AppleWebKit/537.36 '
    '(KHTML, like Gecko) Chrome/30.0.1599.66 Safari/537.36',
    '(X11; Linux x86_64) AppleWebKit/537.31 (KHTML, like Gecko) '
    'Chrome/26.0.1410.63 Safari/537.31',
    '(Macintosh; Intel Mac OS X 10_8_3) AppleWebKit/537.36 '
    '(KHTML, like Gecko) Chrome/30.0.1599.69 Safari/537.36',
    '(Windows NT 6.1) AppleWebKit/537.36 (KHTML, like Gecko) '
    'Chrome/30.0.1599.66 Safari/537.36',
    '(Windows NT 6.3; WOW64; rv:24.0) Gecko/20100101 Firefox/24.0',
    '(X11; Linux i686) AppleWebKit/537.36 (KHTML, like Gecko) '
    'Chrome/30.0.1599.66 Safari/537.36',
)

RUS = (1072, 1073, 1074, 1075, 1076, 1077, 1105, 1078, 1079, 1080, 1081, 1082,
       1083, 1084, 1085, 1086, 1087, 1088, 1089, 1090, 1091, 1092, 1093, 1094,
       1095, 1096, 1097, 1098, 1099, 1100, 1101, 1102, 1103)

ENG = (97, 98, 99, 100, 101, 102, 103, 104, 105, 106, 107, 108, 109, 110, 111,
       112, 113, 114, 115, 116, 117, 118, 119, 120, 121, 122)


def botan_track(chat_id, event, message):
    try:
        botan_url = "https://api.botan.io/track?"
        botan_url += "token=ydRXN:ZK8C:Iq7BXBi9MUb6Sp0ahCJ6M&"
        botan_url += "uid=%s&" % chat_id
        botan_url += "name=%s" % event
        botan = urlfetch.fetch(botan_url,
                               payload=json.encode(message),
                               method=urlfetch.POST,
                               headers={"Content-Type": "application/json"})
        if botan.status_code == 200:
            response = json.decode(botan.content)
            if response['status'] == 'accepted':
                return True

        return False
    except:
        return False


def decode_page(page):
    try:
        page_content = page.content
    except:
        page_content = page.partial
    try:
        content = decompress(page_content, 16 + MAX_WBITS)
    except:
        content = page_content
    return BeautifulSoup(content.decode("cp1251", "ignore"), 'html.parser')


class DozoR(object):
    def __init__(self, sender):
        self.chat_id = sender['id']
        self.title = sender.get('title', sender.get('username', ''))
        self.url = ""
        self.prefix = ""
        self.credentials = ""
        self.enabled = False
        self.browser = Session()
        self.name = "@DzzzzR_bot"
        self.dr_code = re_compile(ur"^[0-9dDдДrRрР]+$")

    def get_dzzzr(self, code=None):
        if code:
            answer = self.browser.post(
                self.url,
                data={'action': "entcod",
                      'cod': code.encode("cp1251")}
            )
        else:
            answer = self.browser.get(self.url)
        if not answer:
            raise Exception(u"Нет ответа. Проверьте вручную.")
        try:
            return decode_page(answer)
        except:
            raise Exception(u"Нет ответа. Проверьте вручную.")

    def set_dzzzr(self, arguments):
        try:
            arguments = arguments.split()
            if len(arguments) > 4:
                self.url, captain, pin, login, password = arguments[:5]
            else:
                raise ValueError

            if len(arguments) > 5:
                if "[" not in arguments[5]:
                    self.prefix = arguments[5].upper()
                else:
                    self.dr_code = re_compile(ur"^%s$" % arguments[5])
            else:
                self.prefix = ""
            if len(arguments) > 6:
                self.dr_code = re_compile(ur"^%s$" % arguments[6])

        except ValueError:
            return (
                u"Использование:\n"
                u"/set_dzzzr url captain pin login password [prefix] [regexp]")
        else:
            merged = "|".join((self.url, captain, login))
            if (merged in CREDENTIALS and self.chat_id != CREDENTIALS[merged]):
                return (u"Бот уже используется этой командой. В чате %s\n"
                        u"Сначала остановите его. (/stop)\n"
                        % SESSIONS[CREDENTIALS[merged]].title)
            self.browser.headers.update({
                'referer': self.url,
                'User-Agent': "Mozilla/5.0 " + choice(USERAGENTS)
            })
            self.browser.auth = (captain, pin)
            login_page = self.browser.post(
                self.url,
                data={
                    'login': login,
                    'password': password,
                    'action': "auth",
                    'notags': ''
                }
            )
            if login_page.status_code != 200:
                return u"Авторизация не удалась"
            else:
                answer = decode_page(login_page)
                message = answer.find(class_="sysmsg")
                if message and message.get_text():
                    message = message.get_text()
                else:
                    message = u"Авторизация не удалась"
                if u"Авторизация пройдена успешно" not in message:
                    return message
                self.enabled = True
                self.credentials = "|".join((self.url, captain, login))
                CREDENTIALS[self.credentials] = self.chat_id
                return u"Добро пожаловать, %s" % login

    def show_sessions(self, _):
        return u"Сейчас используют:\n" + u"\n".join(CREDENTIALS.keys())

    def show_sess(self, _):
        sessions = ["%s (%s)" % (v.title, k) for k, v in SESSIONS.items()]
        return u"Сейчас используют:\n" + u"\n".join(sessions)

    def send_message(self, arguments):
        try:
            chat_id, _, text = arguments.partition(" ")
            payload = urlencode({'chat_id': chat_id,
                                 'text': text.encode("utf8")})
            urlfetch.fetch(
                "https://api.telegram.org/"
                "bot117677541:AAEKw2NOQabXRGwr-Edvqx1RJ6Z73Xjxn8k/sendMessage",
                payload=payload,
                method=urlfetch.POST).content
            return u"Сообщение отправлено"
        except:
            return u"Не удалось отправить сообщение"

    def broadcast_message(self, text):
        fl = True

        for chat_id in SESSIONS:
            if chat_id == self.chat_id:
                continue
            payload = urlencode({'chat_id': chat_id,
                                 'text': text.encode("utf8")})
            urlfetch.fetch(
                "https://api.telegram.org/"
                "bot117677541:AAEKw2NOQabXRGwr-Edvqx1RJ6Z73Xjxn8k/sendMessage",
                payload=payload,
                method=urlfetch.POST).content

        return (u"Сообщение разослано %s получателям" % (len(SESSIONS) - 1)
                if fl else u"Сообщение доставлено не всем")

    def not_found(self, _):
        return (u"Команда не найдена. Используйте /help \n"
                u"Или дайте денег автору, и он сделает такую команду")

    def version(self, _):
        return u"Версия: 3.2.2"

    def help(self, _):
        return (
            u"Я могу принимать следующие команды:\n"
            u"/help - эта справка\n"
            u"/about - информация об авторе\n"
            u"/base64 <text> - Base64 кодирование/раскодирование\n"
            u"/pos <num1 num2 numN> - Слово из порядковых букв в алфавите\n"
            u"/gps <lat, long> - Карта по координатам\n"
            u"/start - команда заглушка, эмулирующая начало общения\n"
            u"/stop - команда удаляющая сессию общения с ботом\n"
            u"\nDozoR\n"
            u"/set_dzzzr url captain pin login password - "
            u"  установить урл и учетные данные для движка DozoR.\n"
            u"Если все коды имеют префикс игры (например 27d),"
            u"то его можно указать здесь \n"
            u"/set_dzzzr url captain pin login password prefix \n"
            u"и отправлять коды уже в сокращенном виде (12r3 = 27d12r3)\n"
            u"Если коды не стандартные, то можно указать regexp для того, "
            u"как выглядит код (например, для 1d2r regexp будет [0-9dDrR]+ )\n"
            u"/set_dzzzr url captain pin login password [0-9dDrR]+ \n"
            u"Префикс и regexp - необязательные параметры. "
            u"(если нужны оба - сначала префикс, потом regexp)\n"
            u"\n/pause - приостанавливает отправку кодов\n"
            u"/resume - возобновляет отправку кодов\n"
            u"\nСами коды могут пристуствовать в любом сообщении в чате "
            u"как с русскими буквами, так и английскими, "
            u"игнорируя регистр символов. "
            u"(Главное, чтобы сообщение начиналось с кода)")

    def start(self, _):
        return u"Внимательно слушаю!"

    def pause(self, _):
        self.enabled = False
        return (u"Ок, я больше не буду реагировать на сообщения мне "
                u"(не считая команды). "
                u"Не забудьте потом включить с помощью /resume")

    def resume(self, _):
        self.enabled = True
        return u"Я вернулся! Давайте ваши коды!"

    def stop(self, _):
        try:
            self.enabled = False
            del CREDENTIALS[self.credentials]
            del SESSIONS[self.chat_id]
        except:
            pass
        return u"До новых встреч!"

    def about(self, _):
        return (u"Привет!\n"
                u"Мой автор @m_messiah\n"
                u"Сайт: https://m-messiah.com\n"
                u"\nА еще принимаются пожертвования:\n"
                u"https://paypal.me/muzafarov\n"
                u"http://yasobe.ru/na/m_messiah")

    def base64(self, arguments):
        response = None
        try:
            response = b64decode(arguments.encode("utf8"))
            assert len(response)
            response.decode("utf8").encode("utf8")
        except:
            response = b64encode(arguments.encode("utf8"))
        finally:
            return response

    def pos(self, text):
        try:
            positions = list(map(int, text.split()))
        except ValueError:
            try:
                positions = list(map(int, text.split(",")))
            except:
                return None

        return u"\n".join((
            u"".join(map(lambda i: unichr(RUS[(i - 1) % 33]), positions)),
            u"".join(map(lambda i: unichr(ENG[(i - 1) % 26]), positions))
        ))

    def gps(self, text):
        try:
            raw_coords = text.split(",")
            coords = [0, [[], []]]
            for i, lat in enumerate(raw_coords):
                lat = lat.split()
                count = len(lat)
                if count > coords[0]:
                    coords[0] = count
                coords[1][i] = lat
            if coords[0] == 1:
                return tuple(map(lambda x: round(float(x[0]), 6), coords[1]))
            if coords[0] == 2:
                result = []
                for lat in coords[1]:
                    d, m = map(float, lat[:2])
                    result.append(round(d + m / 60 * (-1 if d < 0 else 1), 6))
                return tuple(result)
            if coords[0] == 3:
                result = []
                for lat in coords[1]:
                    d, m, s = map(float, lat[:3])
                    result.append(round(
                        d + (m * 60 + s) / 3600 * (-1 if d < 0 else 1),
                        6
                    ))
                return tuple(result)
            return None
        except:
            pass

    def time(self, _):
        if self.url == "":
            return u"Сначала надо войти в движок"
        try:
            answer = self.get_dzzzr()
        except Exception as e:
            return e.message

        message = answer.find(
            "p", text=re_compile(ur"Время на уровне: (\d\d:\d\d:\d\d)")
        )
        if message and message.get_text():
            return u" ".join(message.get_text().split()[:4])
        return u"Нет ответа"

    def codes(self, _):
        if self.url == "":
            return u"Сначала надо войти в движок"
        try:
            answer = self.get_dzzzr()
        except Exception as e:
            return e.message
        message = None
        try:
            message = answer.find(
                "strong", text=re_compile(u"Коды сложности")
            ).nextSibling
        except:
            return u"Коды сложности не найдены"

        if message and message.contents:
            sectors = re_split("<br/?>", message.encode_contents())[:-1]
            result = []
            for sector in filter(len, sectors):
                sector_name, _, codes = sector.partition(":")
                _, __, codes = codes.partition(":")
                codes = filter(lambda c: "span" not in c[1],
                               enumerate(codes.strip().split(", "), start=1))
                result.append(
                    u"%s (осталось %s): %s" % (
                        sector_name.decode("utf8"),
                        len(codes),
                        u", ".join(map(lambda t: u"%s (%s)" % (t[0], t[1]),
                                       codes))
                    ))
            return u"\n".join(result)
        return u"Нет ответа"

    def handle(self, message):
        if message['text'][0] == '/':
            command, _, arguments = message['text'].partition(" ")
            if self.name in command:
                command = command[:command.find("@DzzzzR_bot")]
            if "@" in command:
                return None
            botan_track(self.chat_id, command, message)
            if command == "/set_dzzzr":
                try:
                    return self.set_dzzzr(arguments)
                except Exception as e:
                    return "Incorrect format (%s)" % e
            else:
                try:
                    return getattr(self, command[1:],
                                   self.not_found)(arguments)
                except UnicodeEncodeError as e:
                    return self.not_found(None)
                except Exception as e:
                    logging.error(e)
                    return None
        else:
            try:
                response = self.code(message)
                if response:
                    return response
            except:
                pass

    def code(self, message):
        def send(browser, url, code):
            if url == "":
                return code + u" - сначала надо войти в движок"
            try:
                answer = self.get_dzzzr(code=code)
            except Exception as e:
                return e.message
            message = answer.find(class_="sysmsg")
            return code + " - " + (message.get_text()
                                   if message and message.get_text()
                                   else u"нет ответа.")
        if self.enabled:
            if message['text'].count(",") == 1:
                try:
                    result = self.gps(message['text'])
                    if result:
                        botan_track(self.chat_id, "gps", message)
                        return result
                except:
                    pass

            codes = message['text'].split()
            result = []
            if len(codes) < 1:
                return None
            if self.dr_code.match(codes[0]):
                for code in codes:
                    if self.dr_code.match(code):
                        code = code.upper()
                        if self.dr_code.search(u"DR"):
                            code = code.translate({ord(u'Д'): u'D',
                                                   ord(u'Р'): u'R'})
                        if self.prefix and self.prefix not in code:
                            code = self.prefix + code
                    result.append(send(self.browser, self.url, code))
            if len(result):
                return u"\n".join(result)

        if u"привет" in message['text'].lower():
            if u"бот" in message['text'].lower():
                botan_track(self.chat_id, "hello", message)
                return u"Привет!"
        return None


def hello_message(user):
    response = u"Привет, %s! " % user.get('first_name')
    response += choice([
        u"Во время игры мы тут не флудим.",
        u"Я буду отправлять найденные коды сразу в движок.",
        u"Буду краток - тебя ждали.",
        u"А мы тебя уже давно ждём.",
        u"А меня зовут бот. Приятно познакомиться.",
        u"Как %s?" % choice([u"оно", u"дела", u"жизнь", u"ты сюда попал(а)"]),
    ])
    return response


class MainPage(webapp2.RequestHandler):
    def show_error(self):
        self.response.headers['Content-Type'] = 'application/json'
        self.response.write(json.encode({
            'result': "Info",
            "name": "I am DR bot (https://telegram.me/DzzzzR_bot)"
        }))

    def get(self):
        return self.show_error()

    def post(self):
        if 'Content-Type' not in self.request.headers:
            return self.show_error()
        if 'application/json' not in self.request.headers['Content-Type']:
            return self.show_error()
        try:
            update = json.decode(self.request.body)
        except Exception:
            return self.show_error()
        response = None
        if 'message' not in update:
            if 'inline_query' in update:
                self.response.headers['Content-Type'] = 'application/json'
                self.response.write(json.encode({
                    'method': 'answerInlineQuery',
                    'inline_query_id': update['inline_query']['id'],
                    'cache_time': 60,
                    'results': json.encode([{
                        'type': 'article',
                        'id': "1",
                        'title': "405",
                        'message_text': "Inline mode not implemented",
                        'description': "Inline-режим не реализован"
                    }])
                }))
            return self.show_error()

        message = update['message']
        sender = message['chat']
        if "text" in message:
            logging.debug(message['text'])
            if sender['id'] not in SESSIONS:
                SESSIONS[sender['id']] = DozoR(sender)

            output = SESSIONS[sender['id']].handle(message)
            if isinstance(output, tuple):
                response = {'method': "sendLocation",
                            'chat_id': sender['id'],
                            'reply_to_message_id': message['message_id'],
                            'latitude': output[0],
                            'longitude': output[1]}
            elif output:
                response = {'method': "sendMessage",
                            'chat_id': sender['id'],
                            'text': output,
                            'reply_to_message_id': message['message_id'],
                            'disable_web_page_preview': True}

        elif "contact" in message:
            response = {'method': "sendMessage",
                        'chat_id': sender['id'],
                        'text': "id = %s"
                                % message['contact'].get('user_id', "none"),
                        'reply_to_message_id': message['message_id'],
                        'disable_web_page_preview': True}
        elif "new_chat_participant" in message:
            response = {'method': "sendMessage",
                        'chat_id': sender['id'],
                        'text': hello_message(message['new_chat_participant']),
                        'disable_web_page_preview': True}
        elif "left_chat_participant" in message:
            response = {'method': "sendMessage",
                        'chat_id': sender['id'],
                        'text': u"А я буду скучать...",
                        'disable_web_page_preview': True}

        self.response.headers['Content-Type'] = 'application/json'
        self.response.write(json.encode(response if response else {}))


app = webapp2.WSGIApplication([('/', MainPage)])

if __name__ == '__main__':
    app.run()
