# coding=utf-8
import webapp2
from webapp2_extras import json

import messages
from message import Message

__author__ = 'm_messiah'

CREDENTIALS = {}
SESSIONS = {}


class MainPage(webapp2.RequestHandler):
    def get(self):
        return self._show_error()

    def _get_update(self):
        if 'Content-Type' not in self.request.headers:
            return {}
        if 'application/json' not in self.request.headers['Content-Type']:
            return {}
        try:
            return json.decode(self.request.body)
        except Exception:
            return {}

    def _answer(self, response):
        self.response.headers['Content-Type'] = 'application/json'
        self.response.write(json.encode(response))

    def _show_error(self):
        self._answer({'result': "Info", "name": messages.DEFAULT_ANSWER})

    def _inline_query(self, query):
        return self._answer({
            'method': 'answerInlineQuery',
            'inline_query_id': query['id'],
            'cache_time': 60,
            'results': json.encode([{
                'type': 'article',
                'id': "1",
                'title': "405",
                'message_text': messages.INLINE_TEXT,
                'description': messages.INLINE_DESCRIPTION,
            }])
        })

    def _get_message(self, update):
        if 'message' in update:
            return Message(update['message'])
        elif 'edited_message' in update:
            return Message(update['edited_message'])

    def post(self):
        update = self._get_update()
        if 'inline_query' in update:
            return self._inline_query(update['inline_query'])

        message = self._get_message(update)
        if message:
            return self._answer(message.handle() or {})

        return self._show_error()


app = webapp2.WSGIApplication([('/', MainPage)])

if __name__ == '__main__':  # pragma: no cover
    app.run()
