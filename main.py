from os import environ
import urllib
from flask import Flask, request, jsonify, json
from google.appengine.api import urlfetch
from requests import Session
app = Flask(__name__)
app.config['DEBUG'] = False
app.browser = Session()
app.dzzzr_url = ""
app.code_prefix = ""


from commands import CMD

try:
    from bot_token import BOT_TOKEN, DR_LOGIN, DR_PASSWORD
except ImportError:
    BOT_TOKEN = environ["TOKEN"]
    DR_LOGIN = environ["DR_LOGIN"]
    DR_PASSWORD = environ["DR_PASSWORD"]

URL = "https://api.telegram.org/bot%s/" % BOT_TOKEN
MyURL = "https://dzzzr-bot.appspot.com"


def set_dzzzr(arguments, chat_id):
    try:
        arguments = arguments.split()
        if len(arguments) > 2:
            url, captain, password = arguments[:3]
        else:
            raise ValueError

        prefix = arguments[3] if len(arguments) > 3 else ""

    except ValueError:
        return {
            'chat_id': chat_id,
            'text': "Usage: /set_dzzzr url captain password [prefix]"
        }
    else:
        app.dzzzr_url = url
        app.code_prefix = prefix
        app.browser.headers.update({'referer': app.dzzzr_url})
        app.browser.auth = (captain, password)
        login_page = app.browser.post(
            app.dzzzr_url,
            data={'login': DR_LOGIN,
                  'password': DR_PASSWORD,
                  'action': "auth", 'notags': ''})
        if login_page.status_code != 200:
            return {
                'chat_id': chat_id,
                'text': "Not authorized"
            }
        else:
            return {
                'chat_id': chat_id,
                'text': "Welcome %s" % DR_LOGIN
            }


def error():
    return 'Hello World! I am DR bot (https://telegram.me/DzzzzR_bot)'


def not_found(_, message):
    return {
        'chat_id': message['chat']['id'],
        'text': "Command not found. Try /help"
    }


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

                if text[0] == '/':
                    command, _, arguments = text.partition(" ")
                    app.logger.debug("REQUEST\t%s\t%s\t'%s'",
                                     sender['id'],
                                     command.encode("utf8"),
                                     arguments.encode("utf8"))
                    if command == "/set_dzzzr":
                        if str(sender['id']) == "3798371":
                            response = set_dzzzr(arguments, sender['id'])
                        else:
                            response = {'chat_id': sender['id'],
                                        'text': "Where is my master?"}
                    else:
                        response = CMD.get(command, not_found)(arguments,
                                                               message)

                    send_reply(response)
                else:
                    response = CMD["#code"](None, message,
                                            app.browser,
                                            app.dzzzr_url,
                                            app.code_prefix)
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

