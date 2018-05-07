# coding=utf-8
import logging
from base64 import b64decode, b64encode
from random import choice
from re import compile as re_compile
from re import split as re_split
from zlib import MAX_WBITS, decompress

from bs4 import BeautifulSoup
from requests import Session

import main
from useragents import USERAGENTS

__author__ = 'm_messiah'

CREDENTIALS = {}

RUS = (1072, 1073, 1074, 1075, 1076, 1077, 1105, 1078, 1079, 1080, 1081, 1082,
       1083, 1084, 1085, 1086, 1087, 1088, 1089, 1090, 1091, 1092, 1093, 1094,
       1095, 1096, 1097, 1098, 1099, 1100, 1101, 1102, 1103)

ENG = (97, 98, 99, 100, 101, 102, 103, 104, 105, 106, 107, 108, 109, 110, 111,
       112, 113, 114, 115, 116, 117, 118, 119, 120, 121, 122)

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
    def __init__(self, sender):
        self.chat_id = sender['id']
        self.title = sender.get('title', sender.get('username', ''))
        self.url = ""
        self.prefix = ""
        self.credentials = ""
        self.enabled = False
        self.classic = True
        self.browser = Session()
        self.name = "@DzzzzR_bot"
        self.dr_code = re_compile(ur"^[0-9dDдДrRlLzZрРлЛ]+$")

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
            if merged in CREDENTIALS and self.chat_id != CREDENTIALS[merged]:
                return (u"Бот уже используется этой командой. В чате %s\n"
                        u"Сначала остановите его. (/stop)\n" % main.SESSIONS[CREDENTIALS[merged]].title)
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
                },
                stream=True
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
                self.classic = True
                self.credentials = "|".join((self.url, captain, login))
                CREDENTIALS[self.credentials] = self.chat_id
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
                CREDENTIALS[self.credentials] = self.chat_id
                return message

    def show_sessions(self, _):
        sessions = ["%s (%s)" % (v.title, k) for k, v in main.SESSIONS.items()]
        return u"Сейчас используют:\n" + u"\n".join(sessions)

    def not_found(self, _):
        return (u"Команда не найдена. Используйте /help \n"
                u"Или дайте денег автору, и он сделает такую команду")

    def version(self, _):
        return u"Версия: 3.2.3"

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
        return (u"Ок, я больше не буду реагировать на сообщения мне (не считая команды).\n"
                u"Не забудьте потом включить с помощью /resume")

    def resume(self, _):
        self.enabled = True
        return u"Я вернулся! Давайте ваши коды!"

    def stop(self, _):
        try:
            self.enabled = False
            del CREDENTIALS[self.credentials]
            del main.SESSIONS[self.chat_id]
        except Exception:
            pass
        return u"До новых встреч!"

    def about(self, _):
        return (u"Привет!\n"
                u"Мой автор @m_messiah\n"
                u"Мой код: https://github.com/m-messiah/dzzzzr-bot\n"
                u"\nА еще принимаются пожертвования:\n"
                u"https://paypal.me/muzafarov\n"
                u"http://yasobe.ru/na/m_messiah")

    def base64(self, arguments):
        response = None
        try:
            response = b64decode(arguments.encode("utf8"))
            assert len(response)
            response.decode("utf8").encode("utf8")
        except Exception:
            response = b64encode(arguments.encode("utf8"))
        finally:
            return response

    def _construct_from_pos(self, positions, lang):
        return u"".join(map(lambda i: unichr(lang[(i - 1) % len(lang)]), positions))

    def pos(self, text):
        try:
            positions = list(map(int, text.split()))
        except ValueError:
            try:
                positions = list(map(int, text.split(",")))
            except Exception:
                return None

        return u"\n".join(self._construct_from_pos(positions, lang) for lang in (RUS, ENG))

    def _gps_dd(self, coords):
        return tuple(map(lambda x: round(float(x[0]), 6), coords))

    def _gps_dmr(self, coords):
        result = []
        for lat in coords:
            d, m = map(float, lat[:2])
            result.append(round(d + m / 60 * (-1 if d < 0 else 1), 6))
        return tuple(result)

    def _gps_dmsr(self, coords):
        result = []
        for lat in coords:
            d, m, s = map(float, lat[:3])
            result.append(round(d + (m * 60 + s) / 3600 * (-1 if d < 0 else 1), 6))
        return tuple(result)

    def _split_gps(self, text):
        raw_coords = text.split(",")
        coords = [0, [[], []]]
        for i, lat in enumerate(raw_coords):
            lat = lat.split()
            count = len(lat)
            if count > coords[0]:
                coords[0] = count
            coords[1][i] = lat
        return coords

    def gps(self, text):
        try:
            coords = self._split_gps(text)
            if coords[0] == 1:
                return self._gps_dd(coords[1])
            if coords[0] == 2:
                return self._gps_dmr(coords[1])
            if coords[0] == 3:
                return self._gps_dmsr(coords[1])
        except Exception:
            pass

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

    def codes(self, _):
        answer, message = self._get_dzzzr_answer()
        if message:
            return message
        try:
            message = answer.find("strong", string=re_compile(u"Коды сложности")).parent
        except Exception:
            return u"Коды сложности не найдены"
        if message:
            message = unicode(message).split(u"Коды сложности")[1]
            sectors = re_split("<br/?>", message)[:-1]
            result = []
            for sector in filter(len, sectors):
                try:
                    sector_name, _, codes = sector.partition(u":")
                    _, __, codes = codes.partition(u":")
                    if not codes:
                        continue
                    codes = filter(lambda c: u"span" not in c[1], enumerate(codes.strip().split(u", "), start=1))
                    result.append(
                        u"%s (осталось %s): %s" % (
                            sector_name,
                            len(codes),
                            u", ".join(map(lambda t: u"%s (%s)" % (t[0], t[1]), codes))
                        ))
                except Exception:
                    pass
            return u"\n".join(result)
        return u"Нет ответа"

    def handle_command(self, text):
        command, _, arguments = text.partition(" ")
        if self.name in command:
            command = command[:command.find("@DzzzzR_bot")]
        if "@" in command:
            return None
        if command == "/set_dzzzr":
            try:
                return self.set_dzzzr(arguments)
            except Exception as e:
                return "Incorrect format (%s)" % e
        else:
            try:
                return getattr(self, command[1:], self.not_found)(arguments)
            except UnicodeEncodeError as e:
                return self.not_found(None)
            except Exception as e:
                logging.error(e)
                return None

    def handle(self, message):
        try:
            if message['text'][0] == '/':
                return self.handle_command(message['text'])
            else:
                return self.code(message)
        except Exception:
            return None

    def _send_code(self, code):
        if self.url == "":
            return code + u" - сначала надо войти в движок"
        try:
            answer = self.get_dzzzr(code=code)
        except Exception as e:
            return e.message
        if self.classic:
            message = answer.find(class_="sysmsg")
            return code + " - " + (message.get_text() if message and message.get_text() else u"нет ответа.")
        else:
            message = LITE_MESSAGE.search(str(answer))
            return code + u" - " + (message.group(1).decode("utf8") if message else u"нет ответа")

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

    def code(self, message):
        if self.enabled:
            if message['text'].count(",") == 1:
                try:
                    result = self.gps(message['text'])
                    if result:
                        return result
                except Exception:
                    pass

            codes = message['text'].split()
            if len(codes) < 1:
                return None
            if self.dr_code.match(codes[0]):
                result = filter(None, map(self._handle_code, codes))
                if len(result):
                    return u"\n".join(result)

        if u"привет" in message['text'].lower() and u"бот" in message['text'].lower():
            return u"Привет!"
