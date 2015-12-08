# coding=utf-8
from base64 import b64decode, b64encode
from os import environ
from zlib import decompress, MAX_WBITS
from bs4 import BeautifulSoup
from flask import Flask, request, jsonify
from requests import Session
from re import compile as re_compile

app = Flask(__name__)
app.config['DEBUG'] = False
dr_code = re_compile(ur"^[0-9dDдДrRрР]+$")

try:
    from bot_token import BOT_TOKEN
except ImportError:
    BOT_TOKEN = environ["TOKEN"]

SESSIONS = {}
CREDENTIALS = {}

URL = "https://api.telegram.org/bot%s/" % BOT_TOKEN
MyURL = "https://dzzzr-bot.appspot.com"


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

    def help(self, _):
        return (
            u"Я могу принимать следующие команды:\n"
            u"  /help - эта справка\n"
            u"  /about - информация об авторе\n"
            u"  /base64 <text> - Base64 кодирование/раскодирование\n"
            u"  /start - команда заглушка, эмулирующая начало общения\n"
            u"  /stop - команда удаляющая сессию общения с ботом\n"
            u"\n  DozoR\n"
            u"  /set_dzzzr url captain pin login password [prefix] - "
            u"  установить урл и учетные данные для движка DozoR.\n"
            u"  Если все коды имеют префикс игры (например 27d),"
            u"то его можно указать здесь "
            u"и отправлять коды уже в сокращенном виде (12r3 = 27d12r3)\n"
            u"\n  /pause - приостанавливает отправку кодов\n"
            u"  /resume - возобновляет отправку кодов\n"
            u"\n  Сами коды могут пристуствовать в любом сообщении в чате\n"
            u"  как с русскими буквами, так и английскими,\n"
            u"  игнорируя регистр символов.\n"
            u"  (Главное, чтобы сообщение начиналось с кода)")

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

    def about(self, _):
        return (u"Привет!\n"
                u"Мой автор @m_messiah\n"
                u"Контакты: https://m-messiah.ru\n"
                u"\nА еще принимаются пожертвования:\n"
                u"  https://paypal.me/muzafarov\n"
                u"  http://yasobe.ru/na/m_messiah")

    def base64(self, arguments):
        response = None
        try:
            response = b64decode(arguments.encode("utf8"))
            assert len(response)
        except:
            response = b64encode(arguments.encode("utf8"))
        finally:
            return response

    def handle(self, text):
        if text[0] == '/':
            command, _, arguments = text.partition(" ")
            if self.name in command:
                command = command[:command.find("@DzzzzR_bot")]
            app.logger.debug("REQUEST\t%s\t%s\t'%s'",
                             self.chat_id,
                             command.encode("utf8"),
                             arguments.encode("utf8"))
            if command == "/set_dzzzr":
                # if str(sender['id']) == "3798371":
                try:
                    return self.set_dzzzr(arguments)
                except Exception as e:
                    return "Incorrect format (%s)" % e
            else:
                return getattr(self, command[1:], self.not_found)(arguments)
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


def error():
    return 'Hello World! I am DR bot (https://telegram.me/DzzzzR_bot)'


@app.route('/', methods=['POST', 'GET'])
def index():
    if request.method == 'GET':
        return error()
    else:
        if 'Content-Type' not in request.headers:
            return error()
        if request.headers['Content-Type'] != 'application/json':
            return error()
        try:
            update = request.json
            message = update['message']
            chat = message['chat']
            text = message.get('text')
            if text:
                app.logger.debug(message)
                if chat['id'] not in SESSIONS:
                    SESSIONS[chat['id']] = DozoR(chat['id'])

                response = SESSIONS[chat['id']].handle(text)
                if response:
                    return jsonify(
                        method="sendMessage",
                        chat_id=chat['id'],
                        text=response,
                        reply_to_message_id=message['message_id'],
                        disable_web_page_preview=True,
                    )

            return jsonify(result="OK", text="Accepted")
        except Exception as e:
            app.logger.warning(str(e))
            return jsonify(result="Fail", text=str(e))


@app.errorhandler(404)
def page_not_found(e):
    """Return a custom 404 error."""
    return 'Sorry, nothing at this URL.', 404
