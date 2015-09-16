# coding=utf-8
from base64 import b64decode, b64encode
from os import environ
import urllib
from zlib import decompress, MAX_WBITS
from bs4 import BeautifulSoup
from flask import Flask, request, jsonify
from google.appengine.api import urlfetch
from requests import Session
from re import compile as re_compile

app = Flask(__name__)
app.config['DEBUG'] = True
dr_code = re_compile(ur"^[0-9]*[dDдД]?[0-9]*[rRрР][0-9]*$")

try:
    from bot_token import BOT_TOKEN
except ImportError:
    BOT_TOKEN = environ["TOKEN"]


SESSIONS = {}

URL = "https://api.telegram.org/bot%s/" % BOT_TOKEN
MyURL = "https://dzzzr-bot.appspot.com"


class DozoR(object):
    def __init__(self, chat_id):
        self.chat_id = chat_id
        self.url = ""
        self.prefix = ""
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
                'text': "Usage: \n"
                        "/set_dzzzr url captain pin login password [prefix]"
            }
        else:
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
                    'text': "Not authorized"
                }
            else:
                return {
                    'chat_id': self.chat_id,
                    'text': "Welcome %s" % login
                }

    def not_found(self, _):
        return {
            'chat_id': self.chat_id,
            'text': "Command not found. Try /help"
        }

    def start(self, _):
        return {'chat_id': self.chat_id, 'text': "I am awake!"}

    def about(self, _):
        return {
            'chat_id': self.chat_id,
            'text': "Hey!\n"
                    "My author is @m_messiah."
                    "You can find this nickname at:"
                    "\t+ Telegram"
                    "\t+ Twitter"
                    "\t+ Instagram"
                    "\t+ VK"
                    "\t+ GitHub (m-messiah)"
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

    def code(self, text, reply_id):
        def send(browser, url, code):
            if url == "":
                return code + u" - сначала надо войти в движок"
            answer = browser.post(url, data={'action': "entcod",
                                             'cod': code})
            if not answer:
                return code + u" - Нет ответа. Проверьте вручную."
            answer = BeautifulSoup(
                decompress(answer.content, 16 + MAX_WBITS)
                .decode("cp1251", "ignore"),
                'html.parser'
            )

            message = answer.find(class_="sysmsg")
            return code + " - " + (message.string if message and message.string
                                   else u"нет ответа.")

        response = {'chat_id': self.chat_id}
        if reply_id:
            response['reply_to_message_id'] = reply_id

        codes = text.split()
        result = []
        for code in codes:
            if dr_code.match(code):
                code = code.upper().translate({ord(u'Д'): u'D',
                                               ord(u'Р'): u'R'})
                if "D" not in code:
                    code = self.prefix + code
                result.append(send(self.browser, self.url, code))
        if len(result):
            response['text'] = u"\n".join(result).encode("utf8")
            return response
        else:
            if u" бот" in text[-5:]:
                response['text'] = u"хуебот".encode("utf8")
                return response

            if u"Привет" in text:
                response['text'] = u"Привет!".encode("utf8")
                return response
            return None


def error():
    return 'Hello World! I am DR bot (https://telegram.me/DzzzzR_bot)'


def send_reply(response):
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
        app.logger.debug("Request: %s", request)
        try:
            update = request.json
            message = update['message']
            sender = message['chat']
            text = message.get('text')
            if text:
                app.logger.debug("MESSAGE FROM\t%s",
                                 sender['username'] if 'username' in sender
                                 else sender['id'])
                if sender['id'] not in SESSIONS:
                    SESSIONS[sender['id']] = DozoR(sender['id'])

                response = SESSIONS[sender['id']].handle(text)
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

