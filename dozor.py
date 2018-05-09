# coding=utf-8
from random import choice
from re import compile as re_compile
from re import split as re_split
from zlib import MAX_WBITS, decompress

from bs4 import BeautifulSoup
from requests import Session

import main
from useragents import USERAGENTS

__author__ = 'm_messiah'

LITE_MESSAGE = re_compile(ur'<!--errorText--><p><strong>(.*?)</strong></p><!--errorTextEnd-->')
LITE_TIME_ON = re_compile(ur'<!--timeOnLevelBegin (\d*?) timeOnLevelEnd-->')
LITE_TIME_TO = re_compile(ur'<!--timeToFinishBegin (\d*?) timeToFinishEnd-->')


def decode_page(page):
    page_content = page.raw.read()
    try:
        content = decompress(page_content, 16 + MAX_WBITS)
    except Exception:
        content = page_content
    return BeautifulSoup(content, 'html.parser', from_encoding="windows-1251")


class DozoR(object):
    def __init__(self, chat_id):
        self.chat_id = chat_id
        self.url = ""
        self.prefix = ""
        self.credentials = ""
        self.enabled = False
        self.classic = True
        self.browser = Session()
        self.dr_code = re_compile(ur"^[0-9dDдДrRlLzZрРлЛ]+$")

    def help(self):
        return (
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
            u"(Главное, чтобы сообщение начиналось с кода)"
        )

    def pause(self, _):
        self.enabled = False
        return (u"Ок, я больше не буду реагировать на сообщения мне (не считая команды).\n"
                u"Не забудьте потом включить с помощью /resume")

    def resume(self, _):
        self.enabled = True
        return u"Я вернулся! Давайте ваши коды!"

    def get_dzzzr(self, code=None):
        try:
            if code:
                answer = self.browser.post(
                    self.url,
                    data={
                        'action': "entcod",
                        'cod': code.encode("cp1251")
                    },
                    stream=True
                )
            else:
                answer = self.browser.get(self.url, stream=True)
            if not answer:
                raise Exception()
            return decode_page(answer)
        except Exception:
            raise Exception(u"Нет ответа. Проверьте вручную.")

    def _handle_set_dzzzr_arguments(self, arguments):
        arguments = arguments.split()
        if len(arguments) < 5:
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
        self.url = arguments[0]
        return arguments[1:5]

    def _get_dup_session(self, captain, login):
        merged = "|".join((self.url, captain, login))
        if merged in main.CREDENTIALS and self.chat_id != main.CREDENTIALS[merged]:
            return (u"Бот уже используется этой командой. В чате %s\n"
                    u"Сначала остановите его. (/stop)\n" % main.SESSIONS[main.CREDENTIALS[merged]].title)

    def _send_dzzzr_auth(self, captain, pin, login, password):
        self.browser.headers.update({
            'referer': self.url,
            'User-Agent': "Mozilla/5.0 " + choice(USERAGENTS)
        })
        self.browser.auth = (captain, pin)
        try:
            login_page = self.browser.post(
                self.url,
                data={
                    'login': login,
                    'password': password,
                    'action': "auth",
                    'notags': ''
                },
                stream=True
            )
        except Exception as e:
            return False, "Incorrect format (%s)" % e

        if login_page.status_code != 200:
            return False, u"Авторизация не удалась"

        return True, login_page

    def _dzzzr_auth(self, captain, pin, login, password):
        is_authenticated, login_page = self._send_dzzzr_auth(captain, pin, login, password)
        if not is_authenticated:
            return False, login_page
        try:
            answer = decode_page(login_page)
            message = answer.find(class_="sysmsg")
            if not (message and message.get_text()):
                return False, u"Авторизация не удалась"
            message = message.get_text()
            return u"Авторизация пройдена успешно" in message, message
        except Exception as e:
            return False, "Incorrect page (%s)" % e

    def set_dzzzr(self, arguments):
        try:
            captain, pin, login, password = self._handle_set_dzzzr_arguments(arguments)
        except Exception:
            return (
                u"Использование:\n"
                u"/set_dzzzr url captain pin login password [prefix] [regexp]"
            )

        dup_message = self._get_dup_session(captain, login)
        if dup_message:
            return dup_message

        is_authenticated, message = self._dzzzr_auth(captain, pin, login, password)
        if not is_authenticated:
            return message

        self.enabled = True
        self.classic = True
        self.credentials = "|".join((self.url, captain, login))
        main.CREDENTIALS[self.credentials] = self.chat_id
        return u"Добро пожаловать, %s" % login

    def set_lite(self, arguments):
        try:
            arguments = arguments.split()
            if len(arguments) > 1:
                self.url, pin = arguments[:2]
            else:
                raise ValueError
        except ValueError:
            return u"Использование:\n/set_lite url pin"
        else:
            self.browser.headers.update({
                'referer': self.url,
                'User-Agent': "Mozilla/5.0 " + choice(USERAGENTS)
            })
            login_page = self.browser.get(self.url, params={'pin': pin}, stream=True)
            if login_page.status_code != 200:
                return u"Авторизация не удалась"
            else:
                answer = decode_page(login_page)
                message = LITE_MESSAGE.search(str(answer))
                if message:
                    message = message.group(1)
                else:
                    message = u"Авторизация не удалась"
                    return message
                self.enabled = True
                self.classic = False
                self.credentials = "|".join((self.url, pin))
                main.CREDENTIALS[self.credentials] = self.chat_id
                return message

    def time(self, _):
        answer, message = self._get_dzzzr_answer()
        if message:
            return message

        if self.classic:
            message = answer.find("p", string=re_compile(u"Время на уровне:"))
            if message and message.get_text():
                return u" ".join(message.get_text().split()[:4])
        else:
            def to_minutes(sec):
                return u"%s:%s" % (sec / 60, sec % 60)

            on_level = LITE_TIME_ON.search(str(answer))
            to_finish = LITE_TIME_TO.search(str(answer))
            if on_level and to_finish:
                return u"Время на уровне: %s, Осталось: %s" % (
                    to_minutes(int(on_level.group(1))),
                    to_minutes(int(to_finish.group(1))),
                )

        return u"Нет ответа"

    def _get_dzzzr_answer(self):
        try:
            if self.url == "":
                raise Exception(u"Сначала надо войти в движок")
            return self.get_dzzzr(), None
        except Exception as e:
            return None, unicode(e.message)

    def _parse_sector(self, sector):
        if not sector:
            return
        try:
            sector_name, _, codes = sector.partition(u":")
            _, __, codes = codes.partition(u":")
            if not codes:
                return
            codes = codes.strip().split(u", ")
            codes = [c for c in enumerate(codes, start=1) if u"span" not in c[1]]
            return (
                u"%s (осталось %s): %s" % (
                    sector_name,
                    len(codes),
                    u", ".join(u"%s (%s)" % t for t in codes)
                ))
        except Exception:
            pass

    def codes(self, _):
        answer, message = self._get_dzzzr_answer()
        if message:
            return message
        try:
            message = answer.find("strong", string=re_compile(u"Коды сложности")).parent
        except Exception:
            return u"Коды сложности не найдены"
        if not message:
            return u"Нет ответа"

        message = unicode(message).split(u"Коды сложности")[1]
        sectors = re_split("<br/?>", message)[:-1]
        result = filter(None, map(self._parse_sector, sectors))
        return u"\n".join(result)

    def _classic_result(self, code, answer):
        message = answer.find(class_="sysmsg")
        if message and message.get_text():
            message_answer = message.get_text()
        else:
            message_answer = u"нет ответа"
        return code + " - " + message_answer

    def _lite_result(self, code, answer):
        message = LITE_MESSAGE.search(str(answer))
        if message:
            message_answer = message.group(1).decode("utf8")
        else:
            message_answer = u"нет ответа"
        return code + u" - " + message_answer

    def _send_code(self, code):
        if self.url == "":
            return code + u" - сначала надо войти в движок"
        try:
            answer = self.get_dzzzr(code=code)
        except Exception as e:
            return e.message
        try:
            if self.classic:
                return self._classic_result(code, answer)
            else:
                return self._lite_result(code, answer)
        except Exception:
            return u"нет ответа"

    def _handle_code(self, code):
        if not self.dr_code.match(code):
            return
        code = code.upper()
        if self.dr_code.search(u"D"):
            code = code.translate({ord(u'Д'): u'D',
                                   ord(u'Р'): u'R',
                                   ord(u'Л'): u'L'})
        if self.prefix and self.prefix not in code:
            code = self.prefix + code
        return self._send_code(code)

    def handle_text(self, text):
        if not self.enabled:
            return

        codes = text.split()
        if len(codes) < 1:
            return None

        result = filter(None, map(self._handle_code, codes))
        if result:
            return u"\n".join(result)
