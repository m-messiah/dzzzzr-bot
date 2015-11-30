# coding=utf-8
from base64 import b64decode, b64encode
from os import environ
import urllib
from zlib import decompress, MAX_WBITS
from bs4 import BeautifulSoup
from flask import Flask, request, jsonify
try:
    from google.appengine.api import urlfetch
except ImportError:
    print "App configured for GAE"


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

    def set_dzzzr(self, arguments):
        try:
            arguments = arguments.split()
            if len(arguments) > 4:
                self.url, captain, pin, login, password = arguments[:5]
            else:
                raise ValueError

            self.prefix = arguments[5] if len(arguments) > 5 else ""

        except ValueError:
            return {
                'chat_id': self.chat_id,
                'text': u"Использование: \n"
                        u"/set_dzzzr url captain pin login password [prefix]"
            }
        else:
            if "|".join((self.url, captain, login)) in CREDENTIALS:
                return {
                    'chat_id': self.chat_id,
                    'text': u"Бот уже используется этой командой. "
                            u"chat_id = %s"
                            u"Сначала остановите его. (/stop)"
                            % CREDENTIALS["|".join((self.url, captain, login))]
                }
            self.browser.headers.update({'referer': self.url})
            self.browser.auth = (captain, pin)
            login_page = self.browser.post(
                self.url,
                data={'login': login,
                      'password': password,
                      'action': "auth", 'notags': ''})
            if login_page.status_code != 200:
                return {
                    'chat_id': self.chat_id,
                    'text': u"Авторизация не удалась"
                }
            else:
                self.enabled = True
                self.credentials = "|".join((self.url, captain, login))
                CREDENTIALS[self.credentials] = self.chat_id
                return {
                    'chat_id': self.chat_id,
                    'text': u"Добро пожаловать, %s" % login
                }

    def show_sessions(self, _):
        return {
            'chat_id': self.chat_id,
            'text': u"Сейчас используют:\n" + "\n".join(CREDENTIALS.keys())
        }

    def not_found(self, _):
        return {
            'chat_id': self.chat_id,
            'text': u"Команда не найдена. Используйте /help"
        }

    def help(self, _):
        return {
            'chat_id': self.chat_id,
            'text': u"Я могу принимать следующие команды:\n"
                    u"/help - эта справка\n"
                    u"/about - информация об авторе\n"
                    u"/base64 <text> - Base64 кодирование/раскодирование\n"
                    u"/start - команда заглушка, эмулирующая начало общения\n"
                    u"/stop - команда удаляющая сессию общения с ботом\n"
                    u"DozoR\n"
                    u"/set_dzzzr url captain pin login password [prefix] - "
                    u"установить урл и учетные данные для движка DozoR. "
                    u"Если все коды имеют префикс игры (например 27d), "
                    u"то его можно указать здесь и отправлять коды уже "
                    u"в сокращенном виде (12r3 = 27d12r3)\n"
                    u"/pause - приостанавливает отправку кодов\n"
                    u"/resume - возобновляет отправку кодов\n"
                    u"\nСами коды могут пристуствовать в любом сообщении "
                    u"в чате как с русскими буквами, так и английскими, "
                    u"игнорируя регистр символов."
        }

    def start(self, _):
        return {'chat_id': self.chat_id, 'text': u"Внимательно слушаю!"}

    def pause(self, _):
        self.enabled = False
        return {'chat_id': self.chat_id,
                'text': u"Ок, я больше не буду реагировать на сообщения мне "
                        u"(не считая команды). "
                        u"Не забудьте потом включить с помощью /resume"}

    def resume(self, _):
        self.enabled = True
        return {'chat_id': self.chat_id,
                'text': u"Я вернулся! Давайте ваши коды!"}

    def stop(self, _):
        self.enabled = False
        del CREDENTIALS[self.credentials]
        del SESSIONS[self.chat_id]

    def about(self, _):
        return {
            'chat_id': self.chat_id,
            'disable_web_page_preview': True,
            'text': u"Привет!\n"
                    u"Мой автор @m_messiah\n"
                    u"Контакты: https://m-messiah.ru\n"
                    u"\nА еще принимаются пожертвования:\n"
                    u"\t+ https://paypal.me/muzafarov\n"
                    u"\t+ http://yasobe.ru/na/messiah\n"
        }

    def base64(self, arguments):
        response = {'chat_id': self.chat_id}
        try:
            response['text'] = b64decode(arguments.encode("utf8"))
            assert len(response['text'])
        except:
            response['text'] = b64encode(arguments.encode("utf8"))
        finally:
            return response

    def handle(self, text, reply_id=None):
        if text[0] == '/':
            command, _, arguments = text.partition(" ")
            app.logger.debug("REQUEST\t%s\t%s\t'%s'",
                             self.chat_id,
                             command.encode("utf8"),
                             arguments.encode("utf8"))
            if command == "/set_dzzzr":
                #if str(sender['id']) == "3798371":
                try:
                    return self.set_dzzzr(arguments)
                except Exception as e:
                    return {'chat_id': self.chat_id,
                            'text': "Incorrect format (%s)" % e}
            else:
                return getattr(self, command[1:], self.not_found)(arguments)
        else:
            response = self.code(text, reply_id)
            if response:
                return response

    def code(self, text, reply_id=None):
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
            response = {'chat_id': self.chat_id}

            codes = text.split()
            result = []
            for code in codes:
                if dr_code.match(code):
                    code = code.upper().translate({ord(u'Д'): u'D',
                                                   ord(u'Р'): u'R'})
                    if self.prefix and self.prefix not in code:
                        code = self.prefix + code
                    result.append(send(self.browser, self.url, code))
            if len(result):
                response['text'] = u"\n".join(result)
                if reply_id:
                    response['reply_to_message_id'] = reply_id
                return response
            else:
                if u" бот" in text[-5:]:
                    response['text'] = u"хуебот"
                    return response

                if u"Привет" in text:
                    response['text'] = u"Привет!"
                    return response
                return None
        else:
            pass


def error():
    return 'Hello World! I am DR bot (https://telegram.me/DzzzzR_bot)'


def send_reply(response):
    response['text'] = response['text'].encode("utf8")
    app.logger.debug("SENT\t%s", response)
    payload = urllib.urlencode(response)
    if 'sticker' in response:
        urlfetch.fetch(url=URL + "sendSticker",
                       payload=payload,
                       method=urlfetch.POST)
    elif 'text' in response:
        if response['text'] == '':
            return
        o = urlfetch.fetch(URL + "sendMessage",
                           payload=payload,
                           method=urlfetch.POST)
        app.logger.debug(str(o.content))


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

                response = SESSIONS[chat['id']].handle(
                    text, reply_id=message['message_id'])
                if response:
                    send_reply(response)

            return jsonify(result="OK", text="Accepted")
        except Exception as e:
            app.logger.warning(str(e))
            return jsonify(result="Fail", text=str(e))


@app.errorhandler(404)
def page_not_found(e):
    """Return a custom 404 error."""
    return 'Sorry, nothing at this URL.', 404

