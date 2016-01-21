# coding=utf-8
from base64 import b64decode, b64encode
from re import compile as re_compile
from zlib import decompress, MAX_WBITS

import webapp2
from bs4 import BeautifulSoup
from requests import Session
from webapp2_extras import json

__author__ = 'm_messiah'
__url__ = "https://dzzzr-bot.appspot.com"

dr_code = re_compile(ur"^[0-9dDдДrRрР]+$")

SESSIONS = {}
CREDENTIALS = {}

RUS = (1072, 1073, 1074, 1075, 1076, 1077, 1105, 1078, 1079, 1080, 1081, 1082,
       1083, 1084, 1085, 1086, 1087, 1088, 1089, 1090, 1091, 1092, 1093, 1094,
       1095, 1096, 1097, 1098, 1099, 1100, 1101, 1102, 1103)

ENG = (97, 98, 99, 100, 101, 102, 103, 104, 105, 106, 107, 108, 109, 110, 111,
       112, 113, 114, 115, 116, 117, 118, 119, 120, 121, 122)


class DozoR(object):
    def __init__(self, chat_id):
        self.chat_id = chat_id
        self.url = ""
        self.prefix = ""
        self.credentials = ""
        self.enabled = True
        self.browser = Session()
        self.name = "@DzzzzR_bot"

    def set_dzzzr(self, arguments):
        try:
            arguments = arguments.split()
            if len(arguments) > 4:
                self.url, captain, pin, login, password = arguments[:5]
            else:
                raise ValueError

            self.prefix = arguments[5] if len(arguments) > 5 else ""

        except ValueError:
            return (u"Использование:\n"
                    u"/set_dzzzr url captain pin login password [prefix]")
        else:
            if "|".join((self.url, captain, login)) in CREDENTIALS:
                return (u"Бот уже используется этой командой. chat_id = %s\n"
                        u"Сначала остановите его. (/stop)\n"
                        % CREDENTIALS["|".join((self.url, captain, login))])
            self.browser.headers.update({'referer': self.url})
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
                self.enabled = True
                self.credentials = "|".join((self.url, captain, login))
                CREDENTIALS[self.credentials] = self.chat_id
                return u"Добро пожаловать, %s" % login

    def show_sessions(self, _):
        return u"Сейчас используют:\n" + "\n".join(CREDENTIALS.keys())

    def not_found(self, _):
        return u"Команда не найдена. Используйте /help"

    def version(self, _):
        return u"Версия: 2.1"

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
            u"/set_dzzzr url captain pin login password [prefix] - "
            u"  установить урл и учетные данные для движка DozoR.\n"
            u"Если все коды имеют префикс игры (например 27d),"
            u"то его можно указать здесь "
            u"и отправлять коды уже в сокращенном виде (12r3 = 27d12r3)\n"
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
        self.enabled = False
        del CREDENTIALS[self.credentials]
        del SESSIONS[self.chat_id]
        return u"До новых встреч!"

    def about(self, _):
        return (u"Привет!\n"
                u"Мой автор @m_messiah\n"
                u"Сайт: https://m-messiah.ru\n"
                u"\nА еще принимаются пожертвования:\n"
                u"https://paypal.me/muzafarov\n"
                u"http://yasobe.ru/na/m_messiah")

    def base64(self, arguments):
        response = None
        try:
            response = b64decode(arguments.encode("utf8"))
            assert len(response)
        except:
            response = b64encode(arguments.encode("utf8"))
        finally:
            return response

    def pos(self, text):
        positions = list(map(int, text.split()))

        return u"\n".join((
            u"".join(map(lambda i: unichr(RUS[(i - 1) % 33]), positions)),
            u"".join(map(lambda i: unichr(ENG[(i - 1) % 26]), positions))
        ))

    def gps(self, text):
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
                result.append(
                    round(d + (m * 60 + s) / 3600 * (-1 if d < 0 else 1), 6)
                )
            return tuple(result)
        return u"Неправильные координаты"

    def handle(self, text):
        if text[0] == '/':
            command, _, arguments = text.partition(" ")
            if self.name in command:
                command = command[:command.find("@DzzzzR_bot")]
            if command == "/set_dzzzr":
                # if str(sender['id']) == "3798371":
                try:
                    return self.set_dzzzr(arguments)
                except Exception as e:
                    return "Incorrect format (%s)" % e
            else:
                try:
                    return getattr(self, command[1:],
                                   self.not_found)(arguments)
                except UnicodeEncodeError:
                    return self.not_found(None)
        else:
            response = self.code(text)
            if response:
                return response

    def code(self, text):
        def send(browser, url, code):
            if url == "":
                return code + u" - сначала надо войти в движок"
            answer = browser.post(url, data={'action': "entcod",
                                             'cod': code})
            if not answer:
                return code + u" - Нет ответа. Проверьте вручную."
            try:
                content = decompress(answer.content, 16 + MAX_WBITS)
            except:
                content = answer.content
            answer = BeautifulSoup(
                content.decode("cp1251", "ignore"),
                'html.parser'
            )
            message = answer.find(class_="sysmsg")
            return code + " - " + (message.get_text()
                                   if message and message.get_text()
                                   else u"нет ответа.")

        if self.enabled:
            codes = text.split()
            result = []
            if dr_code.match(codes[0]):
                for code in codes:
                    if dr_code.match(code):
                        code = code.upper().translate({ord(u'Д'): u'D',
                                                       ord(u'Р'): u'R'})
                        if self.prefix and self.prefix not in code:
                            code = self.prefix + code
                    result.append(send(self.browser, self.url, code))
            if len(result):
                return u"\n".join(result)
            else:
                if u" бот" in text[-5:]:
                    return u"хуебот"

                if u"Привет" in text or u"привет" in text:
                    return u"Привет!"
                return None
        else:
            pass


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
        message = update['message']
        sender = message['chat']['id']
        text = message.get('text')
        if text:
            response = None
            if sender not in SESSIONS:
                SESSIONS[sender] = DozoR(sender)

            output = SESSIONS[sender].handle(text)
            if isinstance(output, tuple):
                response = {'method': "sendLocation",
                            'chat_id': sender,
                            'reply_to_message_id': message['message_id'],
                            'latitude': output[0],
                            'longitude': output[1]}
            elif output:
                response = {'method': "sendMessage",
                            'chat_id': sender,
                            'text': output,
                            'reply_to_message_id': message['message_id'],
                            'disable_web_page_preview': True}

            if response:
                self.response.headers['Content-Type'] = 'application/json'
                self.response.write(json.encode(response))
            else:
                self.show_error()


app = webapp2.WSGIApplication([('/', MainPage)])

if __name__ == '__main__':
    app.run()
