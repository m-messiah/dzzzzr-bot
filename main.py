# coding=utf-8
import logging
from random import choice

import webapp2
from webapp2_extras import json

from dozor import DozoR

__author__ = 'm_messiah'

SESSIONS = {}


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
        if 'message' not in update and 'edited_message' not in update:
            if 'inline_query' in update:
                self.response.headers['Content-Type'] = 'application/json'
                return self.response.write(json.encode({
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

        message = update.get('message', update.get('edited_message'))
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
                        'text': "id = %s" % message['contact'].get('user_id', "none"),
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
    app.run()  # noqa
